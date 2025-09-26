"""
Aviation Weather API integration with aviationweather.gov
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WeatherData:
    """Weather data structure"""
    station_id: str
    observation_time: datetime
    visibility_miles: Optional[float]
    wind_direction: Optional[int]
    wind_speed: Optional[int]
    temperature_celsius: Optional[float]
    dewpoint_celsius: Optional[float]
    altimeter_setting: Optional[float]
    flight_category: Optional[str]  # VFR, MVFR, IFR, LIFR
    raw_text: str


@dataclass
class SigmetData:
    """SIGMET data structure"""
    hazard_type: str
    severity: str
    valid_from: datetime
    valid_to: datetime
    area: str
    raw_text: str


class AviationWeatherAPI:
    """
    Integration with Aviation Weather Center (aviationweather.gov) APIs
    """
    
    BASE_URL = "https://aviationweather.gov/adds/dataserver_current/httpparam"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_metar(self, icao_codes: List[str]) -> Dict[str, WeatherData]:
        """
        Get METAR weather reports for specified airports
        
        Args:
            icao_codes: List of 4-letter ICAO airport codes
            
        Returns:
            Dictionary mapping ICAO codes to WeatherData objects
        """
        if not self.session:
            raise RuntimeError("Must use within async context manager")
        
        # Prepare parameters for METAR request
        params = {
            'dataSource': 'metars',
            'requestType': 'retrieve',
            'format': 'xml',
            'stationString': ','.join(icao_codes),
            'hoursBeforeNow': '2'  # Get reports from last 2 hours
        }
        
        try:
            async with self.session.get(self.BASE_URL, params=params) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    return self._parse_metar_xml(xml_content)
                else:
                    logger.error(f"Failed to fetch METAR data: HTTP {response.status}")
                    return {}
        
        except Exception as e:
            logger.error(f"Error fetching METAR data: {e}")
            return {}
    
    def _parse_metar_xml(self, xml_content: str) -> Dict[str, WeatherData]:
        """Parse METAR XML response"""
        weather_data = {}
        
        try:
            root = ET.fromstring(xml_content)
            
            for metar in root.findall('.//METAR'):
                station_id = self._get_text(metar, 'station_id')
                if not station_id:
                    continue
                
                observation_time_str = self._get_text(metar, 'observation_time')
                observation_time = self._parse_datetime(observation_time_str) if observation_time_str else datetime.utcnow()
                
                weather_data[station_id] = WeatherData(
                    station_id=station_id,
                    observation_time=observation_time,
                    visibility_miles=self._get_float(metar, 'visibility_statute_mi'),
                    wind_direction=self._get_int(metar, 'wind_dir_degrees'),
                    wind_speed=self._get_int(metar, 'wind_speed_kt'),
                    temperature_celsius=self._get_float(metar, 'temp_c'),
                    dewpoint_celsius=self._get_float(metar, 'dewpoint_c'),
                    altimeter_setting=self._get_float(metar, 'altim_in_hg'),
                    flight_category=self._get_text(metar, 'flight_category'),
                    raw_text=self._get_text(metar, 'raw_text', '')
                )
        
        except ET.ParseError as e:
            logger.error(f"Error parsing METAR XML: {e}")
        
        return weather_data
    
    async def get_sigmets(self, region: str = "US") -> List[SigmetData]:
        """
        Get SIGMET reports for specified region
        
        Args:
            region: Region code (default: "US")
            
        Returns:
            List of SigmetData objects
        """
        if not self.session:
            raise RuntimeError("Must use within async context manager")
        
        params = {
            'dataSource': 'airsigmets',
            'requestType': 'retrieve',
            'format': 'xml',
            'hoursBeforeNow': '4'  # Get SIGMETs from last 4 hours
        }
        
        try:
            async with self.session.get(self.BASE_URL, params=params) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    return self._parse_sigmet_xml(xml_content)
                else:
                    logger.error(f"Failed to fetch SIGMET data: HTTP {response.status}")
                    return []
        
        except Exception as e:
            logger.error(f"Error fetching SIGMET data: {e}")
            return []
    
    def _parse_sigmet_xml(self, xml_content: str) -> List[SigmetData]:
        """Parse SIGMET XML response"""
        sigmets = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for sigmet in root.findall('.//AIRSIGMET'):
                hazard_type = self._get_text(sigmet, 'hazard')
                if not hazard_type:
                    continue
                
                valid_from_str = self._get_text(sigmet, 'valid_time_from')
                valid_to_str = self._get_text(sigmet, 'valid_time_to')
                
                valid_from = self._parse_datetime(valid_from_str) if valid_from_str else datetime.utcnow()
                valid_to = self._parse_datetime(valid_to_str) if valid_to_str else datetime.utcnow() + timedelta(hours=6)
                
                sigmets.append(SigmetData(
                    hazard_type=hazard_type,
                    severity=self._get_text(sigmet, 'severity', 'MODERATE'),
                    valid_from=valid_from,
                    valid_to=valid_to,
                    area=self._get_text(sigmet, 'area', ''),
                    raw_text=self._get_text(sigmet, 'raw_text', '')
                ))
        
        except ET.ParseError as e:
            logger.error(f"Error parsing SIGMET XML: {e}")
        
        return sigmets
    
    async def get_route_weather(self, route_points: List[Tuple[float, float]], icao_codes: List[str]) -> Dict:
        """
        Get comprehensive weather data for a flight route
        
        Args:
            route_points: List of (latitude, longitude) tuples along the route
            icao_codes: List of airport ICAO codes
            
        Returns:
            Dictionary containing weather analysis for the route
        """
        # Get METAR data for airports
        metar_data = await self.get_metar(icao_codes)
        
        # Get SIGMET data
        sigmet_data = await self.get_sigmets()
        
        # Analyze route weather
        route_analysis = self._analyze_route_weather(route_points, metar_data, sigmet_data)
        
        return {
            'airport_weather': metar_data,
            'sigmets': sigmet_data,
            'route_analysis': route_analysis,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _analyze_route_weather(self, route_points: List[Tuple[float, float]], 
                              metar_data: Dict[str, WeatherData], 
                              sigmet_data: List[SigmetData]) -> Dict:
        """Analyze weather conditions along the flight route"""
        
        # Determine overall flight conditions
        flight_categories = [data.flight_category for data in metar_data.values() if data.flight_category]
        
        risk_level = "green"
        if any(cat in ["IFR", "LIFR"] for cat in flight_categories):
            risk_level = "red"
        elif any(cat == "MVFR" for cat in flight_categories):
            risk_level = "amber"
        
        # Check for active SIGMETs
        active_sigmets = [s for s in sigmet_data if s.valid_to > datetime.utcnow()]
        if active_sigmets:
            risk_level = "amber" if risk_level == "green" else "red"
        
        summary_text = []
        
        # Add airport weather summaries
        for icao, data in metar_data.items():
            if data.flight_category:
                summary_text.append(f"Weather at {icao} is {data.flight_category}.")
        
        # Add SIGMET summaries
        for sigmet in active_sigmets[:3]:  # Limit to first 3
            summary_text.append(f"{sigmet.hazard_type} SIGMET active in {sigmet.area}.")
        
        return {
            'risk_level': risk_level,
            'summary_text': summary_text,
            'active_sigmets': len(active_sigmets),
            'airports_analyzed': len(metar_data)
        }
    
    @staticmethod
    def _get_text(element: ET.Element, tag: str, default: str = None) -> Optional[str]:
        """Safely get text content from XML element"""
        child = element.find(tag)
        return child.text if child is not None else default
    
    @staticmethod
    def _get_float(element: ET.Element, tag: str) -> Optional[float]:
        """Safely get float value from XML element"""
        text = AviationWeatherAPI._get_text(element, tag)
        try:
            return float(text) if text else None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _get_int(element: ET.Element, tag: str) -> Optional[int]:
        """Safely get integer value from XML element"""
        text = AviationWeatherAPI._get_text(element, tag)
        try:
            return int(float(text)) if text else None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _parse_datetime(datetime_str: str) -> Optional[datetime]:
        """Parse ISO datetime string"""
        try:
            # Handle timezone-aware datetime strings
            if datetime_str.endswith('Z'):
                datetime_str = datetime_str[:-1] + '+00:00'
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None


# Convenience function for synchronous usage
def get_weather_sync(icao_codes: List[str]) -> Dict[str, WeatherData]:
    """
    Synchronous wrapper for getting METAR data
    
    Args:
        icao_codes: List of 4-letter ICAO airport codes
        
    Returns:
        Dictionary mapping ICAO codes to WeatherData objects
    """
    async def _get_weather():
        async with AviationWeatherAPI() as api:
            return await api.get_metar(icao_codes)
    
    return asyncio.run(_get_weather())
