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


class MultiICAOFlightPlanRequest(BaseModel):
    """Request for flight plan generation with multiple ICAO codes"""
    icao_codes: List[str] = Field(..., min_length=2, description="Ordered list of ICAO codes (minimum 2 for origin and destination)")
    departure_time: Optional[datetime] = Field(None, description="Planned departure time (optional)")
    user_id: Optional[str] = Field(None, description="User identifier (optional)")
    circular: bool = Field(False, description="If true, return to the first airport")
    
    class Config:
        json_schema_extra = {
            "example": {
                "icao_codes": ["KJFK", "KLAX", "EGLL", "EDDF"],
                "departure_time": "2025-09-26T12:00:00Z",
                "user_id": "user-123",
                "circular": False
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


# Weather System DTOs
class WeatherBriefingRequest(BaseModel):
    """Request for weather briefing"""
    route_type: str = Field(..., description="'single' for two airports, 'multi_airport' for multiple")
    airports: List[str] = Field(..., description="List of ICAO airport codes (2-10 airports)")
    detail_level: str = Field(default="summary", description="'summary' or 'detailed'")
    include_ml_predictions: bool = Field(default=True, description="Include ML-based predictions")
    include_alternative_routes: bool = Field(default=False, description="Include alternative routes")
    enable_flight_monitoring: bool = Field(default=False, description="Enable real-time monitoring")
    flight_id: Optional[str] = Field(None, description="Optional flight identifier for monitoring")
    
    class Config:
        json_schema_extra = {
            "example": {
                "route_type": "single",
                "airports": ["KJFK", "KLAX"],
                "detail_level": "summary",
                "include_ml_predictions": True,
                "include_alternative_routes": False,
                "enable_flight_monitoring": False,
                "flight_id": "FL001"
            }
        }


class WeatherData(BaseModel):
    """Weather data for a single airport"""
    airport_code: str
    current_conditions: Dict
    forecast: Optional[Dict]
    metar: Optional[str]
    taf: Optional[str]
    pireps: Optional[List[Dict]]
    sigmets: Optional[List[Dict]]


class MLPredictions(BaseModel):
    """Machine learning predictions"""
    temperature: Optional[float]
    wind_speed: Optional[float]
    wind_direction: Optional[float]
    pressure: Optional[float]
    turbulence_level: Optional[str]
    icing_probability: Optional[float]
    weather_category: Optional[str]
    confidence_score: Optional[str]


class RiskAssessment(BaseModel):
    """Risk assessment data"""
    overall_risk_score: float = Field(..., ge=0, le=100, description="Risk score from 0-100")
    risk_category: str = Field(..., description="LOW, MODERATE, HIGH, SEVERE")
    flight_recommendation: str
    risk_factors: List[str]
    weather_hazards: List[str]


class AlternativeRoute(BaseModel):
    """Alternative route suggestion"""
    route_airports: List[str]
    reason: str
    estimated_additional_time: Optional[int]  # minutes
    risk_reduction: Optional[float]


class WeatherBriefingResponse(BaseModel):
    """Complete weather briefing response"""
    success: bool
    message: str
    briefing_id: str
    generated_at: datetime
    route_type: str
    airports: List[str]
    detail_level: str
    
    # Core briefing content
    executive_summary: str
    weather_data: List[WeatherData]
    ml_predictions: Optional[Dict[str, MLPredictions]]
    risk_assessment: RiskAssessment
    
    # Optional features
    alternative_routes: Optional[List[AlternativeRoute]]
    flight_monitoring_enabled: bool
    monitoring_id: Optional[str]
    
    # Additional metadata
    data_sources: List[str]
    last_updated: datetime
    valid_until: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Weather briefing generated successfully",
                "briefing_id": "WB-20250927-001",
                "generated_at": "2025-09-27T10:00:00Z",
                "route_type": "single",
                "airports": ["KJFK", "KLAX"],
                "detail_level": "summary",
                "executive_summary": "Weather conditions are favorable for VFR flight...",
                "risk_assessment": {
                    "overall_risk_score": 25.5,
                    "risk_category": "LOW",
                    "flight_recommendation": "PROCEED",
                    "risk_factors": ["Light turbulence expected"],
                    "weather_hazards": []
                },
                "flight_monitoring_enabled": False
            }
        }

