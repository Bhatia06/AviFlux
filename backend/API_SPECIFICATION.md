# AviFlux API Specification

**OpenAPI 3.0 Specification for AviFlux Backend**

*Version: 2.0.0 - September 27, 2025*

## Base Information

```yaml
openapi: 3.0.0
info:
  title: AviFlux Weather Summarizer API
  description: Aviation weather summarizer and flight path analysis for pilots
  version: 2.0.0
  contact:
    name: AviFlux Development Team
    url: https://github.com/Bhatia06/AviFlux
servers:
  - url: http://localhost:8000
    description: Development server
  - url: https://api.aviflux.com
    description: Production server (when deployed)
```

## Authentication

All protected endpoints require Bearer token authentication:

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT access token obtained from OAuth flow
```

**Usage:**
```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Authentication Endpoints

### Generate OAuth URL

**`GET /auth/oauth-url`**

Generate Google OAuth authentication URL.

**Parameters:**
- `provider` (query, optional): OAuth provider name (default: "google")
- `redirect_to` (query, optional): URL to redirect after authentication

**Response 200:**
```json
{
  "success": true,
  "auth_url": "https://accounts.google.com/oauth/authorize?client_id=...",
  "provider": "google"
}
```

**Example:**
```bash
curl "http://localhost:8000/auth/oauth-url?provider=google&redirect_to=http://localhost:3000/callback"
```

### Handle OAuth Callback

**`POST /auth/callback`**

Process OAuth callback tokens and create user session.

**Request Body:**
```json
{
  "access_token": "ya29.a0AfH6SMC...",
  "refresh_token": "1//04_tokenstring..."
}
```

**Response 200:**
```json
{
  "success": true,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "avatar_url": "https://lh3.googleusercontent.com/a/default-user=s96-c",
    "provider": "google",
    "created_at": "2024-01-01T00:00:00Z",
    "last_sign_in": "2024-01-01T12:00:00Z"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "expires_at": 1704067200,
    "token_type": "Bearer"
  },
  "message": "OAuth login successful"
}
```

### Get Current User

**`GET /auth/me`** 🔒

Get authenticated user profile information.

**Security:** Bearer Token Required

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe", 
  "avatar_url": "https://lh3.googleusercontent.com/a/default-user=s96-c",
  "provider": "google",
  "created_at": "2024-01-01T00:00:00Z",
  "last_sign_in": "2024-01-01T12:00:00Z"
}
```

### Refresh Token

**`POST /auth/refresh`**

Refresh expired access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 200:**
```json
{
  "success": true,
  "tokens": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "expires_at": 1704070800,
    "token_type": "Bearer"
  },
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "avatar_url": "https://lh3.googleusercontent.com/a/default-user=s96-c",
    "provider": "google",
    "created_at": "2024-01-01T00:00:00Z",
    "last_sign_in": "2024-01-01T12:00:00Z"
  }
}
```

### Logout

**`POST /auth/logout`** 🔒

Logout current user and invalidate session.

**Security:** Bearer Token Required

**Response 200:**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

### Validate Token

**`GET /auth/validate`**

Validate current authentication token (optional authentication).

**Response 200 (Valid Token):**
```json
{
  "valid": true,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "avatar_url": "https://lh3.googleusercontent.com/a/default-user=s96-c",
    "provider": "google",
    "created_at": "2024-01-01T00:00:00Z",
    "last_sign_in": "2024-01-01T12:00:00Z"
  },
  "error": null
}
```

**Response 200 (Invalid Token):**
```json
{
  "valid": false,
  "user": null,
  "error": "Invalid or expired token"
}
```

## Flight Path Endpoints

### Calculate Single Path

**`GET /api/path`** 🔒

Calculate great circle path between two airports.

**Security:** Bearer Token Required

**Parameters:**
- `departure` (query, required): Departure airport ICAO code (4 characters)
- `arrival` (query, required): Arrival airport ICAO code (4 characters)

**Response 200:**
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
        [-71.1, 42.1],
        [-69.8, 43.0],
        "...",
        [-0.461389, 51.4775]
      ],
      "total_distance_km": 5554.78,
      "total_distance_nm": 2999.12,
      "antimeridian_crossing": false
    }
  }
}
```

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/path?departure=KJFK&arrival=EGLL"
```

### Multi-Leg Route Planning

**`POST /api/route/multi-leg`** 🔒

Calculate multi-segment route with multiple airports.

**Security:** Bearer Token Required

**Request Body:**
```json
{
  "airports": ["KJFK", "EGLL", "OMDB", "NZAA"],
  "include_return": false,
  "aircraft_type": "B777",
  "preferred_altitude": 35000
}
```

**Response 200:**
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
        "path_coordinates": [
          [-73.779317, 40.639447],
          "...",
          [-0.461389, 51.4775]
        ],
        "antimeridian_crossing": false
      },
      {
        "segment_number": 2,
        "departure": "EGLL",
        "arrival": "OMDB", 
        "distance_km": 5499.64,
        "distance_nm": 2969.36,
        "estimated_duration_hours": 7.0,
        "path_coordinates": [...],
        "antimeridian_crossing": false
      },
      {
        "segment_number": 3,
        "departure": "OMDB",
        "arrival": "NZAA",
        "distance_km": 13664.00,
        "distance_nm": 7378.40,
        "estimated_duration_hours": 13.0,
        "path_coordinates": [...],
        "antimeridian_crossing": true
      }
    ]
  }
}
```

## Flight Plan Management

### List Flight Plans

**`GET /api/flightplans`** 🔒

Get user's flight plans with pagination.

**Security:** Bearer Token Required

**Parameters:**
- `limit` (query, optional): Maximum number of results (default: 50)
- `offset` (query, optional): Number of results to skip (default: 0)

**Response 200:**
```json
[
  {
    "id": "fp-550e8400-e29b-41d4-a716-446655440000",
    "title": "New York to London Business Trip",
    "description": "Regular business flight route",
    "departure_icao": "KJFK",
    "arrival_icao": "EGLL",
    "route_data": {
      "waypoints": [...],
      "estimated_duration": 480,
      "fuel_requirements": {...}
    },
    "estimated_duration": 480,
    "estimated_distance": 5554.78,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### Create Flight Plan

**`POST /api/flightplans`** 🔒

Create a new flight plan.

**Security:** Bearer Token Required

**Request Body:**
```json
{
  "title": "New York to London",
  "description": "Business trip flight plan",
  "departure_icao": "KJFK",
  "arrival_icao": "EGLL",
  "route_data": {
    "waypoints": ["KJFK", "CYQX", "EINN", "EGLL"],
    "estimated_duration": 480,
    "fuel_requirements": {
      "departure_fuel": 120000,
      "arrival_fuel": 8000,
      "reserve_fuel": 12000
    },
    "weather_conditions": {...},
    "flight_level": 350
  }
}
```

**Response 201:**
```json
{
  "id": "fp-550e8400-e29b-41d4-a716-446655440000", 
  "title": "New York to London",
  "description": "Business trip flight plan",
  "departure_icao": "KJFK",
  "arrival_icao": "EGLL",
  "route_data": {...},
  "estimated_duration": 480,
  "estimated_distance": 5554.78,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Get Flight Plan

**`GET /api/flightplans/{flight_plan_id}`** 🔒

Get specific flight plan by ID.

**Security:** Bearer Token Required

**Path Parameters:**
- `flight_plan_id` (required): Flight plan UUID

**Response 200:**
```json
{
  "id": "fp-550e8400-e29b-41d4-a716-446655440000",
  "title": "New York to London Business Trip", 
  "description": "Regular business flight route",
  "departure_icao": "KJFK",
  "arrival_icao": "EGLL",
  "route_data": {
    "waypoints": [...],
    "estimated_duration": 480,
    "fuel_requirements": {...}
  },
  "estimated_duration": 480,
  "estimated_distance": 5554.78,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Update Flight Plan

**`PUT /api/flightplans/{flight_plan_id}`** 🔒

Update existing flight plan.

**Security:** Bearer Token Required

**Path Parameters:**
- `flight_plan_id` (required): Flight plan UUID

**Request Body (partial updates allowed):**
```json
{
  "title": "Updated Flight Plan Title",
  "description": "Updated description",
  "route_data": {
    "waypoints": ["KJFK", "CYQX", "EINN", "EGKK"],
    "estimated_duration": 490
  }
}
```

**Response 200:**
```json
{
  "id": "fp-550e8400-e29b-41d4-a716-446655440000",
  "title": "Updated Flight Plan Title",
  "description": "Updated description",
  "departure_icao": "KJFK",
  "arrival_icao": "EGLL",
  "route_data": {...},
  "estimated_duration": 490,
  "estimated_distance": 5554.78,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:30:00Z"
}
```

### Delete Flight Plan

**`DELETE /api/flightplans/{flight_plan_id}`** 🔒

Delete flight plan.

**Security:** Bearer Token Required

**Path Parameters:**
- `flight_plan_id` (required): Flight plan UUID

**Response 204:**
No content (successful deletion)

### Generate Multi-ICAO Flight Plan

**`POST /api/flightplan/generate`** 🔒

Generate flight plan from multiple ICAO codes.

**Security:** Bearer Token Required

**Request Body:**
```json
{
  "title": "Around the World Flight",
  "description": "Multi-city adventure flight plan",
  "icao_codes": ["KJFK", "EGLL", "OMDB", "VTBS", "NZAA"],
  "include_return": true
}
```

**Response 201:**
```json
{
  "id": "fp-550e8400-e29b-41d4-a716-446655440000",
  "title": "Around the World Flight",
  "description": "Multi-city adventure flight plan",
  "departure_icao": "KJFK",
  "arrival_icao": "KJFK",
  "route_data": {
    "segments": [
      {
        "from": "KJFK",
        "to": "EGLL", 
        "distance_km": 5554.78,
        "estimated_duration_minutes": 480
      },
      "..."
    ],
    "total_distance_km": 41889.23,
    "total_duration_minutes": 3120,
    "airports_visited": 5
  },
  "estimated_duration": 3120,
  "estimated_distance": 41889.23,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

## Error Responses

### Authentication Errors

**401 Unauthorized:**
```json
{
  "success": false,
  "error": "Authentication token is required",
  "error_code": "MISSING_TOKEN",
  "details": {}
}
```

**401 Token Expired:**
```json
{
  "success": false,
  "error": "Authentication token has expired", 
  "error_code": "TOKEN_EXPIRED",
  "details": {}
}
```

### Validation Errors

**400 Bad Request:**
```json
{
  "detail": [
    {
      "loc": ["body", "departure_icao"],
      "msg": "ensure this value has at least 4 characters",
      "type": "value_error.any_str.min_length",
      "ctx": {"limit_value": 4}
    }
  ]
}
```

### Not Found Errors

**404 Not Found:**
```json
{
  "detail": "Flight plan not found"
}
```

### Server Errors

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Internal server error occurred",
  "error_code": "INTERNAL_ERROR",
  "details": {}
}
```

## Rate Limiting

**Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

**Rate Limit Exceeded (429):**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

## Data Models

### UserProfile
```json
{
  "id": "string (UUID)",
  "email": "string (email format)",
  "full_name": "string or null",
  "avatar_url": "string (URL) or null", 
  "provider": "string",
  "created_at": "string (ISO 8601 datetime)",
  "last_sign_in": "string (ISO 8601 datetime) or null"
}
```

### AuthTokens
```json
{
  "access_token": "string (JWT)",
  "refresh_token": "string (JWT)",
  "expires_in": "integer (seconds)",
  "expires_at": "integer (Unix timestamp)",
  "token_type": "string (default: Bearer)"
}
```

### FlightPlan
```json
{
  "id": "string (UUID)",
  "title": "string",
  "description": "string or null",
  "departure_icao": "string (4 chars)",
  "arrival_icao": "string (4 chars)",
  "route_data": "object (flexible JSON)",
  "estimated_duration": "integer (minutes) or null",
  "estimated_distance": "number (km) or null",
  "created_at": "string (ISO 8601 datetime)",
  "updated_at": "string (ISO 8601 datetime)"
}
```

### Airport
```json
{
  "icao": "string (4 chars)",
  "name": "string",
  "country": "string",
  "coordinates": ["number (longitude)", "number (latitude)"]
}
```

### RouteSegment
```json
{
  "segment_number": "integer",
  "departure": "string (ICAO)",
  "arrival": "string (ICAO)",
  "distance_km": "number",
  "distance_nm": "number",
  "estimated_duration_hours": "number",
  "path_coordinates": [["number", "number"]],
  "antimeridian_crossing": "boolean"
}
```

## SDK Examples

### JavaScript/TypeScript

```typescript
class AviFluxAPI {
  constructor(private baseUrl: string, private accessToken?: string) {}

  async authenticate(accessToken: string, refreshToken: string) {
    const response = await fetch(`${this.baseUrl}/auth/callback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ access_token: accessToken, refresh_token: refreshToken })
    });
    const data = await response.json();
    this.accessToken = data.tokens.access_token;
    return data;
  }

  async calculatePath(departure: string, arrival: string) {
    const response = await fetch(
      `${this.baseUrl}/api/path?departure=${departure}&arrival=${arrival}`,
      { headers: { Authorization: `Bearer ${this.accessToken}` }}
    );
    return response.json();
  }

  async createFlightPlan(flightPlan: any) {
    const response = await fetch(`${this.baseUrl}/api/flightplans`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.accessToken}`
      },
      body: JSON.stringify(flightPlan)
    });
    return response.json();
  }
}
```

### Python

```python
import httpx
from typing import Optional, Dict, Any

class AviFluxAPI:
    def __init__(self, base_url: str, access_token: Optional[str] = None):
        self.base_url = base_url
        self.access_token = access_token
        self.client = httpx.AsyncClient()

    async def authenticate(self, access_token: str, refresh_token: str) -> Dict[str, Any]:
        response = await self.client.post(
            f"{self.base_url}/auth/callback",
            json={"access_token": access_token, "refresh_token": refresh_token}
        )
        data = response.json()
        self.access_token = data["tokens"]["access_token"]
        return data

    async def calculate_path(self, departure: str, arrival: str) -> Dict[str, Any]:
        response = await self.client.get(
            f"{self.base_url}/api/path",
            params={"departure": departure, "arrival": arrival},
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        return response.json()

    async def create_flight_plan(self, flight_plan: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.client.post(
            f"{self.base_url}/api/flightplans",
            json=flight_plan,
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        return response.json()
```

---

**Generated from AviFlux Backend v2.0.0**  
*For complete implementation details, see: `COMPLETE_BACKEND_DOCUMENTATION.md`*