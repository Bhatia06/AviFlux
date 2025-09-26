# AviFlux Backend API Documentation

## Overview
The AviFlux backend has been restructured to provide a comprehensive flight planning and weather analysis system. The system is now organized with proper separation of concerns:

- **Models**: Pydantic models for data validation and serialization
- **Services**: Business logic for flight planning and route calculations
- **API**: External integrations (Aviation Weather)
- **DTOs**: Data Transfer Objects for API requests/responses

## New Architecture

### Directory Structure
```
backend/
├── models/
│   ├── __init__.py
│   ├── flight_plan.py     # Core flight plan models
│   └── dtos.py           # Request/Response models
├── services/
│   ├── __init__.py
│   ├── flight_plan_service.py  # Flight plan generation logic
│   └── route_service.py        # Route calculation logic
├── api/
│   ├── __init__.py
│   └── aviation_weather.py     # Aviation weather API integration
├── main.py               # FastAPI application
├── get_path.py          # Legacy path calculation (integrated)
└── requirements.txt      # Dependencies
```

## API Endpoints

### 1. Health Check
- **GET** `/api/health`
- Returns system status and number of airports loaded

### 2. Flight Plan Generation (NEW)
- **POST** `/api/flightplan/generate`
- **Request Body**:
  ```json
  {
    "origin_icao": "KJFK",
    "destination_icao": "KSFO",
    "departure_time": "2025-09-25T12:00:00Z" // optional
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Flight plan generated successfully",
    "data": {
      "plan_id": "UUID-12345",
      "generated_at": "2025-09-25T09:00:00Z",
      "route": {
        "airports": ["KJFK", "KSFO"],
        "departure_time": "2025-09-25T12:00:00Z",
        "distance_nm": 2475.3,
        "estimated_time_min": 330
      },
      "summary": {
        "text": [
          "Weather at KJFK is VFR.",
          "Weather at KSFO is MVFR."
        ],
        "risk_index": "amber"
      },
      "risks": [],
      "map_layers": {
        "route": {
          "type": "LineString",
          "coordinates": [[-73.778, 40.641], [-122.375, 37.618]]
        },
        "airports": [
          {"icao": "KJFK", "status": "VFR", "coord": [-73.778, 40.641]},
          {"icao": "KSFO", "status": "MVFR", "coord": [-122.375, 37.618]}
        ],
        "hazards": []
      }
    }
  }
  ```

### 3. Flight Path Calculation (Enhanced)
- **GET** `/api/path/{origin_icao}/{destination_icao}`
- Integrates `get_path.py` functionality
- Returns detailed path information for React frontend

### 4. Flight Path Summary (Existing)
- **GET** `/api/flightpath/summary/{origin_icao}/{destination_icao}`
- Original endpoint, maintained for compatibility

## Data Models

### FlightPlan Model
The core flight plan structure includes:
- `plan_id`: Unique identifier
- `generated_at`: Generation timestamp
- `route`: Route information (airports, times, distances)
- `summary`: Text summary and risk assessment
- `risks`: List of identified hazards
- `map_layers`: GeoJSON data for map visualization

### Route Model
- `airports`: List of ICAO codes
- `departure_time`: Planned departure
- `distance_nm`: Distance in nautical miles
- `estimated_time_min`: Estimated flight time

### Summary Model
- `text`: Array of summary statements
- `risk_index`: Overall risk level (green/amber/red)

## Services

### FlightPlanService
- `generate_flight_plan()`: Creates comprehensive flight plans
- Weather integration via Aviation Weather API
- Risk assessment and route analysis

### RouteService
- `calculate_great_circle_route()`: Great circle calculations
- `create_route_geometry()`: GeoJSON generation
- `get_airport_info_list()`: Airport data formatting

## Aviation Weather Integration

### AviationWeatherAPI
- Integrates with aviationweather.gov
- Fetches METAR reports for airports
- Retrieves SIGMET data for hazards
- Provides comprehensive route weather analysis

### Features:
- Async HTTP client using aiohttp
- XML parsing for aviation weather data
- Real-time weather conditions
- Risk assessment based on flight categories

## Usage Examples

### Testing the API
Run the test script:
```bash
cd backend
python test_endpoints.py
```

### Starting the Server
```bash
cd backend
python main.py
```

The server will start on `http://localhost:8000` with automatic reload enabled.

### Frontend Integration
The new `/api/flightplan/generate` endpoint provides all data needed for:
- Route visualization on maps
- Weather hazard display
- Risk assessment presentation
- Flight summary information

## Dependencies
New dependencies added:
- `aiohttp>=3.9.0`: Async HTTP client for weather API
- Updated Pydantic models to v2 syntax

## Migration Notes
- Existing endpoints remain functional
- New endpoints provide enhanced functionality
- `get_path.py` functionality is now integrated
- Weather data is automatically fetched and analyzed
- All models use proper Pydantic validation

## Error Handling
- Comprehensive error responses
- Input validation via Pydantic
- Graceful fallbacks for weather data failures
- Detailed logging for debugging
