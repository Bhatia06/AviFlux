#!/usr/bin/env python3
"""
Aviation Weather API Tester
Tests aviationweather.gov API endpoints and displays comprehensive weather data
in prettified JSON format for any ICAO airport code.

Usage:
    python weather_api_tester.py
    Enter ICAO code when prompted (e.g., KJFK, EGLL, OMDB)
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

class AviationWeatherTester:
    def __init__(self):
        self.base_url = "https://aviationweather.gov/api/data"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AviFlux-Weather-Tester/1.0',
            'Accept': 'application/json'
        })
    
    def get_metar_data(self, icao_code: str) -> Optional[Dict]:
        """Fetch METAR data for airport"""
        try:
            url = f"{self.base_url}/metar"
            params = {
                'ids': icao_code,
                'format': 'json',
                'taf': 'false',
                'hours': '3'  # Last 3 hours of METAR data
            }
            
            print(f"🌤️  Fetching METAR data for {icao_code}...")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data if data else None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ METAR fetch error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ METAR JSON decode error: {e}")
            return None
    
    def get_taf_data(self, icao_code: str) -> Optional[Dict]:
        """Fetch TAF data for airport"""
        try:
            url = f"{self.base_url}/taf"
            params = {
                'ids': icao_code,
                'format': 'json',
                'hours': '30'  # Next 30 hours of TAF data
            }
            
            print(f"🔮 Fetching TAF data for {icao_code}...")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data if data else None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ TAF fetch error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ TAF JSON decode error: {e}")
            return None
    
    def get_pirep_data(self, icao_code: str) -> Optional[Dict]:
        """Fetch PIREP data around airport"""
        try:
            url = f"{self.base_url}/pirep"
            params = {
                'bbox': self._get_bbox_for_airport(icao_code),
                'format': 'json',
                'hours': '6'  # Last 6 hours of PIREPs
            }
            
            print(f"✈️  Fetching PIREP data around {icao_code}...")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data if data else None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ PIREP fetch error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ PIREP JSON decode error: {e}")
            return None
    
    def get_sigmet_data(self, icao_code: str) -> Optional[Dict]:
        """Fetch SIGMET data around airport"""
        try:
            url = f"{self.base_url}/sigmet"
            params = {
                'bbox': self._get_bbox_for_airport(icao_code),
                'format': 'json',
                'hazards': 'convective,turbulence,icing,ifr,mountain_obscuration,volcanic_ash,dust_sand'
            }
            
            print(f"⚠️  Fetching SIGMET data around {icao_code}...")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data if data else None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ SIGMET fetch error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ SIGMET JSON decode error: {e}")
            return None
    
    def get_airmet_data(self, icao_code: str) -> Optional[Dict]:
        """Fetch AIRMET data around airport"""
        try:
            url = f"{self.base_url}/airmet"
            params = {
                'bbox': self._get_bbox_for_airport(icao_code),
                'format': 'json'
            }
            
            print(f"🌪️  Fetching AIRMET data around {icao_code}...")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data if data else None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ AIRMET fetch error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ AIRMET JSON decode error: {e}")
            return None
    
    def _get_bbox_for_airport(self, icao_code: str) -> str:
        """Get bounding box around airport for PIREP/SIGMET queries"""
        # This is a simplified approach - in production, you'd use actual airport coordinates
        # Common airport coordinates (you can expand this)
        airport_coords = {
            'KJFK': (40.6413, -73.7781),  # JFK New York
            'KLAX': (33.9425, -118.4081), # LAX Los Angeles
            'EGLL': (51.4700, -0.4543),   # Heathrow London
            'OMDB': (25.2532, 55.3657),   # Dubai
            'LFPG': (49.0097, 2.5479),    # Charles de Gaulle Paris
            'EDDF': (50.0264, 8.5431),    # Frankfurt
            'RJTT': (35.5494, 139.7798),  # Narita Tokyo
            'YSSY': (-33.9399, 151.1753), # Sydney
            'CYYZ': (43.6777, -79.6248),  # Toronto Pearson
            'ZBAA': (40.0725, 116.5974)   # Beijing Capital
        }
        
        if icao_code in airport_coords:
            lat, lon = airport_coords[icao_code]
        else:
            # Default to a central US location if airport not in our list
            lat, lon = 39.8283, -98.5795  # Geographic center of US
        
        # Create 50nm radius bounding box
        delta = 0.75  # Approximately 50nm in degrees
        return f"{lat-delta},{lon-delta},{lat+delta},{lon+delta}"
    
    def format_weather_summary(self, icao_code: str, weather_data: Dict) -> Dict:
        """Create a comprehensive weather summary"""
        summary = {
            "airport_code": icao_code,
            "query_timestamp": datetime.now().isoformat(),
            "data_sources": []
        }
        
        # Process METAR data
        if weather_data.get('metar') and len(weather_data['metar']) > 0:
            latest_metar = weather_data['metar'][0]
            summary['current_weather'] = {
                "source": "METAR",
                "observation_time": latest_metar.get('obsTime'),
                "raw_metar": latest_metar.get('rawOb'),
                "flight_category": latest_metar.get('fltcat'),
                "temperature_celsius": latest_metar.get('temp'),
                "dewpoint_celsius": latest_metar.get('dewp'),
                "wind_direction": latest_metar.get('wdir'),
                "wind_speed_knots": latest_metar.get('wspd'),
                "wind_gust_knots": latest_metar.get('wgst'),
                "visibility_miles": latest_metar.get('visib'),
                "altimeter_inhg": latest_metar.get('altim'),
                "sea_level_pressure_mb": latest_metar.get('slp'),
                "weather_conditions": latest_metar.get('wxString'),
                "sky_conditions": latest_metar.get('clds'),
                "remarks": latest_metar.get('rmk')
            }
            summary['data_sources'].append("METAR")
        
        # Process TAF data
        if weather_data.get('taf') and len(weather_data['taf']) > 0:
            latest_taf = weather_data['taf'][0]
            summary['forecast'] = {
                "source": "TAF",
                "issue_time": latest_taf.get('issueTime'),
                "bulletin_time": latest_taf.get('bulletinTime'),
                "valid_time_from": latest_taf.get('validTimeFrom'),
                "valid_time_to": latest_taf.get('validTimeTo'),
                "raw_taf": latest_taf.get('rawTAF'),
                "forecast_periods": latest_taf.get('fcsts', [])
            }
            summary['data_sources'].append("TAF")
        
        # Process PIREP data
        if weather_data.get('pirep') and len(weather_data['pirep']) > 0:
            summary['pilot_reports'] = {
                "source": "PIREP",
                "report_count": len(weather_data['pirep']),
                "reports": []
            }
            
            for pirep in weather_data['pirep'][:10]:  # Limit to 10 most recent
                summary['pilot_reports']['reports'].append({
                    "observation_time": pirep.get('obsTime'),
                    "aircraft_type": pirep.get('acType'),
                    "flight_level": pirep.get('fltlvl'),
                    "turbulence": pirep.get('turb'),
                    "icing": pirep.get('ice'),
                    "visibility": pirep.get('vis'),
                    "temperature": pirep.get('tmp'),
                    "wind": pirep.get('wnd'),
                    "location": pirep.get('location'),
                    "raw_pirep": pirep.get('rawOb')
                })
            summary['data_sources'].append("PIREP")
        
        # Process SIGMET data
        if weather_data.get('sigmet') and len(weather_data['sigmet']) > 0:
            summary['significant_weather'] = {
                "source": "SIGMET",
                "warning_count": len(weather_data['sigmet']),
                "warnings": []
            }
            
            for sigmet in weather_data['sigmet']:
                summary['significant_weather']['warnings'].append({
                    "hazard": sigmet.get('hazard'),
                    "severity": sigmet.get('severity'),
                    "type": sigmet.get('sigmetType'),
                    "valid_time_from": sigmet.get('validTimeFrom'),
                    "valid_time_to": sigmet.get('validTimeTo'),
                    "altitude_range": {
                        "top": sigmet.get('altitudeHi1'),
                        "bottom": sigmet.get('altitudeLo1')
                    },
                    "raw_sigmet": sigmet.get('rawSigmet')
                })
            summary['data_sources'].append("SIGMET")
        
        # Process AIRMET data
        if weather_data.get('airmet') and len(weather_data['airmet']) > 0:
            summary['airmen_meteorological_info'] = {
                "source": "AIRMET",
                "advisory_count": len(weather_data['airmet']),
                "advisories": []
            }
            
            for airmet in weather_data['airmet']:
                summary['airmen_meteorological_info']['advisories'].append({
                    "hazard": airmet.get('hazard'),
                    "severity": airmet.get('severity'),
                    "valid_time_from": airmet.get('validTimeFrom'),
                    "valid_time_to": airmet.get('validTimeTo'),
                    "raw_airmet": airmet.get('rawAirmet')
                })
            summary['data_sources'].append("AIRMET")
        
        return summary
    
    def test_airport_weather(self, icao_code: str) -> Dict:
        """Comprehensive weather test for an airport"""
        icao_code = icao_code.upper().strip()
        
        if len(icao_code) != 4:
            raise ValueError("ICAO code must be exactly 4 characters")
        
        print(f"\n{'='*60}")
        print(f"🛩️  TESTING AVIATION WEATHER FOR {icao_code}")
        print(f"{'='*60}")
        
        # Collect all weather data
        weather_data = {}
        
        # Fetch METAR
        metar_data = self.get_metar_data(icao_code)
        if metar_data:
            weather_data['metar'] = metar_data
            print(f"✅ METAR: {len(metar_data)} records")
        else:
            print("❌ METAR: No data")
        
        # Fetch TAF
        taf_data = self.get_taf_data(icao_code)
        if taf_data:
            weather_data['taf'] = taf_data
            print(f"✅ TAF: {len(taf_data)} records")
        else:
            print("❌ TAF: No data")
        
        # Fetch PIREP
        pirep_data = self.get_pirep_data(icao_code)
        if pirep_data:
            weather_data['pirep'] = pirep_data
            print(f"✅ PIREP: {len(pirep_data)} records")
        else:
            print("❌ PIREP: No data")
        
        # Fetch SIGMET
        sigmet_data = self.get_sigmet_data(icao_code)
        if sigmet_data:
            weather_data['sigmet'] = sigmet_data
            print(f"✅ SIGMET: {len(sigmet_data)} records")
        else:
            print("❌ SIGMET: No data")
        
        # Fetch AIRMET
        airmet_data = self.get_airmet_data(icao_code)
        if airmet_data:
            weather_data['airmet'] = airmet_data
            print(f"✅ AIRMET: {len(airmet_data)} records")
        else:
            print("❌ AIRMET: No data")
        
        # Format comprehensive summary
        weather_summary = self.format_weather_summary(icao_code, weather_data)
        
        print(f"\n{'='*60}")
        print(f"📊 WEATHER SUMMARY GENERATED")
        print(f"Data sources: {', '.join(weather_summary['data_sources'])}")
        print(f"{'='*60}")
        
        return weather_summary

def main():
    """Main interactive function"""
    tester = AviationWeatherTester()
    
    print("🌤️  Aviation Weather API Tester")
    print("Fetches comprehensive weather data from aviationweather.gov")
    print("-" * 60)
    
    while True:
        try:
            # Get ICAO code from user
            icao_code = input("\n✈️  Enter ICAO airport code (or 'quit' to exit): ").strip()
            
            if icao_code.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not icao_code:
                continue
            
            # Test the weather API
            weather_data = tester.test_airport_weather(icao_code)
            
            # Pretty print the results
            print(f"\n{'='*60}")
            print(f"🎯 PRETTIFIED JSON OUTPUT FOR {icao_code}")
            print(f"{'='*60}")
            
            print(json.dumps(weather_data, indent=2, ensure_ascii=False, default=str))
            
            # Ask if user wants to save to file
            save = input(f"\n💾 Save results to file? (y/n): ").strip().lower()
            if save in ['y', 'yes']:
                filename = f"weather_{icao_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                try:
                    with open(filename, 'w') as f:
                        json.dump(weather_data, f, indent=2, ensure_ascii=False, default=str)
                    print(f"✅ Results saved to {filename}")
                except Exception as e:
                    print(f"❌ Error saving file: {e}")
        
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()