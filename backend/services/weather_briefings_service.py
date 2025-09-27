"""
Weather Briefings Database Service
Handles storage and retrieval of weather briefings in Supabase
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from models.dtos import WeatherBriefingResponse

logger = logging.getLogger(__name__)


class WeatherBriefingsService:
    """Service for weather briefings database operations"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    async def store_weather_briefing(self, briefing: WeatherBriefingResponse, user_id: Optional[str] = None) -> bool:
        """
        Store a weather briefing in the database
        
        Args:
            briefing: WeatherBriefingResponse to store
            user_id: Optional user ID for user-specific briefings
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare data for storage
            briefing_data = {
                'briefing_id': briefing.briefing_id,
                'user_id': user_id,
                'route_type': briefing.route_type,
                'airports': briefing.airports,
                'detail_level': briefing.detail_level,
                'executive_summary': briefing.executive_summary,
                'weather_data': self._serialize_weather_data(briefing.weather_data),
                'ml_predictions': self._serialize_ml_predictions(briefing.ml_predictions),
                'risk_assessment': self._serialize_risk_assessment(briefing.risk_assessment),
                'alternative_routes': self._serialize_alternative_routes(briefing.alternative_routes),
                'flight_monitoring_enabled': briefing.flight_monitoring_enabled,
                'monitoring_id': briefing.monitoring_id,
                'data_sources': briefing.data_sources,
                'generated_at': briefing.generated_at.isoformat(),
                'last_updated': briefing.last_updated.isoformat(),
                'valid_until': briefing.valid_until.isoformat(),
                'success': briefing.success,
                'message': briefing.message
            }
            
            # Insert into database
            response = self.supabase.table('weather_briefings').insert(briefing_data).execute()
            
            if response.data:
                logger.info(f"Weather briefing stored successfully: {briefing.briefing_id}")
                return True
            else:
                logger.error(f"Failed to store weather briefing: {briefing.briefing_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing weather briefing {briefing.briefing_id}: {e}")
            return False
    
    async def get_weather_briefing(self, briefing_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a weather briefing by ID
        
        Args:
            briefing_id: Briefing identifier
            user_id: Optional user ID for user-specific briefings
            
        Returns:
            Dict with briefing data if found, None otherwise
        """
        try:
            query = self.supabase.table('weather_briefings').select('*').eq('briefing_id', briefing_id)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            response = query.execute()
            
            if response.data and len(response.data) > 0:
                briefing_data = response.data[0]
                
                # Deserialize complex fields
                briefing_data['weather_data'] = self._deserialize_weather_data(briefing_data.get('weather_data'))
                briefing_data['ml_predictions'] = self._deserialize_ml_predictions(briefing_data.get('ml_predictions'))
                briefing_data['risk_assessment'] = self._deserialize_risk_assessment(briefing_data.get('risk_assessment'))
                briefing_data['alternative_routes'] = self._deserialize_alternative_routes(briefing_data.get('alternative_routes'))
                
                return briefing_data
            else:
                logger.warning(f"Weather briefing not found: {briefing_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving weather briefing {briefing_id}: {e}")
            return None
    
    async def get_user_briefings(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all weather briefings for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of briefing data
        """
        try:
            response = (self.supabase.table('weather_briefings')
                       .select('briefing_id, route_type, airports, generated_at, valid_until, success, message')
                       .eq('user_id', user_id)
                       .order('generated_at', desc=True)
                       .range(offset, offset + limit - 1)
                       .execute())
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error getting user briefings for {user_id}: {e}")
            return []
    
    async def cleanup_expired_briefings(self) -> int:
        """
        Remove expired weather briefings from database
        
        Returns:
            Number of briefings cleaned up
        """
        try:
            current_time = datetime.utcnow().isoformat()
            
            # Delete briefings that have expired
            response = (self.supabase.table('weather_briefings')
                       .delete()
                       .lt('valid_until', current_time)
                       .execute())
            
            count = len(response.data) if response.data else 0
            logger.info(f"Cleaned up {count} expired weather briefings")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired briefings: {e}")
            return 0
    
    def _serialize_weather_data(self, weather_data) -> Optional[str]:
        """Serialize weather data to JSON string"""
        if not weather_data:
            return None
        try:
            return json.dumps([data.dict() if hasattr(data, 'dict') else data for data in weather_data])
        except Exception:
            return None
    
    def _serialize_ml_predictions(self, ml_predictions) -> Optional[str]:
        """Serialize ML predictions to JSON string"""
        if not ml_predictions:
            return None
        try:
            serialized = {}
            for airport, predictions in ml_predictions.items():
                serialized[airport] = predictions.dict() if hasattr(predictions, 'dict') else predictions
            return json.dumps(serialized)
        except Exception:
            return None
    
    def _serialize_risk_assessment(self, risk_assessment) -> Optional[str]:
        """Serialize risk assessment to JSON string"""
        if not risk_assessment:
            return None
        try:
            return json.dumps(risk_assessment.dict() if hasattr(risk_assessment, 'dict') else risk_assessment)
        except Exception:
            return None
    
    def _serialize_alternative_routes(self, alternative_routes) -> Optional[str]:
        """Serialize alternative routes to JSON string"""
        if not alternative_routes:
            return None
        try:
            return json.dumps([route.dict() if hasattr(route, 'dict') else route for route in alternative_routes])
        except Exception:
            return None
    
    def _deserialize_weather_data(self, data_str) -> Optional[List]:
        """Deserialize weather data from JSON string"""
        if not data_str:
            return None
        try:
            return json.loads(data_str)
        except Exception:
            return None
    
    def _deserialize_ml_predictions(self, data_str) -> Optional[Dict]:
        """Deserialize ML predictions from JSON string"""
        if not data_str:
            return None
        try:
            return json.loads(data_str)
        except Exception:
            return None
    
    def _deserialize_risk_assessment(self, data_str) -> Optional[Dict]:
        """Deserialize risk assessment from JSON string"""
        if not data_str:
            return None
        try:
            return json.loads(data_str)
        except Exception:
            return None
    
    def _deserialize_alternative_routes(self, data_str) -> Optional[List]:
        """Deserialize alternative routes from JSON string"""
        if not data_str:
            return None
        try:
            return json.loads(data_str)
        except Exception:
            return None