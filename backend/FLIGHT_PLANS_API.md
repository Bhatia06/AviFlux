# Flight Plans Database API Documentation

## Overview
The Flight Plans Database API provides comprehensive CRUD operations for managing flight plans stored in Supabase. Each flight plan contains route details, weather summaries, risk analysis, map layers, and chart data stored as JSONB columns.

## Database Schema

### Table: `flight_plans`
```sql
- id (TEXT PRIMARY KEY) - Unique flight plan identifier  
- user_id (TEXT) - User who created the flight plan
- generated_at (TIMESTAMP) - When the flight plan was generated
- created_at (TIMESTAMP DEFAULT NOW()) - Database record creation time
- route_details (JSONB) - Route information and coordinates
- weather_summary (JSONB) - Weather analysis and conditions  
- risk_analysis (JSONB) - Risk assessment and hazards
- map_layers (JSONB) - Map visualization data
- chart_data (JSONB) - Charts and analytical data
```

## API Endpoints

### 1. Create Flight Plan
**POST** `/api/flight-plans`

Create a new flight plan record in the database.

**Request Body:**
```json
{
  "route_details": {
    "origin": "KJFK",
    "destination": "KLAX", 
    "distance_nm": 2144.5,
    "estimated_time_min": 360,
    "airports": ["KJFK", "KLAX"],
    "departure_time": "2025-09-27T10:00:00Z"
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
```

**Response:**
```json
{
  "success": true,
  "message": "Flight plan created successfully",
  "data": {
    "id": "uuid-generated-id",
    "user_id": "user-123",
    "generated_at": "2025-09-26T12:00:00Z",
    "route": { /* route_details */ },
    "weather": { /* weather_summary */ },
    "risks": { /* risk_analysis */ },
    "map_data": { /* map_layers */ },
    "charts": { /* chart_data */ },
    "summary": {
      "origin": "KJFK",
      "destination": "KLAX",
      "distance": 2144.5,
      "risk_level": "low"
    }
  }
}
```

### 2. Get Flight Plan by ID
**GET** `/api/flight-plans/{plan_id}`

Retrieve a specific flight plan by its unique identifier.

**Response:** Same format as create response.

### 3. Get All Flight Plans
**GET** `/api/flight-plans?limit=50&offset=0&user_id=optional-user-id`

Retrieve flight plans with optional user filtering and pagination.

**Query Parameters:**
- `limit` (int, default: 50) - Maximum records to return
- `offset` (int, default: 0) - Records to skip for pagination  
- `user_id` (string, optional) - Filter by specific user

**Response:**
```json
{
  "success": true,
  "message": "Retrieved X flight plans",
  "data": {
    "flight_plans": [
      { /* formatted flight plan */ },
      { /* formatted flight plan */ }
    ],
    "count": 25,
    "limit": 50,
    "offset": 0
  }
}
```

### 4. Update Flight Plan  
**PUT** `/api/flight-plans/{plan_id}`

Update an existing flight plan. Only provided fields will be updated.

**Request Body:** Partial flight plan data (same structure as create)

### 5. Delete Flight Plan
**DELETE** `/api/flight-plans/{plan_id}`

Delete a flight plan by ID.

**Response:**
```json
{
  "success": true,
  "message": "Flight plan deleted successfully", 
  "data": {
    "deleted_id": "plan-id"
  }
}
```

### 6. Search Flight Plans
**POST** `/api/flight-plans/search`

Search flight plans with advanced criteria.

**Request Body:**
```json
{
  "user_id": "user-123",
  "date_from": "2025-09-01T00:00:00Z",
  "date_to": "2025-09-30T23:59:59Z",
  "limit": 20,
  "offset": 0
}
```

### 7. Generate and Save Flight Plan
**POST** `/api/flight-plans/generate-and-save`

Generate a complete flight plan using the existing flight plan service and automatically save it to the database.

**Query Parameters:**
- `origin_icao` (string) - Origin airport ICAO code
- `destination_icao` (string) - Destination airport ICAO code  
- `user_id` (string, optional) - User identifier
- `departure_time` (string, optional) - ISO datetime string

**Response:**
```json
{
  "success": true,
  "message": "Flight plan generated and saved successfully",
  "data": {
    "flight_plan": { /* complete generated flight plan */ },
    "database_record": { /* formatted database record */ }
  }
}
```

## Data Format for Frontend

The API automatically formats data for frontend consumption:

```json
{
  "id": "flight-plan-uuid",
  "user_id": "user-123", 
  "generated_at": "2025-09-26T12:00:00Z",
  "created_at": "2025-09-26T12:01:00Z",
  "route": { /* route details */ },
  "weather": { /* weather summary */ },
  "risks": { /* risk analysis */ },
  "map_data": { /* map layers */ },
  "charts": { /* chart data */ },
  "summary": {
    "origin": "KJFK",
    "destination": "KLAX", 
    "distance": 2144.5,
    "risk_level": "low"
  }
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

HTTP Status Codes:
- `200` - Success
- `400` - Bad Request (validation errors)  
- `404` - Not Found (flight plan doesn't exist)
- `500` - Internal Server Error

## Testing

Run the test suite:
```bash
python test_flight_plans_api.py
```

This will test all endpoints and provide example usage.

## Integration with Existing Services

The flight plans database integrates with:
- **AirportDatabase** - For airport data and coordinates
- **FlightPlanService** - For generating complete flight plans
- **RouteService** - For route calculations
- **Supabase** - For data persistence

## Frontend Usage Examples

### Create a Simple Flight Plan
```javascript
const response = await fetch('/api/flight-plans', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    route_details: { origin: 'KJFK', destination: 'KLAX' },
    weather_summary: { risk_index: 'green' },
    risk_analysis: { overall_risk: 'low' },
    map_layers: {},
    chart_data: {},
    user_id: 'current-user-id'
  })
});
```

### Get User's Flight Plans  
```javascript
const response = await fetch('/api/flight-plans?user_id=current-user-id&limit=10');
const data = await response.json();
const flightPlans = data.data.flight_plans;
```

### Generate Complete Flight Plan
```javascript
const response = await fetch(
  '/api/flight-plans/generate-and-save?origin_icao=KJFK&destination_icao=KLAX&user_id=current-user-id',
  { method: 'POST' }
);
```