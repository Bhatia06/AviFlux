#!/usr/bin/env python3
"""
AviFlux Weather Summarizer App for Pilots
Main FastAPI application with flight path summary functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Tuple, Optional, Dict
import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging
from pyproj import Geod

# Import new models and services
from models import FlightPlanRequest, FlightPlanResponse, FlightPlan
from models.dtos import (
    MultiLegRouteRequest, MultiLegRouteSummaryResponse, RouteSegmentSummary,
    CreateFlightPlanRequest, FlightPlanSearchRequest
)
from services import FlightPlanService, RouteService
from services.flight_plans_service import FlightPlansService, FlightPlanResponse as DBFlightPlanResponse
from get_path import get_path_for_react

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AviFlux Weather Summarizer API", 
    version="1.0.0",
    description="Aviation weather summarizer and flight path analysis for pilots"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AirportDatabase:
    """
    Airport database class for managing airport data from Supabase.
    Downloads and caches airport data on initialization.
    """
    
    def __init__(self):
        """Initialize the airport database by loading data from Supabase."""
        self._airports_df: Optional[pd.DataFrame] = None
        self._icao_coords_map: Dict[str, Tuple[float, float]] = {}
        self._supabase_client = self._init_supabase()
        self._load_airports_data()
        
    def _init_supabase(self) -> Client:
        """Initialize Supabase client with environment variables."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
        
        return create_client(supabase_url, supabase_anon_key)
    
    def _load_airports_data(self):
        """Load airports data from Supabase and create ICAO to coordinates mapping."""
        logger.info("Loading airports data from Supabase...")
        
        try:
            # Query Supabase for all airports data using pagination
            all_data = []
            page_size = 1000
            offset = 0
            
            while True:
                response = self._supabase_client.table('airports').select('*').range(offset, offset + page_size - 1).execute()
                
                if not response.data:
                    break
                
                all_data.extend(response.data)
                logger.info(f"Loaded {len(response.data)} records (total so far: {len(all_data)})")
                
                # If we got less than the page size, we've reached the end
                if len(response.data) < page_size:
                    break
                
                offset += page_size
            
            if not all_data:
                logger.error("No airports data found in Supabase")
                raise ValueError("No airports data found in database")
            
            # Convert to DataFrame
            self._airports_df = pd.DataFrame(all_data)
            logger.info(f"Successfully loaded {len(self._airports_df)} total airports from Supabase")
            
            # Create ICAO to coordinates mapping
            self._create_icao_coords_map()
            
        except Exception as e:
            logger.error(f"Error loading airports data from Supabase: {e}")
            raise
    
    def _create_icao_coords_map(self):
        """Create a dictionary mapping ICAO codes to (latitude, longitude) tuples."""
        if self._airports_df is None:
            raise ValueError("Airports data not loaded")
        
        # Filter out rows with null ICAO codes or coordinates
        valid_airports = self._airports_df.dropna(subset=['icao_code', 'latitude', 'longitude'])
        
        # Create the mapping
        for _, airport in valid_airports.iterrows():
            icao_code = str(airport['icao_code']).upper()
            if icao_code and len(icao_code) == 4:  # Valid ICAO codes are 4 characters
                self._icao_coords_map[icao_code] = (
                    float(airport['latitude']),
                    float(airport['longitude'])
                )
        
        logger.info(f"Created ICAO coordinates mapping for {len(self._icao_coords_map)} airports")
    
    def get_coords(self, icao_code: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates for a given ICAO code.
        
        Args:
            icao_code: 4-letter ICAO airport code
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        return self._icao_coords_map.get(icao_code.upper())
    
    def get_airport_info(self, icao_code: str) -> Optional[Dict]:
        """
        Get full airport information for a given ICAO code.
        
        Args:
            icao_code: 4-letter ICAO airport code
            
        Returns:
            Dictionary with airport details or None if not found
        """
        if self._airports_df is None:
            return None
        
        airport = self._airports_df[self._airports_df['icao_code'] == icao_code.upper()]
        
        if airport.empty:
            return None
        
        airport_data = airport.iloc[0]
        return {
            'icao': airport_data['icao_code'],
            'name': airport_data['name'],
            'latitude': float(airport_data['latitude']),
            'longitude': float(airport_data['longitude']),
            'type': airport_data.get('type', 'airport'),
            'country': airport_data.get('iso_country', 'Unknown')
        }


# Pydantic Models
class PathSummaryResponse(BaseModel):
    """Response model for flight path summary."""
    origin_airport: str
    destination_airport: str
    distance_km: float
    path_points_total: int
    first_3_coords: List[Tuple[float, float]]
    last_3_coords: List[Tuple[float, float]]


# Initialize the airport database (singleton)
logger.info("Initializing airport database...")
airport_db = AirportDatabase()
logger.info("Airport database initialized successfully")

# Initialize services
flight_plan_service = FlightPlanService(airport_db)
route_service = RouteService(airport_db)

# Initialize flight plans database service
flight_plans_db_service = FlightPlansService(airport_db._supabase_client)


def calculate_flight_path(origin_icao: str, destination_icao: str) -> Dict:
    """
    Calculate great circle path between two airports using pyproj.
    
    Args:
        origin_icao: Origin airport ICAO code
        destination_icao: Destination airport ICAO code
        
    Returns:
        Dictionary containing path data and coordinates
    """
    # Get coordinates for both airports
    origin_coords = airport_db.get_coords(origin_icao)
    destination_coords = airport_db.get_coords(destination_icao)
    
    if not origin_coords:
        raise ValueError(f"Origin airport {origin_icao} not found")
    if not destination_coords:
        raise ValueError(f"Destination airport {destination_icao} not found")
    
    # Extract coordinates
    lat1, lon1 = origin_coords
    lat2, lon2 = destination_coords
    
    # Create geodesic object (WGS84 ellipsoid)
    geod = Geod(ellps='WGS84')
    
    # Calculate great circle path with 100 points
    num_points = 100
    path_points = geod.npts(lon1, lat1, lon2, lat2, npts=num_points-2)
    
    # Extract coordinates from path points
    if path_points:
        path_coords = [(lat, lon) for lon, lat in path_points]
    else:
        path_coords = []
    
    # Include start and end points
    all_coords = [(lat1, lon1)] + path_coords + [(lat2, lon2)]
    
    # Calculate total distance
    forward_azimuth, back_azimuth, distance = geod.inv(lon1, lat1, lon2, lat2)
    distance_km = distance / 1000
    
    return {
        'coordinates': all_coords,
        'distance_km': distance_km,
        'total_points': len(all_coords)
    }


# API Endpoints
@app.get("/", tags=["root"])
def read_root():
    """Root endpoint."""
    return {"message": "AviFlux Weather Summarizer API is running"}


@app.get("/api/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "airports_loaded": len(airport_db._icao_coords_map)}


@app.get("/api/flightpath/summary/{origin_icao}/{destination_icao}", 
         response_model=PathSummaryResponse,
         tags=["flight-path"])
def get_flight_path_summary(origin_icao: str, destination_icao: str):
    """
    Get flight path summary between two airports.
    
    Args:
        origin_icao: Origin airport ICAO code (4 letters)
        destination_icao: Destination airport ICAO code (4 letters)
        
    Returns:
        PathSummaryResponse with flight path details
        
    Raises:
        HTTPException: If airports are not found or invalid ICAO codes
    """
    # Validate ICAO codes
    if len(origin_icao) != 4 or len(destination_icao) != 4:
        raise HTTPException(
            status_code=400,
            detail="ICAO codes must be exactly 4 characters long"
        )
    
    origin_icao = origin_icao.upper()
    destination_icao = destination_icao.upper()
    
    try:
        # Get airport information
        origin_info = airport_db.get_airport_info(origin_icao)
        destination_info = airport_db.get_airport_info(destination_icao)
        
        if not origin_info:
            raise HTTPException(
                status_code=404,
                detail=f"Origin airport {origin_icao} not found"
            )
        
        if not destination_info:
            raise HTTPException(
                status_code=404,
                detail=f"Destination airport {destination_icao} not found"
            )
        
        # Calculate flight path
        path_data = calculate_flight_path(origin_icao, destination_icao)
        
        # Extract first 3 and last 3 coordinates
        coords = path_data['coordinates']
        first_3_coords = coords[:3] if len(coords) >= 3 else coords
        last_3_coords = coords[-3:] if len(coords) >= 3 else coords
        
        # Create response
        response = PathSummaryResponse(
            origin_airport=f"{origin_info['name']} ({origin_icao})",
            destination_airport=f"{destination_info['name']} ({destination_icao})",
            distance_km=round(path_data['distance_km'], 2),
            path_points_total=path_data['total_points'],
            first_3_coords=first_3_coords,
            last_3_coords=last_3_coords
        )
        
        logger.info(f"Calculated path summary: {origin_icao} -> {destination_icao}, "
                   f"{response.distance_km} km, {response.path_points_total} points")
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating flight path summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/flightpath/summary/route",
          response_model=MultiLegRouteSummaryResponse,
          tags=["flight-path"])
def get_multi_leg_route_summary(request: MultiLegRouteRequest):
    """
    Calculate summary for multi-airport route (supports circular path).

    Request body:
    {
      "icao_codes": ["KJFK", "KLAX", "EGLL", "EDDF", "RJTT"],
      "request_date": "2025-09-26T12:00:00Z",
      "circular": false
    }
    """
    icao_codes = [a.upper() for a in request.icao_codes]
    if len(icao_codes) < 2:
        raise HTTPException(status_code=400, detail="At least two airports required")

    try:
        data = route_service.calculate_multi_leg_route(icao_codes, circular=request.circular)

        segments = [
            RouteSegmentSummary(
                origin=s['origin'],
                destination=s['destination'],
                distance_km=round(s['distance_km'], 2),
                distance_nm=round(s['distance_nm'], 2),
                points=s['points']
            ) for s in data['segments']
        ]

        return MultiLegRouteSummaryResponse(
            icao_codes=icao_codes,
            request_date=request.request_date,
            circular=request.circular,
            total_distance_km=round(data['distance_km'], 2),
            total_distance_nm=round(data['distance_nm'], 2),
            total_points=data['total_points'],
            first_3_coords=data['coordinates'][:3] if data['total_points'] >= 3 else data['coordinates'],
            last_3_coords=data['coordinates'][-3:] if data['total_points'] >= 3 else data['coordinates'],
            segments=segments
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating multi-leg route: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/flightplan/generate", 
          response_model=FlightPlanResponse,
          tags=["flight-plan"])
async def generate_flight_plan(request: FlightPlanRequest):
    """
    Generate a complete flight plan with weather analysis
    
    Args:
        request: FlightPlanRequest with origin, destination, and optional departure time
        
    Returns:
        FlightPlanResponse with complete flight plan data
        
    Raises:
        HTTPException: If airports are not found or generation fails
    """
    try:
        # Validate ICAO codes
        origin_icao = request.origin_icao.upper()
        destination_icao = request.destination_icao.upper()
        
        if len(origin_icao) != 4 or len(destination_icao) != 4:
            raise HTTPException(
                status_code=400,
                detail="ICAO codes must be exactly 4 characters long"
            )
        
        logger.info(f"Generating flight plan: {origin_icao} -> {destination_icao}")
        
        # Generate flight plan using service
        flight_plan = await flight_plan_service.generate_flight_plan(
            origin_icao=origin_icao,
            destination_icao=destination_icao,
            departure_time=request.departure_time
        )
        
        return FlightPlanResponse(
            success=True,
            message="Flight plan generated successfully",
            data=flight_plan,
            error=None
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating flight plan: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/path/{origin_icao}/{destination_icao}",
         tags=["flight-path"])
def get_flight_path(origin_icao: str, destination_icao: str):
    """
    Get flight path data using get_path.py functionality
    
    Args:
        origin_icao: Origin airport ICAO code (4 letters)
        destination_icao: Destination airport ICAO code (4 letters)
        
    Returns:
        Flight path data formatted for React frontend
        
    Raises:
        HTTPException: If airports are not found or calculation fails
    """
    # Validate ICAO codes
    if len(origin_icao) != 4 or len(destination_icao) != 4:
        raise HTTPException(
            status_code=400,
            detail="ICAO codes must be exactly 4 characters long"
        )
    
    origin_icao = origin_icao.upper()
    destination_icao = destination_icao.upper()
    
    try:
        # Use get_path functionality
        result = get_path_for_react(origin_icao, destination_icao)
        
        if result['success']:
            logger.info(f"Path calculated successfully: {origin_icao} -> {destination_icao}")
            return result
        else:
            logger.error(f"Path calculation failed: {result.get('error', 'Unknown error')}")
            raise HTTPException(status_code=404, detail=result.get('error', 'Path calculation failed'))
            
    except Exception as e:
        logger.error(f"Error calculating flight path: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Flight Plans Database Endpoints
@app.post("/api/flight-plans", response_model=Dict, tags=["flight-plans"])
async def create_flight_plan_db(
    route_details: Dict,
    weather_summary: Dict,
    risk_analysis: Dict,
    map_layers: Dict,
    chart_data: Dict,
    user_id: Optional[str] = None
):
    """Create a new flight plan in the database"""
    result = await flight_plans_db_service.create_flight_plan(
        route_details=route_details,
        weather_summary=weather_summary,
        risk_analysis=risk_analysis,
        map_layers=map_layers,
        chart_data=chart_data,
        user_id=user_id
    )
    
    if result.success and result.data:
        return {
            "success": True,
            "message": result.message,
            "data": flight_plans_db_service.format_for_frontend(result.data)
        }
    else:
        raise HTTPException(status_code=400, detail=result.error or "Failed to create flight plan")


@app.get("/api/flight-plans/{plan_id}", response_model=Dict, tags=["flight-plans"])
async def get_flight_plan_db(plan_id: str):
    """Get a specific flight plan by ID"""
    result = await flight_plans_db_service.get_flight_plan(plan_id)
    
    if result.success and result.data:
        return {
            "success": True,
            "message": result.message,
            "data": flight_plans_db_service.format_for_frontend(result.data)
        }
    else:
        raise HTTPException(status_code=404, detail=result.error or "Flight plan not found")


@app.get("/api/flight-plans", response_model=Dict, tags=["flight-plans"])
async def get_all_flight_plans_db(
    limit: int = 50,
    offset: int = 0,
    user_id: Optional[str] = None
):
    """Get flight plans (optionally filtered by user)"""
    if user_id:
        result = await flight_plans_db_service.get_user_flight_plans(user_id, limit, offset)
    else:
        result = await flight_plans_db_service.get_all_flight_plans(limit, offset)
    
    if result.success and result.data:
        # Format all flight plans for frontend
        formatted_plans = [
            flight_plans_db_service.format_for_frontend(plan)
            for plan in result.data['flight_plans']
        ]
        
        return {
            "success": True,
            "message": result.message,
            "data": {
                "flight_plans": formatted_plans,
                "count": result.data['count'],
                "limit": limit,
                "offset": offset
            }
        }
    else:
        raise HTTPException(status_code=500, detail=result.error or "Failed to retrieve flight plans")


@app.put("/api/flight-plans/{plan_id}", response_model=Dict, tags=["flight-plans"])
async def update_flight_plan_db(plan_id: str, updates: Dict):
    """Update a flight plan"""
    result = await flight_plans_db_service.update_flight_plan(plan_id, updates)
    
    if result.success and result.data:
        return {
            "success": True,
            "message": result.message,
            "data": flight_plans_db_service.format_for_frontend(result.data)
        }
    else:
        raise HTTPException(status_code=404, detail=result.error or "Failed to update flight plan")


@app.delete("/api/flight-plans/{plan_id}", response_model=Dict, tags=["flight-plans"])
async def delete_flight_plan_db(plan_id: str):
    """Delete a flight plan"""
    result = await flight_plans_db_service.delete_flight_plan(plan_id)
    
    if result.success:
        return {
            "success": True,
            "message": result.message,
            "data": result.data
        }
    else:
        raise HTTPException(status_code=404, detail=result.error)


@app.post("/api/flight-plans/search", response_model=Dict, tags=["flight-plans"])
async def search_flight_plans_db(
    search_criteria: Dict,
    limit: int = 50,
    offset: int = 0
):
    """Search flight plans based on criteria"""
    result = await flight_plans_db_service.search_flight_plans(
        search_criteria, limit, offset
    )
    
    if result.success and result.data:
        # Format all flight plans for frontend
        formatted_plans = [
            flight_plans_db_service.format_for_frontend(plan)
            for plan in result.data['flight_plans']
        ]
        
        return {
            "success": True,
            "message": result.message,
            "data": {
                "flight_plans": formatted_plans,
                "count": result.data['count'],
                "search_criteria": search_criteria,
                "limit": limit,
                "offset": offset
            }
        }
    else:
        raise HTTPException(status_code=500, detail=result.error or "Search failed")


@app.post("/api/flight-plans/generate-and-save", response_model=Dict, tags=["flight-plans"])
async def generate_and_save_flight_plan(
    origin_icao: str,
    destination_icao: str,
    user_id: Optional[str] = None,
    departure_time: Optional[str] = None
):
    """Generate a flight plan and save it to the database"""
    try:
        # Parse departure time if provided
        parsed_departure_time = None
        if departure_time:
            from datetime import datetime
            parsed_departure_time = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
        
        # Generate the flight plan using existing service
        flight_plan = await flight_plan_service.generate_flight_plan(
            origin_icao=origin_icao,
            destination_icao=destination_icao,
            departure_time=parsed_departure_time
        )
        
        # Prepare data for database storage
        route_details = {
            "origin": origin_icao,
            "destination": destination_icao,
            "airports": flight_plan.route.airports,
            "departure_time": flight_plan.route.departure_time.isoformat() if flight_plan.route.departure_time else None,
            "distance_nm": flight_plan.route.distance_nm,
            "estimated_time_min": flight_plan.route.estimated_time_min
        }
        
        weather_summary = {
            "summary_text": flight_plan.summary.text,
            "risk_index": flight_plan.summary.risk_index
        }
        
        risk_analysis = {
            "risks": [
                {
                    "type": risk.type,
                    "subtype": risk.subtype,
                    "location": risk.location,
                    "severity": risk.severity,
                    "description": risk.description,
                    "geojson": risk.geojson
                }
                for risk in flight_plan.risks
            ],
            "overall_risk": flight_plan.summary.risk_index
        }
        
        map_layers = flight_plan.map_layers.model_dump() if flight_plan.map_layers else {}
        
        chart_data = {
            "plan_id": flight_plan.plan_id,
            "generated_at": flight_plan.generated_at.isoformat()
        }
        
        # Save to database
        save_result = await flight_plans_db_service.create_flight_plan(
            route_details=route_details,
            weather_summary=weather_summary,
            risk_analysis=risk_analysis,
            map_layers=map_layers,
            chart_data=chart_data,
            user_id=user_id
        )
        
        if save_result.success and save_result.data:
            return {
                "success": True,
                "message": "Flight plan generated and saved successfully",
                "data": {
                    "flight_plan": flight_plan.model_dump(),
                    "database_record": flight_plans_db_service.format_for_frontend(save_result.data)
                }
            }
        else:
            # Return the generated flight plan even if saving failed
            return {
                "success": False,
                "message": "Flight plan generated but failed to save to database",
                "data": {
                    "flight_plan": flight_plan.model_dump(),
                    "save_error": save_result.error
                }
            }
            
    except Exception as e:
        logger.error(f"Error generating and saving flight plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run with: python main.py
    import uvicorn
    
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
