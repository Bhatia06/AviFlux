# AviFlux Backend - Quick Reference Guide

**Version 2.0.0 - September 27, 2025**

## 🚀 Quick Start

```bash
# Setup
git clone https://github.com/Bhatia06/AviFlux.git
cd AviFlux/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Edit .env with your Supabase credentials

# Run
python main.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## 📋 System Overview

**AviFlux** is a comprehensive aviation flight planning system with:
- ✅ **OAuth Authentication** (Google via Supabase)
- ✅ **Great Circle Path Calculations** (±8km accuracy) 
- ✅ **Multi-leg Route Planning** 
- ✅ **Flight Plan Management** (CRUD operations)
- ✅ **Real-time Database** (Supabase/PostgreSQL)
- ✅ **Antimeridian Crossing Support**

## 🔧 Core Components

### 1. Authentication System
```python
# Protected endpoint example
@app.get("/protected")
async def protected_endpoint(user: UserProfile = Depends(get_current_user)):
    return {"message": f"Hello {user.full_name}!"}

# Optional authentication
@app.get("/public") 
async def public_endpoint(user: Optional[UserProfile] = Depends(get_optional_user)):
    if user:
        return {"authenticated": True, "user": user.email}
    return {"authenticated": False}
```

### 2. Flight Path Calculation
```python
# Calculate great circle path
result = calculate_great_circle_path("KJFK", "EGLL")
# Returns: coordinates, distances, bearings, antimeridian handling
```

### 3. Database Operations
```python
# Flight plan CRUD
flight_plan = await flight_plans_service.create_flight_plan(
    user_id="user-123",
    title="NYC to London", 
    departure_icao="KJFK",
    arrival_icao="EGLL",
    route_data={...}
)
```

## 🛡️ Authentication Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/oauth-url` | GET | Generate Google OAuth URL |
| `/auth/callback` | POST | Handle OAuth callback |
| `/auth/me` | GET | Get user profile |
| `/auth/refresh` | POST | Refresh access token |
| `/auth/logout` | POST | Logout user |
| `/auth/validate` | GET | Validate token |

## ✈️ Flight Planning Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/path` | GET | Single path calculation |
| `/api/route/multi-leg` | POST | Multi-leg route planning |
| `/api/flightplans` | GET/POST | List/Create flight plans |
| `/api/flightplans/{id}` | PUT/DELETE | Update/Delete flight plan |
| `/api/flightplan/generate` | POST | Multi-ICAO flight plan |

## 📊 Key Data Models

### UserProfile
```python
{
    "id": "user-uuid",
    "email": "user@example.com", 
    "full_name": "John Doe",
    "avatar_url": "https://...",
    "provider": "google",
    "created_at": "2024-01-01T00:00:00Z"
}
```

### Path Calculation Response
```python
{
    "success": true,
    "data": {
        "departure": {"icao": "KJFK", "name": "...", "coordinates": [...]},
        "arrival": {"icao": "EGLL", "name": "...", "coordinates": [...]},
        "path": {
            "coordinates": [[lon, lat], ...],
            "total_distance_km": 5554.78,
            "antimeridian_crossing": false
        }
    }
}
```

### Flight Plan
```python
{
    "id": "plan-uuid",
    "title": "NYC to London",
    "departure_icao": "KJFK", 
    "arrival_icao": "EGLL",
    "route_data": {...},
    "created_at": "2024-01-01T00:00:00Z"
}
```

## 🔧 Configuration

### Required Environment Variables
```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Dependencies Highlights
```txt
fastapi>=0.104.0          # Web framework
supabase>=2.0.0           # Database & Auth
pyproj>=3.4.0             # Geodesic calculations  
pydantic>=2.5.0           # Data validation
PyJWT>=2.8.0              # JWT tokens
pandas>=2.0.0             # Data processing
```

## 🧪 Testing

```bash
# Run individual tests
python test_auth.py              # Authentication tests
python test_flight_plans_api.py  # Flight plan tests  
python test_endpoints.py         # Path calculation tests

# OAuth testing
python login_script.py           # Interactive OAuth testing
```

## 🐛 Common Issues & Solutions

### Authentication Issues
```bash
# Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('URL:', os.getenv('SUPABASE_URL'))"

# Test OAuth URL generation  
curl "http://localhost:8000/auth/oauth-url?provider=google"
```

### Path Calculation Issues
```bash
# Test basic path calculation
curl "http://localhost:8000/api/path?departure=KJFK&arrival=EGLL"

# Check airport data loading
python -c "from get_path import _airports_df; print(f'Loaded {len(_airports_df)} airports' if _airports_df is not None else 'No data')"
```

### Database Issues
```bash
# Test Supabase connection
python -c "from services.flight_plans_service import flight_plans_service; print('DB connected')"
```

## 📈 Recent Improvements (Sept 2025)

### ✨ Major Features Added
- **Complete OAuth System**: Google authentication via Supabase
- **Enhanced Path Calculations**: Improved from ~600km to <8km accuracy  
- **Antimeridian Support**: Proper handling of trans-oceanic routes
- **Flight Plan CRUD**: Full database operations with user isolation
- **Multi-leg Planning**: Complex route planning with multiple stops

### 🔧 Technical Improvements
- JWT token management with refresh
- Protected endpoint middleware
- Dual coordinate systems for visualization
- Haversine distance validation
- Asynchronous database operations
- Comprehensive error handling

## 📝 File Structure Quick Reference

```
backend/
├── main.py                    # FastAPI app entry point
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── models/
│   ├── auth_models.py        # Authentication models
│   ├── flight_models.py      # Flight plan models  
│   └── dtos.py              # Data transfer objects
├── services/
│   ├── auth_service.py       # Authentication logic
│   ├── flight_plans_service.py # Flight plan CRUD
│   └── route_service.py      # Route calculations
├── routes/
│   └── auth_routes.py        # Authentication endpoints
├── middleware/
│   └── auth_middleware.py    # JWT validation
├── get_path.py               # Path calculations
├── improved_path_service.py  # Enhanced calculations
└── test_*.py                 # Test suites
```

## 🚀 Deployment Ready

### Development
```bash
python main.py
```

### Production  
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📞 Support

- **Repository**: https://github.com/Bhatia06/AviFlux
- **Full Documentation**: `COMPLETE_BACKEND_DOCUMENTATION.md`
- **Issues**: GitHub Issues for bug reports
- **API Docs**: http://localhost:8000/docs (when running)

**🎯 Ready to fly with AviFlux!** ✈️