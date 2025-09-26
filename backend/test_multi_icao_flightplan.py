#!/usr/bin/env python3
"""
Test script for Multi-ICAO Flight Plan Generation endpoint
Tests the updated /api/flightplan/generate endpoint with multiple ICAO codes
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_basic_two_airport_plan():
    """Test basic two-airport flight plan (like the old functionality)"""
    print("🧪 Testing Basic Two-Airport Flight Plan")
    print("=" * 50)
    
    test_data = {
        "icao_codes": ["KJFK", "KLAX"],
        "departure_time": "2025-09-27T10:00:00Z",
        "user_id": "test-user-123",
        "circular": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/flightplan/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Two-airport flight plan generated successfully!")
            
            overview = result['data']['overview']
            print(f"📊 Route: {' -> '.join(overview['icao_codes'])}")
            print(f"🛫 Total Distance: {overview['total_distance_km']} km ({overview['total_distance_nm']} nm)")
            print(f"⏰ Estimated Time: {overview['total_estimated_time_min']} minutes")
            print(f"🗺️ Total Legs: {overview['total_legs']}")
            
            # Show leg details
            for leg in result['data']['flight_legs']:
                print(f"  Leg {leg['leg_number']}: {leg['origin']} -> {leg['destination']} "
                      f"({leg['distance_nm']} nm, Risk: {leg['summary']['risk_index']})")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_multi_leg_flight_plan():
    """Test multi-leg flight plan with 4 airports"""
    print(f"\n🌍 Testing Multi-Leg Flight Plan (4 Airports)")
    print("=" * 50)
    
    test_data = {
        "icao_codes": ["KJFK", "EGLL", "EDDF", "RJTT"],
        "departure_time": "2025-09-27T08:00:00Z",
        "user_id": "test-user-456",
        "circular": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/flightplan/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Multi-leg flight plan generated successfully!")
            
            overview = result['data']['overview']
            print(f"📊 Route: {' -> '.join(overview['icao_codes'])}")
            print(f"🛫 Total Distance: {overview['total_distance_km']} km")
            print(f"⏰ Total Time: {overview['total_estimated_time_min']} minutes")
            print(f"🗺️ Number of Legs: {overview['total_legs']}")
            
            risks = result['data']['overall_risks']
            print(f"⚠️ Total Risks: {risks['total_risks']} (High: {risks['high_severity']}, Med: {risks['medium_severity']}, Low: {risks['low_severity']})")
            
            print(f"\n📋 Flight Legs:")
            for leg in result['data']['flight_legs']:
                print(f"  {leg['leg_number']}. {leg['origin']} -> {leg['destination']}: "
                      f"{leg['distance_km']} km, {leg['estimated_time_min']} min")
                print(f"     Risk: {leg['summary']['risk_index']}, Risks: {len(leg['risks'])}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_circular_flight_plan():
    """Test circular flight plan that returns to origin"""
    print(f"\n🔄 Testing Circular Flight Plan")
    print("=" * 50)
    
    test_data = {
        "icao_codes": ["KJFK", "KLAX", "EGLL"],
        "departure_time": "2025-09-27T06:00:00Z",
        "user_id": "test-user-789",
        "circular": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/flightplan/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Circular flight plan generated successfully!")
            
            overview = result['data']['overview']
            print(f"📊 Route: {' -> '.join(overview['icao_codes'])} (Circular: {overview['circular']})")
            print(f"🛫 Total Distance: {overview['total_distance_km']} km")
            print(f"🗺️ Number of Legs: {overview['total_legs']}")
            
            print(f"\n📋 Circular Route Legs:")
            for leg in result['data']['flight_legs']:
                print(f"  {leg['leg_number']}. {leg['origin']} -> {leg['destination']}: {leg['distance_km']} km")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_validation_errors():
    """Test validation error cases"""
    print(f"\n🛡️ Testing Validation Errors")
    print("=" * 50)
    
    # Test invalid ICAO code length
    test_cases = [
        {
            "name": "Invalid ICAO code length",
            "data": {"icao_codes": ["KJF", "KLAX"], "circular": False},
            "expected": "must be exactly 4 characters"
        },
        {
            "name": "Too few airports",
            "data": {"icao_codes": ["KJFK"], "circular": False},
            "expected": "At least 2 airports are required"
        }
    ]
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/flightplan/generate",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                print(f"✅ {test_case['name']}: Correctly rejected")
            else:
                print(f"❌ {test_case['name']}: Expected 400 but got {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test_case['name']}: Error - {e}")


def test_real_world_scenario():
    """Test a real-world multi-city trip scenario"""
    print(f"\n🌏 Testing Real-World Multi-City Trip")
    print("=" * 50)
    
    # Example: New York -> Los Angeles -> London -> Frankfurt -> Tokyo
    test_data = {
        "icao_codes": ["KJFK", "KLAX", "EGLL", "EDDF", "RJTT"],
        "departure_time": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        "user_id": "real-world-test",
        "circular": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/flightplan/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Real-world scenario successful!")
            
            overview = result['data']['overview']
            print(f"📊 World Tour: {' -> '.join(overview['icao_codes'])}")
            print(f"🛫 Total Distance: {overview['total_distance_km']:,} km ({overview['total_distance_nm']:,} nm)")
            print(f"⏰ Total Flight Time: {overview['total_estimated_time_min']/60:.1f} hours")
            print(f"🗺️ Route Coordinates: {len(result['data']['route_coordinates']['coordinates'])} points")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests for the multi-ICAO flight plan endpoint"""
    print("🛩️  Multi-ICAO Flight Plan Generation Test Suite")
    print("=" * 60)
    print("Testing the updated /api/flightplan/generate endpoint")
    print()
    
    results = []
    
    # Run all tests
    results.append(("Basic Two-Airport", test_basic_two_airport_plan()))
    results.append(("Multi-Leg (4 airports)", test_multi_leg_flight_plan()))
    results.append(("Circular Route", test_circular_flight_plan()))
    results.append(("Real-World Scenario", test_real_world_scenario()))
    
    # Test validations
    test_validation_errors()
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The multi-ICAO flight plan endpoint is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the FastAPI server and Supabase connection.")
    
    print("\nMake sure your FastAPI server is running on localhost:8000")


if __name__ == "__main__":
    main()