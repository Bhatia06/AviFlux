#!/usr/bin/env python3
"""
Test script for multi-leg route endpoint with new frontend format
"""

import requests
import json
from datetime import datetime

def test_multi_leg_route():
    """Test the multi-leg route endpoint with the new format"""
    
    # Test data matching your frontend format
    test_data = {
        "icao_codes": [
            "KJFK",
            "KLAX", 
            "EGLL",
            "EDDF",
            "RJTT"
        ],
        "request_date": "2025-09-26T12:00:00Z",
        "circular": False
    }
    
    print("🧪 Testing Multi-Leg Route Endpoint")
    print("=" * 40)
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    print()
    
    try:
        # Make request to the endpoint
        response = requests.post(
            "http://localhost:8000/api/flightpath/summary/route",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            print(f"📊 Total Distance: {result['total_distance_km']} km ({result['total_distance_nm']} nm)")
            print(f"🛫 Route: {' -> '.join(result['icao_codes'])}")
            print(f"📅 Request Date: {result['request_date']}")
            print(f"🔄 Circular: {result['circular']}")
            print(f"📍 Total Points: {result['total_points']}")
            print(f"🗺️ Segments: {len(result['segments'])}")
            
            print("\n📋 Segment Details:")
            for i, segment in enumerate(result['segments'], 1):
                print(f"  {i}. {segment['origin']} -> {segment['destination']}: "
                      f"{segment['distance_km']} km ({segment['distance_nm']} nm)")
                      
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the FastAPI server is running on localhost:8000")
        print("Start the server with: python main.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_circular_route():
    """Test with circular route enabled"""
    
    test_data = {
        "icao_codes": ["KJFK", "KLAX", "EGLL"],
        "request_date": "2025-09-26T12:00:00Z",
        "circular": True
    }
    
    print("\n🔄 Testing Circular Route")
    print("=" * 40)
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/flightpath/summary/route",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Circular route test successful!")
            print(f"🛫 Route: {' -> '.join(result['icao_codes'])} -> {result['icao_codes'][0]}")
            print(f"📊 Total Distance: {result['total_distance_km']} km")
            print(f"🗺️ Segments: {len(result['segments'])}")
        else:
            print(f"❌ Circular route test failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error in circular route test: {e}")

if __name__ == "__main__":
    test_multi_leg_route()
    test_circular_route()