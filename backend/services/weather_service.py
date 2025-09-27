"""
Weather Service for integrating Ultimate Aviation Weather System
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uuid

from models.dtos import (
    WeatherBriefingRequest, WeatherBriefingResponse, WeatherData,
    MLPredictions, RiskAssessment, AlternativeRoute
)
from ai.ultimate_aviation_system import UltimateAviationWeatherSystem

logger = logging.getLogger(__name__)


class WeatherService:
    """Service class for weather briefing operations"""
    
    def __init__(self, supabase_client=None):
        self.supabase_client = supabase_client
        self._weather_system = None
        self._executor = ThreadPoolExecutor(max_workers=4)
    
    def _get_weather_system(self):
        """Get or initialize the weather system"""
        if self._weather_system is None:
            logger.info("Initializing Ultimate Aviation Weather System...")
            self._weather_system = UltimateAviationWeatherSystem()
            
            # Load airport database with Supabase connection
            if self.supabase_client:
                self._weather_system.load_airport_database(self.supabase_client)
            else:
                self._weather_system.load_airport_database()
            
            logger.info("Weather system initialized successfully")
        
        return self._weather_system
    
    async def generate_weather_briefing(self, request: WeatherBriefingRequest) -> WeatherBriefingResponse:
        """
        Generate a comprehensive weather briefing
        
        Args:
            request: Weather briefing request with route and options
            
        Returns:
            WeatherBriefingResponse with complete briefing data
        """
        try:
            logger.info(f"Generating weather briefing for route: {' -> '.join(request.airports)}")
            
            # Validate request
            if len(request.airports) < 2:
                raise ValueError("At least 2 airports required")
            if len(request.airports) > 10:
                raise ValueError("Maximum 10 airports allowed")
            
            # Validate ICAO codes
            for airport in request.airports:
                if len(airport) != 4:
                    raise ValueError(f"Invalid ICAO code: {airport}")
            
            # Generate briefing ID
            briefing_id = f"WB-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
            
            # Get weather system
            weather_system = self._get_weather_system()
            
            # Run weather briefing in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            briefing_result = await loop.run_in_executor(
                self._executor,
                self._run_weather_briefing,
                weather_system,
                request
            )
            
            # Parse the briefing result
            if not briefing_result:
                raise Exception("Failed to generate weather briefing")
            
            # Create response
            response = WeatherBriefingResponse(
                success=True,
                message="Weather briefing generated successfully",
                briefing_id=briefing_id,
                generated_at=datetime.utcnow(),
                route_type=request.route_type,
                airports=request.airports,
                detail_level=request.detail_level,
                executive_summary=self._extract_summary(briefing_result),
                weather_data=self._parse_weather_data(briefing_result, request.airports),
                ml_predictions=self._parse_ml_predictions(briefing_result) if request.include_ml_predictions else None,
                risk_assessment=self._parse_risk_assessment(briefing_result),
                alternative_routes=self._parse_alternative_routes(briefing_result) if request.include_alternative_routes else None,
                flight_monitoring_enabled=request.enable_flight_monitoring,
                monitoring_id=f"MON-{briefing_id}" if request.enable_flight_monitoring else None,
                data_sources=["Aviation Weather Center", "METAR", "TAF", "PIREP", "SIGMET"],
                last_updated=datetime.utcnow(),
                valid_until=datetime.utcnow().replace(hour=datetime.utcnow().hour + 6)  # Valid for 6 hours
            )
            
            logger.info(f"Weather briefing generated successfully: {briefing_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating weather briefing: {e}")
            return WeatherBriefingResponse(
                success=False,
                message=f"Failed to generate weather briefing: {str(e)}",
                briefing_id="",
                generated_at=datetime.utcnow(),
                route_type=request.route_type,
                airports=request.airports,
                detail_level=request.detail_level,
                executive_summary="",
                weather_data=[],
                ml_predictions=None,
                risk_assessment=RiskAssessment(
                    overall_risk_score=100.0,
                    risk_category="UNKNOWN",
                    flight_recommendation="DEFER - DATA UNAVAILABLE",
                    risk_factors=["Unable to retrieve weather data"],
                    weather_hazards=[]
                ),
                alternative_routes=None,
                flight_monitoring_enabled=False,
                monitoring_id=None,
                data_sources=[],
                last_updated=datetime.utcnow(),
                valid_until=datetime.utcnow()
            )
    
    def _run_weather_briefing(self, weather_system, request: WeatherBriefingRequest) -> Dict:
        """Run the weather briefing in a thread"""
        try:
            if request.route_type == "single" and len(request.airports) == 2:
                # Single route briefing
                return weather_system.generate_comprehensive_briefing(
                    departure=request.airports[0],
                    arrival=request.airports[1],
                    detail_level=request.detail_level
                )
            else:
                # Multi-airport briefing
                return weather_system.generate_multi_airport_briefing(
                    airports=request.airports,
                    detail_level=request.detail_level
                )
        except Exception as e:
            logger.error(f"Error in weather briefing thread: {e}")
            return {}
    
    def _extract_summary(self, briefing_result: Dict) -> str:
        """Extract executive summary from briefing result"""
        if not briefing_result:
            return "No weather data available"
        
        # Try different possible keys for summary
        summary_keys = ['executive_summary', 'briefing', 'summary', 'content']
        for key in summary_keys:
            if key in briefing_result and briefing_result[key]:
                return str(briefing_result[key])
        
        return "Weather briefing generated - see detailed data for complete information"
    
    def _parse_weather_data(self, briefing_result: Dict, airports: List[str]) -> List[WeatherData]:
        """Parse weather data from briefing result"""
        weather_data = []
        
        for airport in airports:
            # Extract weather data for each airport
            airport_weather = WeatherData(
                airport_code=airport,
                current_conditions=briefing_result.get(f"{airport}_current", {}),
                forecast=briefing_result.get(f"{airport}_forecast"),
                metar=briefing_result.get(f"{airport}_metar"),
                taf=briefing_result.get(f"{airport}_taf"),
                pireps=briefing_result.get(f"{airport}_pireps"),
                sigmets=briefing_result.get(f"{airport}_sigmets")
            )
            weather_data.append(airport_weather)
        
        return weather_data
    
    def _parse_ml_predictions(self, briefing_result: Dict) -> Optional[Dict[str, MLPredictions]]:
        """Parse ML predictions from briefing result"""
        predictions: Dict[str, MLPredictions] = {}
        
        ml_data = briefing_result.get('ml_predictions', {})
        if ml_data:
            for airport, pred_data in ml_data.items():
                predictions[airport] = MLPredictions(
                    temperature=pred_data.get('temperature'),
                    wind_speed=pred_data.get('wind_speed'),
                    wind_direction=pred_data.get('wind_direction'),
                    pressure=pred_data.get('pressure'),
                    turbulence_level=pred_data.get('turbulence_level'),
                    icing_probability=pred_data.get('icing_probability'),
                    weather_category=pred_data.get('weather_category'),
                    confidence_score=pred_data.get('confidence_score')
                )
        
        return predictions if predictions else None
    
    def _parse_risk_assessment(self, briefing_result: Dict) -> RiskAssessment:
        """Parse risk assessment from briefing result"""
        risk_data = briefing_result.get('risk_assessment', {})
        
        return RiskAssessment(
            overall_risk_score=risk_data.get('risk_score', 50.0),
            risk_category=risk_data.get('risk_category', 'MODERATE'),
            flight_recommendation=risk_data.get('recommendation', 'EVALUATE'),
            risk_factors=risk_data.get('risk_factors', []),
            weather_hazards=risk_data.get('hazards', [])
        )
    
    def _parse_alternative_routes(self, briefing_result: Dict) -> Optional[List[AlternativeRoute]]:
        """Parse alternative routes from briefing result"""
        alternatives: List[AlternativeRoute] = []
        alt_data = briefing_result.get('alternative_routes', [])
        
        for alt in alt_data:
            alternatives.append(AlternativeRoute(
                route_airports=alt.get('airports', []),
                reason=alt.get('reason', ''),
                estimated_additional_time=alt.get('additional_time'),
                risk_reduction=alt.get('risk_reduction')
            ))
        
        return alternatives if alternatives else None


# Global weather service instance
weather_service = None

def get_weather_service(supabase_client=None):
    """Get or create global weather service instance"""
    global weather_service
    if weather_service is None:
        weather_service = WeatherService(supabase_client)
    return weather_service