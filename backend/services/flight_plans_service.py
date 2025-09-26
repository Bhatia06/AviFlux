"""
Flight Plans Database Service
Handles CRUD operations for flight plans stored in Supabase
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

from supabase import Client
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class FlightPlanData(BaseModel):
    """Pydantic model for flight plan data"""
    id: Optional[str] = None
    user_id: Optional[str] = None
    generated_at: datetime
    route_details: Dict[str, Any]
    weather_summary: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    map_layers: Dict[str, Any]
    chart_data: Dict[str, Any]
    created_at: Optional[datetime] = None


class FlightPlanResponse(BaseModel):
    """Response model for flight plan operations"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class FlightPlansService:
    """Service class for flight plans database operations"""
    
    def __init__(self, supabase_client: Client):
        """Initialize with Supabase client"""
        self.supabase = supabase_client
        self.table_name = 'flight_plans'
    
    async def create_flight_plan(
        self, 
        route_details: Dict[str, Any],
        weather_summary: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        map_layers: Dict[str, Any],
        chart_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> FlightPlanResponse:
        """
        Create a new flight plan in the database
        
        Args:
            route_details: JSONB data for route information
            weather_summary: JSONB data for weather analysis
            risk_analysis: JSONB data for risk assessment
            map_layers: JSONB data for map visualization
            chart_data: JSONB data for charts and graphs
            user_id: Optional user identifier
            
        Returns:
            FlightPlanResponse with operation result
        """
        try:
            # Generate unique ID and timestamp
            plan_id = str(uuid.uuid4())
            generated_at = datetime.utcnow()
            
            # Prepare data for insertion
            flight_plan_data = {
                'id': plan_id,
                'user_id': user_id,
                'generated_at': generated_at.isoformat(),
                'route_details': route_details,
                'weather_summary': weather_summary,
                'risk_analysis': risk_analysis,
                'map_layers': map_layers,
                'chart_data': chart_data
            }
            
            # Insert into Supabase
            result = self.supabase.table(self.table_name).insert(flight_plan_data).execute()
            
            if result.data:
                logger.info(f"Flight plan created successfully: {plan_id}")
                return FlightPlanResponse(
                    success=True,
                    message="Flight plan created successfully",
                    data=result.data[0]
                )
            else:
                logger.error("Failed to create flight plan - no data returned")
                return FlightPlanResponse(
                    success=False,
                    message="Failed to create flight plan",
                    error="No data returned from database"
                )
                
        except Exception as e:
            logger.error(f"Error creating flight plan: {e}")
            return FlightPlanResponse(
                success=False,
                message="Error creating flight plan",
                error=str(e)
            )
    
    async def get_flight_plan(self, plan_id: str) -> FlightPlanResponse:
        """
        Retrieve a specific flight plan by ID
        
        Args:
            plan_id: Unique flight plan identifier
            
        Returns:
            FlightPlanResponse with flight plan data
        """
        try:
            result = self.supabase.table(self.table_name).select('*').eq('id', plan_id).execute()
            
            if result.data:
                logger.info(f"Flight plan retrieved: {plan_id}")
                return FlightPlanResponse(
                    success=True,
                    message="Flight plan retrieved successfully",
                    data=result.data[0]
                )
            else:
                logger.warning(f"Flight plan not found: {plan_id}")
                return FlightPlanResponse(
                    success=False,
                    message="Flight plan not found",
                    error=f"No flight plan found with ID: {plan_id}"
                )
                
        except Exception as e:
            logger.error(f"Error retrieving flight plan {plan_id}: {e}")
            return FlightPlanResponse(
                success=False,
                message="Error retrieving flight plan",
                error=str(e)
            )
    
    async def get_user_flight_plans(
        self, 
        user_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> FlightPlanResponse:
        """
        Retrieve flight plans for a specific user
        
        Args:
            user_id: User identifier
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            FlightPlanResponse with list of flight plans
        """
        try:
            query = self.supabase.table(self.table_name).select('*')
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
            
            logger.info(f"Retrieved {len(result.data)} flight plans for user: {user_id}")
            return FlightPlanResponse(
                success=True,
                message=f"Retrieved {len(result.data)} flight plans",
                data={
                    'flight_plans': result.data,
                    'count': len(result.data),
                    'limit': limit,
                    'offset': offset
                }
            )
            
        except Exception as e:
            logger.error(f"Error retrieving user flight plans: {e}")
            return FlightPlanResponse(
                success=False,
                message="Error retrieving flight plans",
                error=str(e)
            )
    
    async def get_all_flight_plans(
        self, 
        limit: int = 50,
        offset: int = 0
    ) -> FlightPlanResponse:
        """
        Retrieve all flight plans (admin function)
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            FlightPlanResponse with list of flight plans
        """
        try:
            result = self.supabase.table(self.table_name).select('*').order('created_at', desc=True).range(offset, offset + limit - 1).execute()
            
            logger.info(f"Retrieved {len(result.data)} flight plans")
            return FlightPlanResponse(
                success=True,
                message=f"Retrieved {len(result.data)} flight plans",
                data={
                    'flight_plans': result.data,
                    'count': len(result.data),
                    'limit': limit,
                    'offset': offset
                }
            )
            
        except Exception as e:
            logger.error(f"Error retrieving all flight plans: {e}")
            return FlightPlanResponse(
                success=False,
                message="Error retrieving flight plans",
                error=str(e)
            )
    
    async def update_flight_plan(
        self, 
        plan_id: str, 
        updates: Dict[str, Any]
    ) -> FlightPlanResponse:
        """
        Update an existing flight plan
        
        Args:
            plan_id: Unique flight plan identifier
            updates: Dictionary of fields to update
            
        Returns:
            FlightPlanResponse with operation result
        """
        try:
            # Filter out None values and ensure valid fields
            valid_fields = {
                'user_id', 'route_details', 'weather_summary', 
                'risk_analysis', 'map_layers', 'chart_data'
            }
            
            filtered_updates = {
                k: v for k, v in updates.items() 
                if k in valid_fields and v is not None
            }
            
            if not filtered_updates:
                return FlightPlanResponse(
                    success=False,
                    message="No valid updates provided",
                    error="No valid fields to update"
                )
            
            result = self.supabase.table(self.table_name).update(filtered_updates).eq('id', plan_id).execute()
            
            if result.data:
                logger.info(f"Flight plan updated: {plan_id}")
                return FlightPlanResponse(
                    success=True,
                    message="Flight plan updated successfully",
                    data=result.data[0]
                )
            else:
                logger.warning(f"Flight plan not found for update: {plan_id}")
                return FlightPlanResponse(
                    success=False,
                    message="Flight plan not found",
                    error=f"No flight plan found with ID: {plan_id}"
                )
                
        except Exception as e:
            logger.error(f"Error updating flight plan {plan_id}: {e}")
            return FlightPlanResponse(
                success=False,
                message="Error updating flight plan",
                error=str(e)
            )
    
    async def delete_flight_plan(self, plan_id: str) -> FlightPlanResponse:
        """
        Delete a flight plan
        
        Args:
            plan_id: Unique flight plan identifier
            
        Returns:
            FlightPlanResponse with operation result
        """
        try:
            result = self.supabase.table(self.table_name).delete().eq('id', plan_id).execute()
            
            if result.data:
                logger.info(f"Flight plan deleted: {plan_id}")
                return FlightPlanResponse(
                    success=True,
                    message="Flight plan deleted successfully",
                    data={'deleted_id': plan_id}
                )
            else:
                logger.warning(f"Flight plan not found for deletion: {plan_id}")
                return FlightPlanResponse(
                    success=False,
                    message="Flight plan not found",
                    error=f"No flight plan found with ID: {plan_id}"
                )
                
        except Exception as e:
            logger.error(f"Error deleting flight plan {plan_id}: {e}")
            return FlightPlanResponse(
                success=False,
                message="Error deleting flight plan",
                error=str(e)
            )
    
    async def search_flight_plans(
        self, 
        search_criteria: Dict[str, Any],
        limit: int = 50,
        offset: int = 0
    ) -> FlightPlanResponse:
        """
        Search flight plans based on criteria
        
        Args:
            search_criteria: Dictionary with search parameters
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            FlightPlanResponse with matching flight plans
        """
        try:
            query = self.supabase.table(self.table_name).select('*')
            
            # Apply search filters
            if 'user_id' in search_criteria:
                query = query.eq('user_id', search_criteria['user_id'])
            
            if 'date_from' in search_criteria:
                query = query.gte('created_at', search_criteria['date_from'])
            
            if 'date_to' in search_criteria:
                query = query.lte('created_at', search_criteria['date_to'])
            
            # Execute query
            result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
            
            logger.info(f"Search returned {len(result.data)} flight plans")
            return FlightPlanResponse(
                success=True,
                message=f"Found {len(result.data)} matching flight plans",
                data={
                    'flight_plans': result.data,
                    'count': len(result.data),
                    'search_criteria': search_criteria,
                    'limit': limit,
                    'offset': offset
                }
            )
            
        except Exception as e:
            logger.error(f"Error searching flight plans: {e}")
            return FlightPlanResponse(
                success=False,
                message="Error searching flight plans",
                error=str(e)
            )
    
    def format_for_frontend(self, flight_plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format flight plan data for frontend consumption
        
        Args:
            flight_plan_data: Raw flight plan data from database
            
        Returns:
            Formatted data optimized for frontend
        """
        try:
            return {
                'id': flight_plan_data.get('id'),
                'user_id': flight_plan_data.get('user_id'),
                'generated_at': flight_plan_data.get('generated_at'),
                'created_at': flight_plan_data.get('created_at'),
                
                # Route information
                'route': flight_plan_data.get('route_details', {}),
                
                # Weather data
                'weather': flight_plan_data.get('weather_summary', {}),
                
                # Risk information
                'risks': flight_plan_data.get('risk_analysis', {}),
                
                # Map data for visualization
                'map_data': flight_plan_data.get('map_layers', {}),
                
                # Charts and analytics
                'charts': flight_plan_data.get('chart_data', {}),
                
                # Summary for quick display
                'summary': {
                    'origin': flight_plan_data.get('route_details', {}).get('origin', ''),
                    'destination': flight_plan_data.get('route_details', {}).get('destination', ''),
                    'distance': flight_plan_data.get('route_details', {}).get('distance', 0),
                    'risk_level': flight_plan_data.get('risk_analysis', {}).get('overall_risk', 'unknown')
                }
            }
            
        except Exception as e:
            logger.error(f"Error formatting flight plan data: {e}")
            return flight_plan_data  # Return original data if formatting fails