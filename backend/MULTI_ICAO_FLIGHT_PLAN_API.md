# Multi-ICAO Flight Plan Generation API

## Updated Endpoint: POST `/api/flightplan/generate`

The flight plan generation endpoint has been updated to accept multiple ICAO codes instead of just origin and destination.

## Request Format

### New Multi-ICAO Request
```json
{
  "icao_codes": ["KJFK", "KLAX", "EGLL", "EDDF", "RJTT"],
  "departure_time": "2025-09-27T10:00:00Z",
  "user_id": "user-123",
  "circular": false
}
```

### Request Fields
- **`icao_codes`** (required): Array of ICAO airport codes (minimum 2)
- **`departure_time`** (optional): ISO datetime string for departure
- **`user_id`** (optional): User identifier
- **`circular`** (optional, default: false): If true, adds return leg to first airport

## Response Format

```json
{
  "success": true,
  "message": "Multi-leg flight plan generated successfully for 4 leg(s)",
  "data": {
    "overview": {
      "icao_codes": ["KJFK", "KLAX", "EGLL", "EDDF", "RJTT"],
      "circular": false,
      "total_legs": 4,
      "total_distance_km": 21567.89,
      "total_distance_nm": 11642.15,
      "total_estimated_time_min": 1440,
      "departure_time": "2025-09-27T10:00:00Z",
      "user_id": "user-123"
    },
    "route_coordinates": {
      "coordinates": [[lng, lat], [lng, lat], ...],
      "total_points": 400
    },
    "flight_legs": [
      {
        "leg_number": 1,
        "origin": "KJFK",
        "destination": "KLAX",
        "distance_km": 3944.42,
        "distance_nm": 2129.92,
        "estimated_time_min": 360,
        "summary": {
          "text": ["Clear skies expected", "Light winds"],
          "risk_index": "green"
        },
        "risks": [
          {
            "type": "weather",
            "subtype": "wind",
            "location": "KJFK",
            "severity": "low",
            "description": "Light crosswinds expected"
          }
        ]
      }
      // ... additional legs
    ],
    "overall_risks": {
      "total_risks": 5,
      "high_severity": 0,
      "medium_severity": 2,
      "low_severity": 3,
      "risk_summary": ["weather", "airspace"]
    }
  }
}
```

## Use Cases

### 1. Simple Two-Airport Flight
```json
{
  "icao_codes": ["KJFK", "KLAX"],
  "departure_time": "2025-09-27T10:00:00Z"
}
```

### 2. Multi-City Tour
```json
{
  "icao_codes": ["KJFK", "EGLL", "EDDF", "RJTT"],
  "user_id": "world-traveler",
  "circular": false
}
```

### 3. Circular Route (Round Trip)
```json
{
  "icao_codes": ["KJFK", "KLAX", "EGLL"],
  "circular": true,
  "departure_time": "2025-09-27T08:00:00Z"
}
```

## Features

### ✅ **Multi-Leg Support**
- Handle 2 to unlimited airports in sequence
- Each leg gets individual flight plan analysis
- Comprehensive route calculations

### ✅ **Circular Routes**
- Automatic return leg to origin airport
- Complete round-trip planning

### ✅ **Comprehensive Analysis**
- Individual leg weather and risk analysis
- Overall trip summary and statistics
- Route coordinate data for mapping

### ✅ **Risk Assessment**
- Per-leg risk analysis
- Overall trip risk summary
- Risk categorization (high/medium/low)

### ✅ **Distance & Time Calculations**
- Total trip distance (km and nautical miles)
- Estimated flight time for each leg
- Total trip time estimation

## Backwards Compatibility

For simple two-airport flights, we've also provided:
- **POST** `/api/flightplan/generate-simple` - Uses the original FlightPlanRequest format

## Validation Rules

1. **ICAO Codes**: Must be exactly 4 characters each
2. **Minimum Airports**: At least 2 airports required
3. **Circular Logic**: Only applies when more than 2 airports provided
4. **DateTime Format**: ISO 8601 format with timezone (Z suffix)

## Error Responses

### 400 Bad Request
```json
{
  "detail": "ICAO code 'JFK' must be exactly 4 characters long"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: [specific error message]"
}
```

## Frontend Integration Examples

### React/JavaScript
```javascript
const generateMultiLegPlan = async (airports) => {
  const response = await fetch('/api/flightplan/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      icao_codes: airports,
      departure_time: new Date().toISOString(),
      user_id: getCurrentUserId(),
      circular: false
    })
  });
  
  const result = await response.json();
  return result.data;
};

// Usage
const flightPlan = await generateMultiLegPlan(['KJFK', 'KLAX', 'EGLL']);
```

### Python
```python
import requests

def generate_flight_plan(icao_codes, circular=False):
    response = requests.post('http://localhost:8000/api/flightplan/generate', 
        json={
            'icao_codes': icao_codes,
            'circular': circular,
            'departure_time': '2025-09-27T10:00:00Z'
        }
    )
    return response.json()

# Usage
plan = generate_flight_plan(['KJFK', 'KLAX', 'EGLL', 'EDDF'])
```

## Testing

Run comprehensive tests:
```bash
python test_multi_icao_flightplan.py
```

The test suite covers:
- Basic two-airport plans
- Multi-leg routes
- Circular routes  
- Real-world scenarios
- Validation error cases

## Migration from Old Endpoint

**Old Format (deprecated):**
```json
{
  "origin_icao": "KJFK",
  "destination_icao": "KLAX",
  "departure_time": "2025-09-27T10:00:00Z"
}
```

**New Format:**
```json
{
  "icao_codes": ["KJFK", "KLAX"],
  "departure_time": "2025-09-27T10:00:00Z"
}
```

The new format provides much more flexibility and supports complex multi-leg routing while maintaining backwards compatibility through the simple endpoint.