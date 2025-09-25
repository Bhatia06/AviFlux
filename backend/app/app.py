from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging

from get_path import get_path_for_react, find_airport_by_icao


app = FastAPI(title="AviFlux API", version="0.1.0")

# Allow browser apps (React dev servers) to call this API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # CRA default
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
def read_root():
    return {"message": "AviFlux API is running"}


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok"}


@app.get("/api/greet", tags=["demo"])
def greet(name: str = "World"):
    return {"greeting": f"Hello, {name}!"}


class EchoPayload(BaseModel):
    message: str


@app.post("/api/echo", tags=["demo"])
def echo(payload: EchoPayload):
    return {"you_sent": payload.message}


# Flight path calculation endpoints
class FlightPathRequest(BaseModel):
    departure_icao: str
    arrival_icao: str
    num_points: Optional[int] = 100


@app.post("/api/flight-path", tags=["flight"])
def calculate_flight_path(request: FlightPathRequest):
    """
    Calculate great circle path between two airports using ICAO codes.
    """
    try:
        # Validate ICAO codes
        if len(request.departure_icao) != 4 or len(request.arrival_icao) != 4:
            raise HTTPException(
                status_code=400, 
                detail="ICAO codes must be exactly 4 characters long"
            )
        
        # Calculate path
        result = get_path_for_react(request.departure_icao, request.arrival_icao)
        
        if result['success']:
            return result['data']
        else:
            raise HTTPException(status_code=404, detail=result['error'])
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error calculating flight path: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/airport/{icao_code}", tags=["airport"])
def get_airport_info(icao_code: str):
    """
    Get airport information by ICAO code.
    """
    try:
        if len(icao_code) != 4:
            raise HTTPException(
                status_code=400, 
                detail="ICAO code must be exactly 4 characters long"
            )
        
        airport = find_airport_by_icao(icao_code)
        
        if not airport:
            raise HTTPException(
                status_code=404, 
                detail=f"Airport with ICAO code {icao_code} not found"
            )
        
        return airport
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching airport info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    # Run with: python app.py (from backend directory)
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

