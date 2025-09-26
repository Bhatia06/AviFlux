"""
Flight plan generation and management service
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from models.flight_plan import FlightPlan, Route, Summary, Risk, MapLayers, HazardInfo
from api.aviation_weather import AviationWeatherAPI
from services.route_service import RouteService

logger = logging.getLogger(__name__)


class FlightPlanService:
    """Service for flight plan generation and management"""
    
    def __init__(self, airport_db):
        """Initialize with airport database"""
        self.airport_db = airport_db
        self.route_service = RouteService(airport_db)
    
    async def generate_flight_plan(self, origin_icao: str, destination_icao: str, 
                                 departure_time: Optional[datetime] = None) -> FlightPlan:
        """
        Generate a complete flight plan
        
        Args:
            origin_icao: Origin airport ICAO code
            destination_icao: Destination airport ICAO code
            departure_time: Planned departure time (optional)
            
        Returns:
            Complete FlightPlan object
        """
        logger.info(f"Generating flight plan: {origin_icao} -> {destination_icao}")
        
        # Validate airports
        if not self.airport_db.get_coords(origin_icao):
            raise ValueError(f"Origin airport {origin_icao} not found")
        if not self.airport_db.get_coords(destination_icao):
            raise ValueError(f"Destination airport {destination_icao} not found")
        
        # Set default departure time if not provided
        if departure_time is None:
            departure_time = datetime.utcnow() + timedelta(hours=2)
        
        # Calculate route
        route_data = self.route_service.calculate_great_circle_route(
            origin_icao, destination_icao
        )
        
        # Get weather data
        weather_data = await self._get_weather_data([origin_icao, destination_icao], 
                                                  route_data['coordinates'])
        
        # Generate flight plan components
        plan_id = str(uuid.uuid4())
        generated_at = datetime.utcnow()
        
        route = Route(
            airports=[origin_icao, destination_icao],
            departure_time=departure_time,
            distance_nm=round(route_data['distance_nm'], 1),
            estimated_time_min=route_data['estimated_time_min']
        )
        
        summary = self._generate_summary(weather_data, origin_icao, destination_icao)
        risks = self._identify_risks(weather_data, route_data)
        map_layers = self._create_map_layers(route_data, [origin_icao, destination_icao], 
                                           weather_data)
        
        return FlightPlan(
            plan_id=plan_id,
            generated_at=generated_at,
            route=route,
            summary=summary,
            risks=risks,
            map_layers=map_layers
        )
    
    async def _get_weather_data(self, icao_codes: List[str], 
                              route_coordinates: List[tuple]) -> Dict:
        """Get comprehensive weather data for the flight"""
        try:
            async with AviationWeatherAPI() as weather_api:
                weather_data = await weather_api.get_route_weather(
                    route_coordinates, icao_codes
                )
            return weather_data
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            # Return empty weather data structure on error
            return {
                'airport_weather': {},
                'sigmets': [],
                'route_analysis': {
                    'risk_level': 'green',
                    'summary_text': ['Weather data unavailable'],
                    'active_sigmets': 0,
                    'airports_analyzed': 0
                }
            }
    
    def _generate_summary(self, weather_data: Dict, origin_icao: str, 
                         destination_icao: str) -> Summary:
        """Generate flight plan summary"""
        summary_text = []
        
        # Add weather summary from route analysis
        route_analysis = weather_data.get('route_analysis', {})
        summary_text.extend(route_analysis.get('summary_text', []))
        
        # Add additional analysis
        airport_weather = weather_data.get('airport_weather', {})
        
        # Check for wind information
        for icao in [origin_icao, destination_icao]:
            if icao in airport_weather:
                weather = airport_weather[icao]
                if weather.wind_speed and weather.wind_speed > 20:
                    summary_text.append(f"Strong winds at {icao}: {weather.wind_speed}kt")
        
        # Check for low visibility
        for icao in [origin_icao, destination_icao]:
            if icao in airport_weather:
                weather = airport_weather[icao]
                if weather.visibility_miles and weather.visibility_miles < 3:
                    summary_text.append(f"Reduced visibility at {icao}: {weather.visibility_miles} miles")
        
        # If no specific issues, add positive note
        if not summary_text:
            summary_text.append("No significant weather hazards identified")
        
        # Determine risk index
        risk_index = route_analysis.get('risk_level', 'green')
        
        return Summary(
            text=summary_text,
            risk_index=risk_index
        )
    
    def _identify_risks(self, weather_data: Dict, route_data: Dict) -> List[Risk]:
        """Identify and categorize flight risks"""
        risks = []
        
        # Analyze SIGMETs
        sigmets = weather_data.get('sigmets', [])
        for sigmet in sigmets:
            if sigmet.valid_to > datetime.utcnow():  # Active SIGMET
                # Determine severity based on hazard type
                severity = "medium"
                if sigmet.hazard_type.upper() in ["CONVECTIVE", "SEVERE_TURBULENCE"]:
                    severity = "high"
                elif sigmet.hazard_type.upper() in ["LIGHT_TURBULENCE", "MOUNTAIN_WAVE"]:
                    severity = "low"
                
                # Create simplified geometry (would be more complex in real implementation)
                risk = Risk(
                    type="weather",
                    subtype=sigmet.hazard_type.lower(),
                    location=sigmet.area,
                    severity=severity,
                    description=f"{sigmet.hazard_type} SIGMET active in {sigmet.area}",
                    geojson={
                        "type": "Polygon",
                        "coordinates": [[
                            [-90.0, 40.0], [-89.0, 40.0], 
                            [-89.0, 41.0], [-90.0, 41.0], 
                            [-90.0, 40.0]
                        ]]  # Simplified polygon
                    }
                )
                risks.append(risk)
        
        # Check for airport weather risks
        airport_weather = weather_data.get('airport_weather', {})
        for icao, weather in airport_weather.items():
            if weather.flight_category in ["IFR", "LIFR"]:
                risk = Risk(
                    type="weather",
                    subtype="low_visibility",
                    location=icao,
                    severity="high" if weather.flight_category == "LIFR" else "medium",
                    description=f"{weather.flight_category} conditions at {icao}",
                    geojson={
                        "type": "Point",
                        "coordinates": [[]]  # Would use actual airport coordinates
                    }
                )
                risks.append(risk)
        
        return risks
    
    def _create_map_layers(self, route_data: Dict, icao_codes: List[str], 
                          weather_data: Dict) -> MapLayers:
        """Create map layers for visualization"""
        
        # Create route geometry
        route_geometry = self.route_service.create_route_geometry(
            route_data['coordinates']
        )
        
        # Create airport information
        airport_weather = weather_data.get('airport_weather', {})
        airports = self.route_service.get_airport_info_list(icao_codes, airport_weather)
        
        # Create hazard information from risks
        hazards = []
        sigmets = weather_data.get('sigmets', [])
        for sigmet in sigmets[:3]:  # Limit to first 3 for performance
            if sigmet.valid_to > datetime.utcnow():
                hazard = HazardInfo(
                    type="sigmet",
                    severity="high" if "CONVECTIVE" in sigmet.hazard_type.upper() else "medium",
                    geojson={
                        "type": "Polygon",
                        "coordinates": [[
                            [-90.0, 40.0], [-89.0, 40.0], 
                            [-89.0, 41.0], [-90.0, 41.0], 
                            [-90.0, 40.0]
                        ]]  # Simplified - would parse actual SIGMET geometry
                    }
                )
                hazards.append(hazard)
        
        return MapLayers(
            route=route_geometry,
            airports=airports,
            hazards=hazards
        )
    
    def get_flight_plan_by_id(self, plan_id: str) -> Optional[FlightPlan]:
        """
        Retrieve a flight plan by ID (placeholder for database integration)
        
        Args:
            plan_id: Flight plan identifier
            
        Returns:
            FlightPlan object if found, None otherwise
        """
        # This would typically query a database
        # For now, return None as this is a placeholder
        logger.info(f"Flight plan retrieval requested for ID: {plan_id}")
        return None
    
    def save_flight_plan(self, flight_plan: FlightPlan) -> bool:
        """
        Save a flight plan (placeholder for database integration)
        
        Args:
            flight_plan: FlightPlan object to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        # This would typically save to a database
        # For now, just log the save operation
        logger.info(f"Flight plan save requested for ID: {flight_plan.plan_id}")
        return True
