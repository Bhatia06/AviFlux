"""
Route calculation and management service
"""

import logging
from typing import Dict, List, Tuple, Optional
from pyproj import Geod
from datetime import datetime
from models.flight_plan import RouteGeometry, AirportInfo

logger = logging.getLogger(__name__)


class RouteService:
    """Service for route calculations and management"""
    
    def __init__(self, airport_db):
        """Initialize with airport database"""
        self.airport_db = airport_db
        self.geod = Geod(ellps='WGS84')
    
    def calculate_great_circle_route(self, origin_icao: str, destination_icao: str, 
                                   num_points: int = 100) -> Dict:
        """
        Calculate great circle route between two airports
        
        Args:
            origin_icao: Origin airport ICAO code
            destination_icao: Destination airport ICAO code
            num_points: Number of intermediate points
            
        Returns:
            Dictionary with route information
        """
        logger.info(f"Calculating route from {origin_icao} to {destination_icao}")
        
        # Get airport coordinates
        origin_coords = self.airport_db.get_coords(origin_icao)
        destination_coords = self.airport_db.get_coords(destination_icao)
        
        if not origin_coords:
            raise ValueError(f"Origin airport {origin_icao} not found")
        if not destination_coords:
            raise ValueError(f"Destination airport {destination_icao} not found")
        
        lat1, lon1 = origin_coords
        lat2, lon2 = destination_coords
        
        # Calculate great circle path
        path_points = self.geod.npts(lon1, lat1, lon2, lat2, npts=num_points-2)
        
        # Format coordinates for route
        if path_points:
            path_coords = [(lat, lon) for lon, lat in path_points]
        else:
            path_coords = []
        
        # Include start and end points
        all_coords = [(lat1, lon1)] + path_coords + [(lat2, lon2)]
        
        # Calculate distance and time
        forward_azimuth, back_azimuth, distance_meters = self.geod.inv(lon1, lat1, lon2, lat2)
        distance_nm = distance_meters / 1852  # Convert to nautical miles
        
        # Estimate flight time (assuming 450 knots average speed)
        estimated_time_min = int((distance_nm / 450) * 60)
        
        return {
            'coordinates': all_coords,
            'distance_nm': distance_nm,
            'distance_km': distance_meters / 1000,
            'estimated_time_min': estimated_time_min,
            'total_points': len(all_coords)
        }
    
    def create_route_geometry(self, coordinates: List[Tuple[float, float]]) -> RouteGeometry:
        """
        Create route geometry for map display
        
        Args:
            coordinates: List of (latitude, longitude) tuples
            
        Returns:
            RouteGeometry object for map display
        """
        # Convert to [longitude, latitude] format for GeoJSON
        geojson_coords = [[lon, lat] for lat, lon in coordinates]
        
        return RouteGeometry(
            type="LineString",
            coordinates=geojson_coords
        )
    
    def calculate_multi_leg_route(self, airports: List[str], circular: bool = False,
                                  num_points_per_leg: int = 100) -> Dict:
        """
        Calculate a multi-leg (optionally circular) great-circle route.

        Args:
            airports: Ordered ICAO list: source -> intermediates -> destination
            circular: When true, append last leg destination->source
            num_points_per_leg: Points per leg including endpoints

        Returns:
            Dictionary with combined coordinates, distance and per-segment summaries
        """
        if len(airports) < 2:
            raise ValueError("At least two airports are required")

        legs: List[Tuple[str, str]] = []
        for i in range(len(airports) - 1):
            legs.append((airports[i], airports[i + 1]))
        if circular:
            legs.append((airports[-1], airports[0]))

        all_coords: List[Tuple[float, float]] = []
        total_distance_meters: float = 0.0
        segments: List[Dict] = []

        for index, (origin, dest) in enumerate(legs):
            segment = self.calculate_great_circle_route(origin, dest, num_points=num_points_per_leg)

            # Merge coordinates, avoid duplicating the start of subsequent legs
            if index == 0:
                all_coords.extend(segment['coordinates'])
            else:
                all_coords.extend(segment['coordinates'][1:])

            total_distance_meters += segment['distance_km'] * 1000.0

            segments.append({
                'origin': origin,
                'destination': dest,
                'distance_km': segment['distance_km'],
                'distance_nm': segment['distance_nm'],
                'points': segment['total_points']
            })

        first_3 = all_coords[:3] if len(all_coords) >= 3 else all_coords
        last_3 = all_coords[-3:] if len(all_coords) >= 3 else all_coords

        return {
            'coordinates': all_coords,
            'distance_km': total_distance_meters / 1000.0,
            'distance_nm': total_distance_meters / 1852.0,
            'total_points': len(all_coords),
            'segments': segments,
        }

    def get_airport_info_list(self, icao_codes: List[str], 
                            weather_data: Optional[Dict] = None) -> List[AirportInfo]:
        """
        Get airport information for map display
        
        Args:
            icao_codes: List of airport ICAO codes
            weather_data: Optional weather data for status
            
        Returns:
            List of AirportInfo objects
        """
        airport_info_list = []
        
        for icao in icao_codes:
            airport_data = self.airport_db.get_airport_info(icao)
            if airport_data:
                # Determine flight category from weather data
                status = "VFR"  # Default
                if weather_data and icao in weather_data:
                    flight_category = weather_data[icao].flight_category
                    if flight_category in ["IFR", "LIFR"]:
                        status = "IFR"
                    elif flight_category == "MVFR":
                        status = "MVFR"
                
                airport_info_list.append(AirportInfo(
                    icao=icao,
                    status=status,
                    coord=[airport_data['longitude'], airport_data['latitude']]
                ))
        
        return airport_info_list
    
    def validate_icao_codes(self, icao_codes: List[str]) -> Dict[str, bool]:
        """
        Validate a list of ICAO codes
        
        Args:
            icao_codes: List of ICAO codes to validate
            
        Returns:
            Dictionary mapping ICAO codes to validation status
        """
        validation_results = {}
        
        for icao in icao_codes:
            # Basic format validation
            if len(icao) != 4:
                validation_results[icao] = False
                continue
            
            # Check if airport exists in database
            coords = self.airport_db.get_coords(icao.upper())
            validation_results[icao] = coords is not None
        
        return validation_results
    
    def get_intermediate_waypoints(self, origin_icao: str, destination_icao: str, 
                                 max_waypoints: int = 5) -> List[str]:
        """
        Get suggested intermediate waypoints for long routes
        
        Args:
            origin_icao: Origin airport ICAO code
            destination_icao: Destination airport ICAO code
            max_waypoints: Maximum number of waypoints to suggest
            
        Returns:
            List of suggested waypoint ICAO codes
        """
        # This is a simplified implementation
        # In a real system, you would use airways, navigation aids, etc.
        
        route_data = self.calculate_great_circle_route(origin_icao, destination_icao)
        
        # For very long routes (>1000nm), suggest intermediate airports
        if route_data['distance_nm'] > 1000:
            # This would typically involve complex logic to find suitable airports
            # For now, we'll return an empty list
            logger.info(f"Long route detected ({route_data['distance_nm']:.0f}nm), "
                       f"intermediate waypoints recommended")
        
        return []  # Simplified - would implement waypoint logic here
