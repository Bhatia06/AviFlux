"""
Pydantic models for flight plan data structures
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union
from datetime import datetime
from uuid import UUID


class GeoJSONCoordinates(BaseModel):
    """GeoJSON coordinate structure"""
    type: Literal["Polygon", "LineString", "Point"]
    coordinates: List[List[List[float]]]  # For Polygon, adjust as needed for other types


class Risk(BaseModel):
    """Individual risk item"""
    type: str = Field(..., description="Type of risk (e.g., weather, terrain)")
    subtype: str = Field(..., description="Subtype of risk (e.g., convective, turbulence)")
    location: str = Field(..., description="Location identifier (e.g., airport ICAO)")
    severity: Literal["low", "medium", "high"] = Field(..., description="Risk severity level")
    description: str = Field(..., description="Human-readable risk description")
    geojson: GeoJSONCoordinates = Field(..., description="Geographic boundary of risk")


class Summary(BaseModel):
    """Flight plan summary"""
    text: List[str] = Field(..., description="List of summary text items")
    risk_index: Literal["green", "amber", "red"] = Field(..., description="Overall risk assessment")


class Route(BaseModel):
    """Flight route information"""
    airports: List[str] = Field(..., description="List of airport ICAO codes in route order")
    departure_time: datetime = Field(..., description="Planned departure time")
    distance_nm: float = Field(..., description="Total route distance in nautical miles")
    estimated_time_min: int = Field(..., description="Estimated flight time in minutes")


class AirportInfo(BaseModel):
    """Airport information for map display"""
    icao: str = Field(..., description="Airport ICAO code")
    status: Literal["VFR", "IFR", "MVFR"] = Field(..., description="Current weather status")
    coord: List[float] = Field(..., description="[longitude, latitude] coordinates")


class RouteGeometry(BaseModel):
    """Route geometry for map display"""
    type: Literal["LineString"]
    coordinates: List[List[float]] = Field(..., description="List of [longitude, latitude] points")


class HazardInfo(BaseModel):
    """Hazard information for map display"""
    type: str = Field(..., description="Type of hazard (e.g., sigmet, airmet)")
    severity: Literal["low", "medium", "high"] = Field(..., description="Hazard severity")
    geojson: GeoJSONCoordinates = Field(..., description="Geographic boundary of hazard")


class MapLayers(BaseModel):
    """Map layer data for visualization"""
    route: RouteGeometry = Field(..., description="Flight route geometry")
    airports: List[AirportInfo] = Field(..., description="Airport information along route")
    hazards: List[HazardInfo] = Field(..., description="Weather hazards and obstacles")


class FlightPlan(BaseModel):
    """Complete flight plan structure"""
    plan_id: str = Field(..., description="Unique flight plan identifier")
    generated_at: datetime = Field(..., description="Timestamp when plan was generated")
    route: Route = Field(..., description="Route information")
    summary: Summary = Field(..., description="Flight plan summary")
    risks: List[Risk] = Field(default=[], description="List of identified risks")
    map_layers: MapLayers = Field(..., description="Map visualization data")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "plan_id": "UUID-12345",
                "generated_at": "2025-09-25T09:00:00Z",
                "route": {
                    "airports": ["KJFK", "ORD", "KSFO"],
                    "departure_time": "2025-09-25T12:00:00Z",
                    "distance_nm": 1780,
                    "estimated_time_min": 215
                },
                "summary": {
                    "text": [
                        "Weather at departure (KJFK) is VFR.",
                        "Convective SIGMET active near ORD between 15Z–18Z."
                    ],
                    "risk_index": "amber"
                },
                "risks": [],
                "map_layers": {
                    "route": {
                        "type": "LineString",
                        "coordinates": [[-73.778, 40.641], [-87.907, 41.974]]
                    },
                    "airports": [
                        {"icao": "KJFK", "status": "VFR", "coord": [-73.778, 40.641]}
                    ],
                    "hazards": []
                }
            }
        }
