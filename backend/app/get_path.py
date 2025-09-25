import pandas as pd
import numpy as np
from pyproj import Geod
from typing import List, Tuple, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store the filtered airports dataframe
_airports_df: Optional[pd.DataFrame] = None

AIRPORTS_CSV_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"

def load_airports_data() -> pd.DataFrame:
    """
    Load and filter airports data from CSV.
    Filters for medium_airport and large_airport types only.
    """
    global _airports_df
    
    if _airports_df is not None:
        logger.info("Using cached airports data")
        return _airports_df
    
    logger.info("Loading airports data from CSV...")
    
    try:
        # Load the full dataset
        df = pd.read_csv(AIRPORTS_CSV_URL)
        logger.info(f"Loaded {len(df)} airports from CSV")
        
        # Filter for medium_airport and large_airport types
        filtered_df = df[df['type'].isin(['medium_airport', 'large_airport'])].copy()
        logger.info(f"Filtered to {len(filtered_df)} medium and large airports")
        
        # Cache the filtered dataframe
        _airports_df = filtered_df
        
        return filtered_df
        
    except Exception as e:
        logger.error(f"Error loading airports data: {e}")
        raise


def find_airport_by_icao(icao_code: str) -> Optional[Dict]:
    """
    Find airport by ICAO code and return its details.
    
    Args:
        icao_code: 4-letter ICAO airport code
        
    Returns:
        Dictionary with airport details or None if not found
    """
    df = load_airports_data()
    
    # Filter by ICAO code (stored in 'ident' column)
    airport = df[df['ident'] == icao_code.upper()]
    
    if airport.empty:
        logger.warning(f"Airport with ICAO code {icao_code} not found")
        return None
    
    airport_data = airport.iloc[0]
    return {
        'icao': airport_data['ident'],
        'name': airport_data['name'],
        'latitude': float(airport_data['latitude_deg']),
        'longitude': float(airport_data['longitude_deg']),
        'type': airport_data['type'],
        'country': airport_data['iso_country']
    }


def calculate_great_circle_path(icao1: str, icao2: str, num_points: int = 100) -> Dict:
    """
    Calculate great circle path between two airports using their ICAO codes.
    
    Args:
        icao1: First airport ICAO code
        icao2: Second airport ICAO code  
        num_points: Number of points along the path (default: 100)
        
    Returns:
        Dictionary containing path coordinates and airport details
    """
    # Find both airports
    airport1 = find_airport_by_icao(icao1)
    airport2 = find_airport_by_icao(icao2)
    
    if not airport1:
        raise ValueError(f"Airport {icao1} not found in database")
    if not airport2:
        raise ValueError(f"Airport {icao2} not found in database")
    
    logger.info(f"Calculating path from {airport1['name']} to {airport2['name']}")
    
    # Extract coordinates
    lon1, lat1 = airport1['longitude'], airport1['latitude']
    lon2, lat2 = airport2['longitude'], airport2['latitude']
    
    # Create geodesic object (WGS84 ellipsoid)
    geod = Geod(ellps='WGS84')
    
    # Calculate great circle path
    path_lons, path_lats, back_azimuths = geod.npts(
        lon1, lat1, lon2, lat2, npts=num_points-2, initial_idx=0, terminal_idx=0
    )
    
    # Include start and end points
    full_lons = [lon1] + path_lons + [lon2]
    full_lats = [lat1] + path_lats + [lat2]
    
    # Calculate total distance and forward azimuth
    forward_azimuth, back_azimuth, distance = geod.inv(lon1, lat1, lon2, lat2)
    
    return {
        'departure_airport': airport1,
        'arrival_airport': airport2,
        'path_coordinates': {
            'longitudes': full_lons,
            'latitudes': full_lats
        },
        'total_distance_meters': distance,
        'total_distance_km': distance / 1000,
        'total_distance_nm': distance / 1852,  # nautical miles
        'forward_azimuth': forward_azimuth,
        'back_azimuth': back_azimuth,
        'num_points': len(full_lons)
    }


def get_path_for_react(icao1: str, icao2: str) -> Dict:
    """
    Main function to be called from FastAPI.
    Returns path data in format suitable for React frontend.
    """
    try:
        path_data = calculate_great_circle_path(icao1, icao2)
        
        # Format for easier consumption by React
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
                    'coordinates': list(zip(
                        path_data['path_coordinates']['longitudes'],
                        path_data['path_coordinates']['latitudes']
                    )),
                    'total_distance_km': round(path_data['total_distance_km'], 2),
                    'total_distance_nm': round(path_data['total_distance_nm'], 2)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating path: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def test_manual_input():
    """
    Test function with manual ICAO code input.
    """
    print("=== AviFlux Great Circle Path Calculator ===")
    print("Enter two ICAO airport codes to calculate the great circle path.")
    print("Example codes: KJFK (New York JFK), EGLL (London Heathrow), OMDB (Dubai)")
    print()
    
    try:
        # Get user input
        icao1 = input("Enter first airport ICAO code: ").strip().upper()
        icao2 = input("Enter second airport ICAO code: ").strip().upper()
        
        if len(icao1) != 4 or len(icao2) != 4:
            print("Error: ICAO codes must be exactly 4 characters long")
            return
        
        print(f"\nCalculating path from {icao1} to {icao2}...")
        
        # Calculate path
        result = get_path_for_react(icao1, icao2)
        
        if result['success']:
            data = result['data']
            print(f"\n✅ Path calculated successfully!")
            print(f"From: {data['departure']['name']} ({data['departure']['icao']})")
            print(f"To: {data['arrival']['name']} ({data['arrival']['icao']})")
            print(f"Distance: {data['path']['total_distance_km']} km ({data['path']['total_distance_nm']} nm)")
            print(f"Path points: {len(data['path']['coordinates'])}")
            
            # Show first few and last few coordinates
            coords = data['path']['coordinates']
            print(f"\nFirst 3 coordinates: {coords[:3]}")
            print(f"Last 3 coordinates: {coords[-3:]}")
            
        else:
            print(f"\n❌ Error: {result['error']}")
            
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    # Run the test function when script is executed directly
    test_manual_input()
