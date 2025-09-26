#!/usr/bin/env python3
"""
Test script to verify Supabase connection and data loading
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from get_path import load_airports_data, find_airport_by_icao

def test_supabase_connection():
    """Test the Supabase connection and data loading"""
    print("🔗 Testing Supabase connection...")
    
    try:
        # Test loading data
        df = load_airports_data()
        print(f"✅ Successfully loaded {len(df)} airports from Supabase")
        
        # Show data structure
        print(f"📊 Data columns: {list(df.columns)}")
        print(f"📋 First few rows:")
        print(df.head())
        
        # Test finding an airport
        print(f"\n🔍 Testing airport lookup...")
        test_codes = ['KJFK', 'EGLL', 'OMDB', 'LFPG']  # JFK, Heathrow, Dubai, CDG
        
        for code in test_codes:
            airport = find_airport_by_icao(code)
            if airport:
                print(f"✅ Found {code}: {airport['name']} ({airport['latitude']}, {airport['longitude']})")
            else:
                print(f"❌ Not found: {code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🛩️  AviFlux Supabase Connection Test")
    print("=" * 40)
    
    success = test_supabase_connection()
    
    if success:
        print(f"\n✅ All tests passed! Supabase integration is working.")
    else:
        print(f"\n❌ Tests failed. Check your configuration.")