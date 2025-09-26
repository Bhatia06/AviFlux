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
    airports: List[str] = Field(..., min_items=2, description="Ordered ICAO list: source -> intermediates -> destination")
    circular: bool = Field(False, description="If true, end leg returns to the source airport")

    class Config:
        json_schema_extra = {
            "example": {
                "airports": ["KJFK", "ORD", "KDEN", "KSFO"],
                "circular": True
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
    airports: List[str]
    circular: bool
    total_distance_km: float
    total_distance_nm: float
    total_points: int
    first_3_coords: List[Tuple[float, float]]
    last_3_coords: List[Tuple[float, float]]
    segments: List[RouteSegmentSummary]

