"""
Improved Great Circle Path Calculation
Fixes for accurate distance calculation and proper path visualization
"""

import pandas as pd
import numpy as np
from pyproj import Geod, Transformer
from typing import List, Tuple, Dict, Optional
import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import math

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store the filtered airports dataframe
_airports_df: Optional[pd.DataFrame] = None

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Validate environment variables
if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def load_airports_data() -> pd.DataFrame:
    """
    Load and filter airports data from Supabase.
    """
    global _airports_df
    
    if _airports_df is not None:
        logger.info("Using cached airports data")
        return _airports_df
    
    logger.info("Loading airports data from Supabase...")
    
    try:
        all_data = []
        page_size = 1000
        offset = 0
        
        while True:
            response = supabase.table('airports').select('*').range(offset, offset + page_size - 1).execute()
            
            if not response.data:
                break
            
            all_data.extend(response.data)
            logger.info(f"Loaded {len(response.data)} records (total so far: {len(all_data)})")
            
            if len(response.data) < page_size:
                break
            
            offset += page_size
        
        if not all_data:
            logger.error("No airports data found in Supabase")
            raise ValueError("No airports data found in database")
        
        df = pd.DataFrame(all_data)
        logger.info(f"Successfully loaded {len(df)} total airports from Supabase")
        
        _airports_df = df
        return df
        
    except Exception as e:
        logger.error(f"Error loading airports data from Supabase: {e}")
        raise


def find_airport_by_icao(icao_code: str) -> Optional[Dict]:
    """Find airport by ICAO code and return its details."""
    df = load_airports_data()
    
    airport = df[df['icao_code'] == icao_code.upper()]
    
    if airport.empty:
        logger.warning(f"Airport with ICAO code {icao_code} not found")
        return None
    
    airport_data = airport.iloc[0]
    return {
        'icao': airport_data['icao_code'],
        'name': airport_data['name'],
        'latitude': float(airport_data['latitude']),
        'longitude': float(airport_data['longitude']),
        'type': 'airport',
        'country': 'Unknown'
    }


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points using Haversine formula.
    More accurate than simple geodesic for validation purposes.
    
    Returns distance in meters.
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = (math.sin(dlat/2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
    
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in meters (using WGS84 mean radius)
    earth_radius = 6371008.8  # meters
    
    return c * earth_radius


def normalize_longitude(lon: float) -> float:
    """Normalize longitude to [-180, 180] range."""
    while lon > 180:
        lon -= 360
    while lon < -180:
        lon += 360
    return lon


def handle_antimeridian_crossing(lon1: float, lon2: float) -> Tuple[float, float]:
    """
    Handle antimeridian (180° meridian) crossings for shortest path.
    
    Returns adjusted longitudes for shortest great circle path.
    """
    lon1 = normalize_longitude(lon1)
    lon2 = normalize_longitude(lon2)
    
    # Check if crossing antimeridian would be shorter
    direct_diff = abs(lon2 - lon1)
    cross_diff = 360 - direct_diff
    
    if cross_diff < direct_diff:
        # Crossing is shorter, adjust one longitude
        if lon1 > lon2:
            lon2 += 360
        else:
            lon1 += 360
    
    return lon1, lon2


def calculate_great_circle_path_improved(icao1: str, icao2: str, num_points: int = 100) -> Dict:
    """
    Improved great circle path calculation with better accuracy and antimeridian handling.
    """
    # Find both airports
    airport1 = find_airport_by_icao(icao1)
    airport2 = find_airport_by_icao(icao2)
    
    if not airport1:
        raise ValueError(f"Airport {icao1} not found in database")
    if not airport2:
        raise ValueError(f"Airport {icao2} not found in database")
    
    logger.info(f"Calculating improved path from {airport1['name']} to {airport2['name']}")
    
    # Extract coordinates
    lat1, lon1 = airport1['latitude'], airport1['longitude']
    lat2, lon2 = airport2['latitude'], airport2['longitude']
    
    # Handle antimeridian crossing
    lon1_adj, lon2_adj = handle_antimeridian_crossing(lon1, lon2)
    
    # Create geodesic object using WGS84 ellipsoid
    geod = Geod(ellps='WGS84')
    
    # Calculate exact distance and bearing using geodesic
    forward_azimuth, back_azimuth, distance_meters = geod.inv(lon1, lat1, lon2, lat2)
    
    # Validate with Haversine for sanity check
    haversine_dist = haversine_distance(lat1, lon1, lat2, lon2)
    distance_diff = abs(distance_meters - haversine_dist)
    
    if distance_diff > 1000:  # More than 1km difference is suspicious
        logger.warning(f"Distance discrepancy: Geodesic={distance_meters/1000:.2f}km, "
                      f"Haversine={haversine_dist/1000:.2f}km, Diff={distance_diff/1000:.2f}km")
    
    # Generate intermediate points using adjusted coordinates for antimeridian
    if num_points > 2:
        # Use npts with adjusted coordinates
        intermediate_points = geod.npts(lon1_adj, lat1, lon2_adj, lat2, npts=num_points-2)
        
        if intermediate_points:
            path_lons = []
            path_lats = []
            
            for point in intermediate_points:
                lon, lat = point[0], point[1]
                # Normalize longitude back to [-180, 180]
                lon = normalize_longitude(lon)
                path_lons.append(lon)
                path_lats.append(lat)
        else:
            path_lons = []
            path_lats = []
    else:
        path_lons = []
        path_lats = []
    
    # Build complete path with normalized longitudes
    full_lons = [normalize_longitude(lon1)] + path_lons + [normalize_longitude(lon2)]
    full_lats = [lat1] + path_lats + [lat2]
    
    # Ensure path doesn't have unrealistic jumps (detect antimeridian crossings in path)
    cleaned_coordinates = []
    for i in range(len(full_lons)):
        lon = full_lons[i]
        lat = full_lats[i]
        
        # Check for unrealistic longitude jumps
        if i > 0:
            prev_lon = cleaned_coordinates[-1][0]
            lon_diff = abs(lon - prev_lon)
            
            # If jump is > 180°, we might need to adjust
            if lon_diff > 180:
                # Choose the longitude that keeps the path shorter
                if lon > prev_lon:
                    lon = lon - 360 if lon - 360 > -180 else lon
                else:
                    lon = lon + 360 if lon + 360 < 180 else lon
        
        cleaned_coordinates.append([lon, lat])
    
    # Extract cleaned coordinates
    final_lons = [coord[0] for coord in cleaned_coordinates]
    final_lats = [coord[1] for coord in cleaned_coordinates]
    
    # Calculate distances in different units
    distance_km = distance_meters / 1000
    distance_nm = distance_meters / 1852  # International nautical mile
    
    logger.info(f"Path calculated: {distance_km:.2f} km ({distance_nm:.2f} nm) with {len(final_lons)} points")
    
    return {
        'departure_airport': airport1,
        'arrival_airport': airport2,
        'path_coordinates': {
            'longitudes': final_lons,
            'latitudes': final_lats
        },
        'total_distance_meters': distance_meters,
        'total_distance_km': distance_km,
        'total_distance_nm': distance_nm,
        'forward_azimuth': forward_azimuth,
        'back_azimuth': back_azimuth,
        'num_points': len(final_lons),
        'haversine_distance_km': haversine_dist / 1000,  # For comparison
        'antimeridian_crossing': abs(lon2 - lon1) > 180
    }


def get_path_for_api_improved(icao1: str, icao2: str) -> Dict:
    """
    Improved main function for API calls with better error handling and validation.
    """
    try:
        path_data = calculate_great_circle_path_improved(icao1, icao2)
        
        # Create coordinates in proper [longitude, latitude] format for GeoJSON/mapping
        coordinates = list(zip(
            path_data['path_coordinates']['longitudes'],
            path_data['path_coordinates']['latitudes']
        ))
        
        # Validate coordinates are reasonable
        for i, (lon, lat) in enumerate(coordinates):
            if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                logger.warning(f"Invalid coordinate at index {i}: [{lon}, {lat}]")
        
        # Format for easier consumption by frontend
        return {
            'success': True,
            'data': {
                'departure': {
                    'icao': path_data['departure_airport']['icao'],
                    'name': path_data['departure_airport']['name'],
                    'country': path_data['departure_airport']['country'],
                    'coordinates': [
                        path_data['departure_airport']['longitude'],
                        path_data['departure_airport']['latitude']
                    ]
                },
                'arrival': {
                    'icao': path_data['arrival_airport']['icao'],
                    'name': path_data['arrival_airport']['name'],
                    'country': path_data['arrival_airport']['country'],
                    'coordinates': [
                        path_data['arrival_airport']['longitude'],
                        path_data['arrival_airport']['latitude']
                    ]
                },
                'path': {
                    'coordinates': coordinates,  # [longitude, latitude] pairs
                    'total_distance_km': round(path_data['total_distance_km'], 2),
                    'total_distance_nm': round(path_data['total_distance_nm'], 2),
                    'haversine_distance_km': round(path_data['haversine_distance_km'], 2),
                    'antimeridian_crossing': path_data['antimeridian_crossing'],
                    'total_points': path_data['num_points']
                },
                'metadata': {
                    'forward_azimuth': round(path_data['forward_azimuth'], 2),
                    'back_azimuth': round(path_data['back_azimuth'], 2),
                    'calculation_method': 'WGS84 Geodesic with Antimeridian Handling'
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating improved path: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def test_distance_accuracy():
    """Test distance accuracy against known airport pairs."""
    test_pairs = [
        ("KJFK", "KLAX", "JFK to LAX"),       # ~3944 km
        ("KJFK", "EGLL", "JFK to Heathrow"),  # ~5541 km  
        ("EGLL", "RJTT", "London to Tokyo"),  # ~9584 km
        ("KLAX", "YSSY", "LAX to Sydney"),    # ~12051 km (crosses antimeridian)
        ("KJFK", "YSSY", "JFK to Sydney"),    # ~15993 km
    ]
    
    print("🧪 Testing Distance Accuracy")
    print("=" * 50)
    
    for icao1, icao2, description in test_pairs:
        try:
            # Import original function for comparison
            from get_path import calculate_great_circle_path
            
            # Original calculation
            old_result = calculate_great_circle_path(icao1, icao2)
            # Improved calculation  
            new_result = calculate_great_circle_path_improved(icao1, icao2)
            
            old_km = old_result['total_distance_km']
            new_km = new_result['total_distance_km']
            haversine_km = new_result['haversine_distance_km']
            
            print(f"\n{description}:")
            print(f"  Original: {old_km:.2f} km")
            print(f"  Improved: {new_km:.2f} km") 
            print(f"  Haversine: {haversine_km:.2f} km")
            print(f"  Difference: {abs(old_km - new_km):.2f} km")
            print(f"  Antimeridian: {new_result['antimeridian_crossing']}")
            
        except Exception as e:
            print(f"  ❌ Error testing {description}: {e}")


if __name__ == "__main__":
    test_distance_accuracy()