"""
Data Transfer Objects (DTOs) for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Tuple, Dict
from datetime import datetime
from .flight_plan import FlightPlan


class FlightPlanRequest(BaseModel):
    """Request model for creating a flight plan"""
    origin_icao: str = Field(..., min_length=4, max_length=4, description="Origin airport ICAO code")
    destination_icao: str = Field(..., min_length=4, max_length=4, description="Destination airport ICAO code")
    departure_time: Optional[datetime] = Field(None, description="Planned departure time (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin_icao": "KJFK",
                "destination_icao": "KSFO",
                "departure_time": "2025-09-25T12:00:00Z"
            }
        }


class FlightPlanResponse(BaseModel):
    """Response model for flight plan operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[FlightPlan] = Field(None, description="Flight plan data if successful")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Flight plan generated successfully",
                "data": {
                    "plan_id": "UUID-12345",
                    "generated_at": "2025-09-25T09:00:00Z"
                },
                "error": None
            }
        }


# Multi-leg route DTOs
class MultiLegRouteRequest(BaseModel):
    """Request for multi-leg route summary and optional circular path"""
    icao_codes: List[str] = Field(..., min_length=2, description="Ordered ICAO list: source -> intermediates -> destination")
    request_date: Optional[datetime] = Field(None, description="Request timestamp (optional)")
    circular: bool = Field(False, description="If true, end leg returns to the source airport")

    class Config:
        json_schema_extra = {
            "example": {
                "icao_codes": ["KJFK", "KLAX", "EGLL", "EDDF", "RJTT"],
                "request_date": "2025-09-26T12:00:00Z",
                "circular": False
            }
        }


class SimpleMultiLegRequest(BaseModel):
    """Simplified request for just ICAO codes"""
    icao_codes: List[str] = Field(..., min_length=2, description="Ordered ICAO list")
    
    class Config:
        json_schema_extra = {
            "example": {
                "icao_codes": ["KJFK", "KLAX", "EGLL", "EDDF", "RJTT"]
            }
        }


# Flight Plans Database DTOs
class CreateFlightPlanRequest(BaseModel):
    """Request to create a flight plan in the database"""
    route_details: Dict = Field(..., description="JSONB route information")
    weather_summary: Dict = Field(..., description="JSONB weather analysis")
    risk_analysis: Dict = Field(..., description="JSONB risk assessment")
    map_layers: Dict = Field(..., description="JSONB map visualization data")
    chart_data: Dict = Field(..., description="JSONB charts and graphs data")
    user_id: Optional[str] = Field(None, description="User identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "route_details": {
                    "origin": "KJFK",
                    "destination": "KLAX",
                    "distance_nm": 2144.5,
                    "estimated_time_min": 360
                },
                "weather_summary": {
                    "summary_text": ["Clear skies", "Light winds"],
                    "risk_index": "green"
                },
                "risk_analysis": {
                    "risks": [],
                    "overall_risk": "low"
                },
                "map_layers": {
                    "route_coordinates": [[-73.7781, 40.6413], [-118.4081, 33.9425]]
                },
                "chart_data": {
                    "generated_at": "2025-09-26T12:00:00Z"
                },
                "user_id": "user-123"
            }
        }


class FlightPlanSearchRequest(BaseModel):
    """Request to search flight plans"""
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    date_from: Optional[datetime] = Field(None, description="Search from date")
    date_to: Optional[datetime] = Field(None, description="Search to date")
    limit: int = Field(50, description="Maximum results to return")
    offset: int = Field(0, description="Number of records to skip")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "date_from": "2025-09-01T00:00:00Z",
                "date_to": "2025-09-30T23:59:59Z",
                "limit": 20,
                "offset": 0
            }
        }


class RouteSegmentSummary(BaseModel):
    """Per-leg summary between two consecutive airports"""
    origin: str
    destination: str
    distance_km: float
    distance_nm: float
    points: int


class MultiLegRouteSummaryResponse(BaseModel):
    """Response summarizing a multi-leg (optionally circular) route"""
    icao_codes: List[str]
    request_date: Optional[datetime]
    circular: bool
    total_distance_km: float
    total_distance_nm: float
    total_points: int
    first_3_coords: List[Tuple[float, float]]
    last_3_coords: List[Tuple[float, float]]
    segments: List[RouteSegmentSummary]

