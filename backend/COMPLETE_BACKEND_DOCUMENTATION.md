# AviFlux Backend Documentation

**Complete Backend API Documentation and System Architecture**

*Version: 2.0.0 - Updated September 27, 2025*

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Authentication System](#authentication-system)
5. [Flight Path Calculation](#flight-path-calculation)
6. [Database Services](#database-services)
7. [API Endpoints](#api-endpoints)
8. [Data Models](#data-models)
9. [Configuration](#configuration)
10. [Testing](#testing)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)

---

## Overview

AviFlux is a comprehensive aviation flight planning and weather analysis system built with FastAPI. The backend provides:

- **OAuth Authentication** with Google via Supabase
- **Flight Path Calculation** using great circle mathematics
- **Multi-leg Route Planning** with ICAO airport codes
- **Flight Plan Management** with full CRUD operations  
- **Weather Integration** for aviation-specific conditions
- **Real-time Database** operations with Supabase
- **Advanced Path Calculations** with antimeridian crossing support

### Technology Stack

- **Framework**: FastAPI 0.104.0+
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth + Google OAuth 2.0
- **Geospatial**: PyProj, Pandas, NumPy
- **Validation**: Pydantic 2.5.0+
- **Environment**: Python 3.8+

---

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   FastAPI       │───▶│   Supabase      │
│   (React/Vue)   │    │   Backend       │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   External APIs │
                       │   (Weather,     │
                       │    Aviation)    │
                       └─────────────────┘
```

### Backend Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│  Routes Layer                                               │
│  ├── auth_routes.py      (OAuth & User Management)         │
│  ├── flight_routes.py    (Flight Planning)                 │
│  └── weather_routes.py   (Weather Integration)             │
├─────────────────────────────────────────────────────────────┤
│  Middleware Layer                                           │
│  ├── auth_middleware.py  (JWT Validation)                  │
│  ├── cors_middleware.py  (Cross-Origin Requests)           │
│  └── error_middleware.py (Global Error Handling)           │
├─────────────────────────────────────────────────────────────┤
│  Services Layer                                             │
│  ├── auth_service.py     (Authentication Logic)            │
│  ├── flight_plans_service.py (Flight Plan CRUD)            │
│  ├── route_service.py    (Path Calculations)               │
│  └── weather_service.py  (Weather Data)                    │
├─────────────────────────────────────────────────────────────┤
│  Models Layer                                               │
│  ├── auth_models.py      (User & Token Models)             │
│  ├── flight_models.py    (Flight Plan Models)              │
│  └── dtos.py            (Data Transfer Objects)            │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ├── get_path.py         (Airport & Path Logic)            │
│  ├── improved_path_service.py (Enhanced Calculations)       │
│  └── supabase_client.py  (Database Connection)             │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Main Application (`main.py`)

The central FastAPI application that orchestrates all services and routes.

**Key Features:**
- CORS middleware configuration for frontend integration
- Global exception handling for authentication errors
- Router registration for modular endpoint management
- Supabase client initialization
- Airport database management

**Critical Sections:**
```python
# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", 
                   "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication integration
app.include_router(auth_router)

# Global authentication error handling
@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(
        status_code=401,
        content=AuthError(
            success=False,
            error=exc.message,
            error_code=exc.error_code,
            details=exc.details
        ).dict()
    )
```

### 2. Airport Database System (`get_path.py`)

Manages airport data loading, caching, and great circle path calculations.

**Key Features:**
- Automated airport data loading from Supabase (4,879+ airports)
- Efficient ICAO code to coordinates mapping
- Great circle path calculations with antimeridian handling
- Distance accuracy improvements (reduced from ~600km to <8km error)
- Visualization coordinate generation for frontend mapping

**Core Functions:**

#### `load_airports_from_supabase()`
- Loads all airport data with pagination support
- Caches data in memory for performance
- Handles up to 4,879 airports globally

#### `calculate_great_circle_path(icao1, icao2, num_points=100)`
- Calculates accurate great circle paths between airports
- Handles antimeridian crossings properly
- Provides both normalized and visualization coordinates
- Returns comprehensive path data including distances and bearings

**Recent Improvements:**
- Enhanced coordinate normalization
- Haversine distance validation
- Antimeridian crossing detection and handling
- Improved accuracy for long-distance routes

---

## Authentication System

### Overview

Complete OAuth 2.0 authentication system using Supabase Auth with Google provider.

### Components

#### 1. Authentication Models (`models/auth_models.py`)

**UserProfile Model:**
```python
class UserProfile(BaseModel):
    id: str                              # Supabase user ID
    email: EmailStr                      # User email (validated)
    full_name: Optional[str]             # From OAuth provider
    avatar_url: Optional[str]            # Profile picture URL
    provider: str                        # OAuth provider (google)
    created_at: datetime                 # Account creation
    last_sign_in: Optional[datetime]     # Last login timestamp
```

**AuthTokens Model:**
```python
class AuthTokens(BaseModel):
    access_token: str                    # JWT access token
    refresh_token: str                   # Token refresh capability
    expires_in: int                      # Expiration time (seconds)
    expires_at: int                      # Expiration timestamp
    token_type: str = "Bearer"          # Token type
```

#### 2. Authentication Service (`services/auth_service.py`)

Central authentication logic with Supabase integration.

**Key Methods:**

**`generate_oauth_url(provider="google", redirect_to=None)`**
- Generates Google OAuth authentication URLs
- Configurable redirect URLs for different environments
- Returns structured OAuth response

**`handle_oauth_callback(access_token, refresh_token)`**
- Processes OAuth callback tokens
- Creates user sessions in Supabase
- Returns complete user profile and tokens

**`validate_token(token)`**
- Validates JWT access tokens
- Returns user profile for valid tokens
- Handles token expiration and invalid formats

**`refresh_token(refresh_token)`**
- Refreshes expired access tokens
- Returns new token pair and updated user data
- Maintains session continuity

#### 3. Authentication Middleware (`middleware/auth_middleware.py`)

FastAPI dependency injection system for route protection.

**Dependencies:**

**`get_current_user()`** - Required Authentication
```python
@app.get("/protected")
async def protected_endpoint(user: UserProfile = Depends(get_current_user)):
    return {"message": f"Hello {user.full_name}!"}
```

**`get_optional_user()`** - Optional Authentication
```python
@app.get("/public")
async def public_endpoint(user: Optional[UserProfile] = Depends(get_optional_user)):
    if user:
        return {"authenticated": True, "user": user.email}
    return {"authenticated": False}
```

**`get_admin_user()`** - Admin-Level Authentication
```python
@app.get("/admin")
async def admin_endpoint(admin: UserProfile = Depends(get_admin_user)):
    return {"admin_access": True, "user": admin.email}
```

#### 4. Authentication Routes (`routes/auth_routes.py`)

Complete set of authentication endpoints.

**Available Endpoints:**

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/auth/oauth-url` | GET | Generate OAuth URL | No |
| `/auth/callback` | POST | Handle OAuth callback | No |
| `/auth/me` | GET | Get user profile | Yes |
| `/auth/refresh` | POST | Refresh tokens | No |
| `/auth/logout` | POST | Logout user | Yes |
| `/auth/validate` | GET | Validate token | Optional |
| `/auth/protected` | GET | Test protected endpoint | Yes |
| `/auth/public` | GET | Test public endpoint | Optional |

---

## Flight Path Calculation

### Great Circle Path Mathematics

The system uses advanced geodesic calculations for accurate flight path planning.

#### Core Algorithm (`calculate_great_circle_path`)

**Input Parameters:**
- `icao1`: Departure airport ICAO code
- `icao2`: Arrival airport ICAO code  
- `num_points`: Path resolution (default: 100 points)

**Calculation Process:**

1. **Airport Data Retrieval:**
   ```python
   airport1 = find_airport_by_icao(icao1)
   airport2 = find_airport_by_icao(icao2)
   ```

2. **Coordinate Extraction:**
   ```python
   lat1, lon1 = airport1['latitude'], airport1['longitude']
   lat2, lon2 = airport2['latitude'], airport2['longitude']
   ```

3. **Antimeridian Handling:**
   ```python
   lon1_adj, lon2_adj = handle_antimeridian_crossing(lon1, lon2)
   ```

4. **Geodesic Calculation (WGS84 Ellipsoid):**
   ```python
   geod = Geod(ellps='WGS84')
   forward_azimuth, back_azimuth, distance_meters = geod.inv(lon1, lat1, lon2, lat2)
   ```

5. **Path Point Generation:**
   ```python
   intermediate_points = geod.npts(lon1_adj, lat1, lon2_adj, lat2, npts=num_points-2)
   ```

6. **Coordinate Normalization:**
   ```python
   normalized_coordinates = [normalize_longitude(lon) for lon in longitudes]
   ```

#### Antimeridian Crossing Handling

**Problem:** Routes crossing the 180° meridian can show incorrect visualizations.

**Solution:** Dual coordinate systems:
- **Normalized Coordinates** ([-180°, 180°]): For storage and calculations
- **Visualization Coordinates**: Continuous path for frontend mapping

**Implementation:**
```python
def handle_antimeridian_crossing(lon1: float, lon2: float) -> Tuple[float, float]:
    """Handle 180° meridian crossings for shortest path calculations."""
    lon1 = normalize_longitude(lon1)
    lon2 = normalize_longitude(lon2)
    
    direct_diff = abs(lon2 - lon1)
    cross_diff = 360 - direct_diff
    
    if cross_diff < direct_diff:
        # Crossing is shorter, adjust coordinates
        if lon1 > lon2:
            lon2 += 360
        else:
            lon1 += 360
    
    return lon1, lon2
```

#### Distance Calculation Accuracy

**Recent Improvements:**
- Geodesic calculations using PyProj library
- Haversine distance validation for accuracy verification
- Coordinate system normalization
- Error reduction from ~600km to <8km for long-distance routes

**Validation Process:**
```python
# Calculate using geodesic (primary method)
distance_meters = geod.inv(lon1, lat1, lon2, lat2)[2]

# Validate with Haversine (backup verification)  
haversine_dist = haversine_distance(lat1, lon1, lat2, lon2)
distance_diff = abs(distance_meters - haversine_dist)

if distance_diff > 1000:  # Flag discrepancies > 1km
    logger.warning(f"Distance discrepancy detected: {distance_diff/1000:.2f}km")
```

---

## Database Services

### Flight Plans Service (`services/flight_plans_service.py`)

Complete CRUD operations for flight plan management.

#### Service Architecture

**FlightPlansService Class Features:**
- Async database operations
- Comprehensive error handling
- Pagination support
- Search functionality
- User-specific flight plan isolation

#### Core Methods

**1. Create Flight Plan**
```python
async def create_flight_plan(
    self,
    user_id: str,
    title: str,
    departure_icao: str,
    arrival_icao: str,
    route_data: Dict,
    description: Optional[str] = None
) -> FlightPlanResponse:
```

**Features:**
- User association for multi-tenant support
- JSON route data storage
- Automatic timestamp generation
- Comprehensive validation

**2. Retrieve Flight Plans**
```python
async def get_flight_plans(
    self,
    user_id: str,
    limit: int = 50,
    offset: int = 0
) -> List[FlightPlanResponse]:
```

**Features:**
- User-specific filtering
- Pagination support
- Ordered by creation date
- Optional search parameters

**3. Update Flight Plan**
```python
async def update_flight_plan(
    self,
    flight_plan_id: str,
    user_id: str,
    updates: Dict[str, Any]
) -> FlightPlanResponse:
```

**Features:**
- User authorization verification
- Selective field updates
- Automatic update timestamps
- Data validation

**4. Delete Flight Plan**
```python
async def delete_flight_plan(
    self,
    flight_plan_id: str,
    user_id: str
) -> bool:
```

**Features:**
- User authorization verification
- Soft delete capability
- Cascade handling for related data

**5. Search Functionality**
```python
async def search_flight_plans(
    self,
    user_id: str,
    query: str,
    filters: Optional[Dict] = None
) -> List[FlightPlanResponse]:
```

**Features:**
- Full-text search across titles and descriptions
- Airport code filtering
- Date range filtering
- User-scoped results

### Database Schema

#### Flight Plans Table Structure

```sql
CREATE TABLE flight_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    departure_icao VARCHAR(4) NOT NULL,
    arrival_icao VARCHAR(4) NOT NULL,
    route_data JSONB NOT NULL,           -- Stores complete route information
    waypoints JSONB,                     -- Optional waypoint data
    estimated_duration INTEGER,          -- Flight duration in minutes
    estimated_distance NUMERIC(10, 2),   -- Distance in kilometers
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Indexes for performance
    INDEX idx_flight_plans_user_id (user_id),
    INDEX idx_flight_plans_icao (departure_icao, arrival_icao),
    INDEX idx_flight_plans_created_at (created_at DESC)
);
```

#### Airports Table Structure

```sql
CREATE TABLE airports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    icao VARCHAR(4) UNIQUE NOT NULL,
    iata VARCHAR(3),
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    municipality VARCHAR(100),
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(11, 7) NOT NULL,
    elevation_ft INTEGER,
    type VARCHAR(50),
    
    -- Spatial index for geographic queries
    INDEX idx_airports_location (latitude, longitude),
    INDEX idx_airports_icao (icao),
    INDEX idx_airports_country (country)
);
```

---

## API Endpoints

### Complete API Reference

#### Authentication Endpoints

**1. Generate OAuth URL**
```http
GET /auth/oauth-url?provider=google&redirect_to=http://localhost:3000/callback
```

**Response:**
```json
{
    "success": true,
    "auth_url": "https://accounts.google.com/oauth/authorize?...",
    "provider": "google"
}
```

**2. Handle OAuth Callback**
```http
POST /auth/callback
Content-Type: application/json

{
    "access_token": "eyJhbGciOiJSUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response:**
```json
{
    "success": true,
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "full_name": "John Doe",
        "avatar_url": "https://lh3.googleusercontent.com/...",
        "provider": "google",
        "created_at": "2024-01-01T00:00:00Z",
        "last_sign_in": "2024-01-01T12:00:00Z"
    },
    "tokens": {
        "access_token": "eyJhbGciOiJSUzI1NiIs...",
        "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
        "expires_in": 3600,
        "expires_at": 1704067200,
        "token_type": "Bearer"
    },
    "message": "OAuth login successful"
}
```

#### Flight Path Endpoints

**1. Calculate Multi-ICAO Path (Enhanced)**
```http
GET /api/path?icao_codes=KJFK,EGLL,OMDB,NZAA
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

**Parameters:**
- `icao_codes`: Comma-separated list of ICAO airport codes (2-10 airports)

**Response for Multiple Airports:**
```json
{
    "success": true,
    "data": {
        "route_type": "multi_leg",
        "total_airports": 4,
        "route_summary": {
            "total_segments": 3,
            "total_distance_km": 24718.42,
            "total_distance_nm": 13346.88,
            "total_estimated_duration_hours": 28.5,
            "segments": [
                {
                    "segment_number": 1,
                    "departure": "KJFK",
                    "arrival": "EGLL",
                    "distance_km": 5554.78,
                    "distance_nm": 2999.12,
                    "estimated_duration_hours": 8.5,
                    "path_coordinates": [...],
                    "antimeridian_crossing": false
                },
                {
                    "segment_number": 2,
                    "departure": "EGLL",
                    "arrival": "OMDB",
                    "distance_km": 5497.52,
                    "distance_nm": 2968.64,
                    "estimated_duration_hours": 7.2,
                    "path_coordinates": [...],
                    "antimeridian_crossing": false
                }
            ]
        }
    }
}
```

**Response for Two Airports (Legacy Format):**
```json
{
    "success": true,
    "data": {
        "departure": {
            "icao": "KJFK",
            "name": "John F Kennedy International Airport",
            "country": "United States",
            "coordinates": [-73.779317, 40.639447]
        },
        "arrival": {
            "icao": "EGLL", 
            "name": "London Heathrow Airport",
            "country": "United Kingdom",
            "coordinates": [-0.461389, 51.4775]
        },
        "path": {
            "coordinates": [
                [-73.779317, 40.639447],
                [-72.5, 41.2],
                ...
                [-0.461389, 51.4775]
            ],
            "total_distance_km": 5554.78,
            "total_distance_nm": 2999.12,
            "antimeridian_crossing": false
        }
    }
}
```

**2. Calculate Simple Path (Legacy - Two Airports Only)**
```http
GET /api/path/simple?departure=KJFK&arrival=EGLL
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

**Parameters:**
- `departure`: Origin airport ICAO code (4 letters)
- `arrival`: Destination airport ICAO code (4 letters)

**Response:**
```json
{
    "success": true,
    "data": {
        "departure": {
            "icao": "KJFK",
            "name": "John F Kennedy International Airport",
            "country": "United States",
            "coordinates": [-73.779317, 40.639447]
        },
        "arrival": {
            "icao": "EGLL", 
            "name": "London Heathrow Airport",
            "country": "United Kingdom",
            "coordinates": [-0.461389, 51.4775]
        },
        "path": {
            "coordinates": [
                [-73.779317, 40.639447],
                [-72.5, 41.2],
                ...
                [-0.461389, 51.4775]
            ],
            "total_distance_km": 5554.78,
            "total_distance_nm": 2999.12,
            "antimeridian_crossing": false
        }
    }
}
```

**3. Multi-Leg Route Calculation (POST)**
```http
POST /api/route/multi-leg
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
Content-Type: application/json

{
    "icao_codes": ["KJFK", "EGLL", "OMDB", "NZAA"],
    "circular": false
}
```

**Response:**
```json
{
    "success": true,
    "route_summary": {
        "total_segments": 3,
        "total_distance_km": 24718.42,
        "total_distance_nm": 13346.88,
        "total_estimated_duration_hours": 28.5,
        "segments": [
            {
                "segment_number": 1,
                "departure": "KJFK",
                "arrival": "EGLL",
                "distance_km": 5554.78,
                "distance_nm": 2999.12,
                "estimated_duration_hours": 8.5,
                "path_coordinates": [...],
                "antimeridian_crossing": false
            }
        ]
    }
}
```

#### Enhanced Flight Path Usage Examples

**Multi-ICAO Path Examples:**

1. **Two Airports (Simple Path):**
   ```bash
   GET /api/path?icao_codes=KJFK,EGLL
   # Returns legacy format for compatibility
   ```

2. **Three Airports (Multi-leg):**
   ```bash
   GET /api/path?icao_codes=KJFK,EGLL,OMDB
   # Returns multi-leg route summary
   ```

3. **Complex Multi-leg Route (Up to 10 airports):**
   ```bash
   GET /api/path?icao_codes=KJFK,EGLL,OMDB,NZAA,YSSY,RJTT,VHHH
   # Returns complete multi-leg route with all segments
   ```

4. **Round-the-World Route:**
   ```bash
   GET /api/path?icao_codes=KJFK,EGLL,OMDB,VIDP,VTBS,RJTT,KSEA,KJFK
   # Include starting airport at end for circular route
   ```

**Response Format Differences:**

- **2 Airports**: Returns legacy single-path format
- **3+ Airports**: Returns multi-leg route summary with segments

**Alternative Endpoints:**

- **Legacy Simple Path**: `GET /api/path/simple?departure=KJFK&arrival=EGLL`
- **POST Multi-leg**: `POST /api/route/multi-leg` with JSON body
- **Path Parameters**: `GET /api/path/KJFK/EGLL` (original format)

#### Flight Plan Management

**1. Create Flight Plan**
```http
POST /api/flightplans
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
Content-Type: application/json

{
    "title": "New York to London",
    "description": "Business trip flight plan",
    "departure_icao": "KJFK",
    "arrival_icao": "EGLL", 
    "route_data": {
        "waypoints": [...],
        "estimated_duration": 480,
        "fuel_requirements": {...}
    }
}
```

**2. Get User Flight Plans**
```http
GET /api/flightplans?limit=20&offset=0
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

**3. Update Flight Plan**
```http
PUT /api/flightplans/{flight_plan_id}
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
Content-Type: application/json

{
    "title": "Updated Flight Plan",
    "description": "Modified description"
}
```

**4. Delete Flight Plan**
```http
DELETE /api/flightplans/{flight_plan_id}
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

**5. Multi-ICAO Flight Plan Generation**
```http
POST /api/flightplan/generate
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
Content-Type: application/json

{
    "title": "Multi-City Tour",
    "description": "Round the world flight",
    "icao_codes": ["KJFK", "EGLL", "OMDB", "NZAA", "KJFK"],
    "include_return": true
}
```

---

## Data Models

### Core Pydantic Models

#### 1. Flight Plan Models (`models/flight_models.py`)

**FlightPlanRequest:**
```python
class FlightPlanRequest(BaseModel):
    departure_icao: str = Field(..., min_length=4, max_length=4)
    arrival_icao: str = Field(..., min_length=4, max_length=4)
    waypoints: Optional[List[str]] = None
    preferred_altitude: Optional[int] = None
    aircraft_type: Optional[str] = None
```

**FlightPlanResponse:**
```python
class FlightPlanResponse(BaseModel):
    id: str
    title: str
    departure_icao: str
    arrival_icao: str
    route_data: Dict[str, Any]
    estimated_duration: Optional[int]
    estimated_distance: Optional[float]
    created_at: datetime
    updated_at: datetime
```

#### 2. Route Models (`models/dtos.py`)

**MultiLegRouteRequest:**
```python
class MultiLegRouteRequest(BaseModel):
    airports: List[str] = Field(..., min_items=2, max_items=10)
    include_return: bool = False
    aircraft_type: Optional[str] = None
    preferred_altitude: Optional[int] = None
```

**RouteSegmentSummary:**
```python
class RouteSegmentSummary(BaseModel):
    segment_number: int
    departure: str
    arrival: str  
    distance_km: float
    distance_nm: float
    estimated_duration_hours: float
    path_coordinates: List[List[float]]
    antimeridian_crossing: bool
```

**MultiLegRouteSummaryResponse:**
```python
class MultiLegRouteSummaryResponse(BaseModel):
    total_segments: int
    total_distance_km: float
    total_distance_nm: float
    total_estimated_duration_hours: float
    segments: List[RouteSegmentSummary]
```

#### 3. Authentication Models (`models/auth_models.py`)

Complete authentication model suite as documented in the Authentication System section.

---

## Configuration

### Environment Variables

**Required Variables:**
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key  # For admin operations
SUPABASE_JWT_SECRET=your-jwt-secret

# FastAPI Configuration  
SECRET_KEY=your-secret-key-for-sessions
DEBUG=true
ENVIRONMENT=development

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# OAuth Configuration
FRONTEND_URL=http://localhost:3000
AUTH_CALLBACK_URL=http://localhost:3000/auth/callback
```

### Dependencies (`requirements.txt`)

```txt
# FastAPI framework and dependencies
fastapi>=0.104.0
uvicorn[standard]>=0.24.0

# Data validation and serialization
pydantic>=2.5.0

# Data processing and geospatial calculations
pandas>=2.0.0
pyproj>=3.4.0
numpy>=1.24.0

# Database and environment
supabase>=2.0.0
python-dotenv>=1.0.0

# Authentication and JWT
PyJWT>=2.8.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# HTTP client for aviation weather API
aiohttp>=3.9.0

# Development dependencies (optional)
pytest>=7.4.0
httpx>=0.25.0  # For testing FastAPI endpoints
```

---

## Testing

### Test Suite Structure

#### 1. Authentication Tests (`test_auth.py`)

**Test Coverage:**
- OAuth service initialization
- OAuth URL generation
- Token validation and refresh
- Protected endpoint access
- User profile management

**Sample Test:**
```python
def test_oauth_url_generation():
    """Test OAuth URL generation."""
    oauth_response = auth_service.generate_oauth_url("google", "http://localhost:3000/callback")
    assert oauth_response.success == True
    assert oauth_response.provider == "google"
    assert "accounts.google.com" in oauth_response.auth_url
```

#### 2. Flight Plan Tests (`test_flight_plans_api.py`)

**Test Coverage:**
- CRUD operations for flight plans
- User authorization validation
- Data persistence and retrieval
- Search functionality
- Multi-ICAO flight plan generation

#### 3. Path Calculation Tests (`test_endpoints.py`)

**Test Coverage:**
- Great circle path accuracy
- Antimeridian crossing handling
- Distance calculation validation
- Multi-leg route planning
- Coordinate normalization

#### 4. Integration Tests

**End-to-End Testing:**
- Complete OAuth flow simulation
- Protected endpoint access
- Database integration validation
- Error handling verification

### Running Tests

**Individual Test Files:**
```bash
python test_auth.py
python test_flight_plans_api.py  
python test_endpoints.py
```

**Complete Test Suite:**
```bash
pytest -v
```

---

## Deployment

### Development Deployment

**1. Environment Setup:**
```bash
# Clone repository
git clone https://github.com/Bhatia06/AviFlux.git
cd AviFlux/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**2. Environment Configuration:**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Supabase credentials
nano .env
```

**3. Database Setup:**
- Configure Supabase project
- Set up Google OAuth provider
- Import airport data (handled automatically)

**4. Start Development Server:**
```bash
python main.py
```

**Server will be available at:**
- API: `http://localhost:8000`
- Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Production Deployment

**1. Docker Deployment:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. Environment Variables (Production):**
```bash
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://your-frontend-domain.com
SUPABASE_URL=https://your-project-id.supabase.co
# ... other production values
```

**3. Security Considerations:**
- Use HTTPS only
- Secure token storage
- Rate limiting implementation
- Input validation and sanitization
- Audit logging

---

## Troubleshooting

### Common Issues

#### 1. Authentication Issues

**Problem:** OAuth callback fails
**Solution:** 
- Verify redirect URLs match exactly in Google OAuth and Supabase
- Check CORS configuration includes frontend origin
- Validate environment variables are loaded correctly

**Problem:** Token validation fails
**Solution:**
- Check JWT secret configuration
- Verify token format and expiration
- Ensure Supabase auth is properly configured

#### 2. Path Calculation Issues

**Problem:** Distance calculations inaccurate
**Solution:**
- Verify PyProj installation and WGS84 ellipsoid usage
- Check coordinate normalization functions
- Validate airport data integrity

**Problem:** Antimeridian crossing visualization incorrect
**Solution:**
- Use visualization coordinates instead of normalized coordinates
- Implement proper coordinate adjustment logic
- Test with trans-Pacific routes

#### 3. Database Issues

**Problem:** Supabase connection fails
**Solution:**
- Verify Supabase URL and keys
- Check network connectivity
- Validate database permissions and RLS policies

**Problem:** Flight plan operations fail
**Solution:**
- Check user authentication status
- Verify database schema matches models
- Validate JSON data structure

#### 4. Performance Issues

**Problem:** Airport data loading slow
**Solution:**
- Implement proper caching mechanisms
- Use pagination for large datasets
- Consider database indexing improvements

### Debug Mode

**Enable Debug Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check Environment Variables:**
```python
import os
from dotenv import load_dotenv
load_dotenv()

print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_ANON_KEY:", "Set" if os.getenv("SUPABASE_ANON_KEY") else "Not Set")
```

**Validate Database Connection:**
```python
from services.flight_plans_service import flight_plans_service
# Test database connectivity
```

---

## Recent Updates (September 2025)

### Major Enhancements

**1. OAuth Authentication System (Complete)**
- Google OAuth integration via Supabase Auth
- JWT token management with refresh capabilities
- Protected endpoint middleware
- User profile management
- Session handling and logout functionality

**2. Flight Path Calculation Improvements**
- Enhanced great circle calculations with PyProj
- Antimeridian crossing handling (fixed visualization issues)
- Distance accuracy improvements (reduced error from ~600km to <8km)
- Dual coordinate system for storage and visualization
- Haversine distance validation

**3. Database Service Enhancements**
- Complete CRUD operations for flight plans
- User-scoped data access with proper authorization
- Pagination and search functionality
- Multi-ICAO flight plan generation
- JSON route data storage with flexible schema

**4. API Endpoint Expansion**
- Authentication endpoints (/auth/*)
- Flight plan management (/api/flightplans/*)
- Multi-leg route planning (/api/route/*)
- Path calculation endpoints (/api/path/*)
- Protected and public endpoint examples

**5. Testing Infrastructure**
- Comprehensive test suites for all components
- Authentication flow testing
- Path calculation validation
- Database operation testing
- Integration test capabilities

### Performance Optimizations

- Airport data caching for improved response times
- Efficient database queries with proper indexing  
- Asynchronous operations throughout the system
- Memory-efficient data structures
- Connection pooling for database operations

### Security Improvements

- JWT token validation middleware
- User authentication and authorization
- CORS protection with configurable origins
- Input validation and sanitization
- Secure token storage recommendations

---

## Support and Maintenance

### Documentation Updates

This documentation is maintained alongside code changes and should be updated when:
- New endpoints are added
- Authentication logic changes
- Database schema modifications occur
- Configuration requirements change
- Bug fixes affect API behavior

### Contact and Support

- **Repository**: https://github.com/Bhatia06/AviFlux
- **Issues**: GitHub Issues for bug reports and feature requests
- **Documentation**: Backend README and API documentation
- **Testing**: Automated test suite for validation

---

*This documentation covers the complete AviFlux backend system as of September 27, 2025. For the most current information, please refer to the source code and test files in the repository.*