#!/usr/bin/env python3
"""
Test script for Flight Plans Database API endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_create_flight_plan():
    """Test creating a flight plan"""
    print("🧪 Testing Flight Plan Creation")
    print("=" * 40)
    
    # Sample data for flight plan creation
    test_data = {
        "route_details": {
            "origin": "KJFK",
            "destination": "KLAX",
            "distance_nm": 2144.5,
            "estimated_time_min": 360
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
            "route_coordinates": [
                [-73.7781, 40.6413],
                [-118.4081, 33.9425]
            ]
        },
        "chart_data": {
            "generated_at": datetime.utcnow().isoformat()
        },
        "user_id": "test-user-123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/flight-plans",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Flight plan created successfully!")
            print(f"📊 Plan ID: {result['data']['id']}")
            print(f"🛫 Route: {result['data']['summary']['origin']} -> {result['data']['summary']['destination']}")
            return result['data']['id']  # Return the ID for other tests
        else:
            print(f"❌ Failed to create flight plan: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating flight plan: {e}")
        return None


def test_get_flight_plan(plan_id):
    """Test retrieving a flight plan by ID"""
    if not plan_id:
        print("⚠️ Skipping get test - no plan ID available")
        return
    
    print(f"\n🔍 Testing Flight Plan Retrieval")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/flight-plans/{plan_id}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Flight plan retrieved successfully!")
            print(f"📊 Plan ID: {result['data']['id']}")
            print(f"🛫 Route: {result['data']['summary']['origin']} -> {result['data']['summary']['destination']}")
            print(f"🎯 Risk Level: {result['data']['summary']['risk_level']}")
        else:
            print(f"❌ Failed to retrieve flight plan: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error retrieving flight plan: {e}")


def test_get_all_flight_plans():
    """Test retrieving all flight plans"""
    print(f"\n📋 Testing All Flight Plans Retrieval")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/flight-plans?limit=10")
        
        if response.status_code == 200:
            result = response.json()
            plans = result['data']['flight_plans']
            print(f"✅ Retrieved {len(plans)} flight plans")
            
            for i, plan in enumerate(plans[:3]):  # Show first 3
                print(f"  {i+1}. {plan['summary']['origin']} -> {plan['summary']['destination']} "
                      f"(Risk: {plan['summary']['risk_level']})")
        else:
            print(f"❌ Failed to retrieve flight plans: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error retrieving flight plans: {e}")


def test_generate_and_save_flight_plan():
    """Test the combined generate and save endpoint"""
    print(f"\n🚀 Testing Generate & Save Flight Plan")
    print("=" * 40)
    
    try:
        params = {
            "origin_icao": "VIDP",
            "destination_icao": "VOBL",
            "user_id": "test-user-456",
            "departure_time": "2025-09-27T10:00:00Z"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/flight-plans/generate-and-save",
            params=params
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Flight plan generated and saved successfully!")
            
            if 'flight_plan' in result['data']:
                fp = result['data']['flight_plan']
                print(f"📊 Generated Plan ID: {fp['plan_id']}")
                
            if 'database_record' in result['data']:
                db_record = result['data']['database_record']
                print(f"💾 Database Record ID: {db_record['id']}")
                print(f"🛫 Route: {db_record['summary']['origin']} -> {db_record['summary']['destination']}")
                
        else:
            print(f"❌ Failed to generate and save: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error generating and saving: {e}")


def test_search_flight_plans():
    """Test searching flight plans"""
    print(f"\n🔍 Testing Flight Plan Search")
    print("=" * 40)
    
    search_criteria = {
        "user_id": "test-user-123",
        "date_from": "2025-09-01T00:00:00Z"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/flight-plans/search",
            json=search_criteria,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            plans = result['data']['flight_plans']
            print(f"✅ Search returned {len(plans)} flight plans")
            
            for i, plan in enumerate(plans[:2]):  # Show first 2
                print(f"  {i+1}. {plan['summary']['origin']} -> {plan['summary']['destination']} "
                      f"(User: {plan['user_id']})")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error searching: {e}")


def main():
    """Run all tests"""
    print("🛩️  Flight Plans Database API Test Suite")
    print("=" * 50)
    
    # Test creation and get the ID for other tests
    plan_id = test_create_flight_plan()
    
    # Test retrieval
    test_get_flight_plan(plan_id)
    
    # Test listing all
    test_get_all_flight_plans()
    
    # Test generate and save
    test_generate_and_save_flight_plan()
    
    # Test search
    test_search_flight_plans()
    
    print(f"\n🎉 All tests completed!")
    print("Make sure your FastAPI server is running on localhost:8000")


if __name__ == "__main__":
    main()