#!/usr/bin/env python3
"""
Aviation API Tester for AviFlux

This script provides a comprehensive aviation data tester that can:
1. Test airport data retrieval by ICAO code
2. Display prettified aviation information
3. Validate airport codes and data integrity
4. Test multiple aviation APIs and databases

Usage:
    python aviation_api_tester.py KJFK
    python aviation_api_tester.py --interactive
"""

import os
import sys
import json
import asyncio
import argparse
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
import aiohttp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich import print as rprint

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import AviFlux modules
from get_path import load_airports_data, find_airport_by_icao
from supabase import create_client


class AviationAPITester:
    """Comprehensive aviation API testing and data display tool."""
    
    def __init__(self):
        """Initialize the aviation API tester."""
        self.console = Console()
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        # Initialize Supabase client if credentials available
        self.supabase = None
        if self.supabase_url and self.supabase_anon_key:
            self.supabase = create_client(self.supabase_url, self.supabase_anon_key)
        
        # External aviation APIs (free tiers)
        self.external_apis = {
            "aviation_stack": {
                "url": "http://api.aviationstack.com/v1/airports",
                "key": os.getenv("AVIATION_STACK_API_KEY"),
                "description": "Aviation Stack API - Airport and flight data"
            },
            "opensky": {
                "url": "https://opensky-network.org/api/metadata/airport",
                "key": None,  # Free API
                "description": "OpenSky Network - Free aviation data"
            },
            "airportapi": {
                "url": "https://www.airport-data.com/api/ap_info.json",
                "key": None,  # Free with limitations
                "description": "Airport-Data.com - Airport information"
            }
        }
    
    async def test_supabase_airport_data(self, icao_code: str) -> Optional[Dict[str, Any]]:
        """Test airport data retrieval from Supabase."""
        try:
            self.console.print(f"[yellow]🔍 Testing Supabase airport data for: {icao_code}[/yellow]")
            
            # Load airport data
            airports_df = await asyncio.to_thread(load_airports_data)
            
            if airports_df is None or airports_df.empty:
                self.console.print("[red]❌ No airport data loaded from Supabase[/red]")
                return None
            
            # Find specific airport
            airport = find_airport_by_icao(icao_code)
            
            if airport is None:
                self.console.print(f"[red]❌ Airport {icao_code} not found in Supabase data[/red]")
                return None
            
            # Convert to dict for consistent format
            airport_data = {
                "icao": airport.get("icao", "N/A"),
                "iata": airport.get("iata", "N/A"),
                "name": airport.get("name", "N/A"),
                "country": airport.get("country", "N/A"),
                "region": airport.get("region", "N/A"),
                "municipality": airport.get("municipality", "N/A"),
                "latitude": float(airport.get("latitude", 0)),
                "longitude": float(airport.get("longitude", 0)),
                "elevation_ft": airport.get("elevation_ft", "N/A"),
                "type": airport.get("type", "N/A"),
                "source": "AviFlux Supabase Database"
            }
            
            self.console.print("[green]✅ Supabase data retrieved successfully[/green]")
            return airport_data
            
        except Exception as e:
            self.console.print(f"[red]❌ Supabase test failed: {e}[/red]")
            return None
    
    async def test_aviation_stack_api(self, icao_code: str) -> Optional[Dict[str, Any]]:
        """Test Aviation Stack API."""
        try:
            api_key = self.external_apis["aviation_stack"]["key"]
            if not api_key:
                self.console.print("[yellow]⚠️ Aviation Stack API key not configured[/yellow]")
                return None
            
            self.console.print(f"[yellow]🔍 Testing Aviation Stack API for: {icao_code}[/yellow]")
            
            async with aiohttp.ClientSession() as session:
                params = {
                    "access_key": api_key,
                    "iata_code": icao_code  # Try IATA first
                }
                
                async with session.get(self.external_apis["aviation_stack"]["url"], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("data") and len(data["data"]) > 0:
                            airport = data["data"][0]
                            
                            airport_data = {
                                "icao": airport.get("icao_code", "N/A"),
                                "iata": airport.get("iata_code", "N/A"),
                                "name": airport.get("airport_name", "N/A"),
                                "country": airport.get("country_name", "N/A"),
                                "city": airport.get("city_name", "N/A"),
                                "latitude": float(airport.get("latitude", 0)),
                                "longitude": float(airport.get("longitude", 0)),
                                "timezone": airport.get("timezone", "N/A"),
                                "gmt_offset": airport.get("gmt", "N/A"),
                                "source": "Aviation Stack API"
                            }
                            
                            self.console.print("[green]✅ Aviation Stack API data retrieved[/green]")
                            return airport_data
            
            self.console.print("[red]❌ No data found in Aviation Stack API[/red]")
            return None
            
        except Exception as e:
            self.console.print(f"[red]❌ Aviation Stack API test failed: {e}[/red]")
            return None
    
    async def test_opensky_api(self, icao_code: str) -> Optional[Dict[str, Any]]:
        """Test OpenSky Network API."""
        try:
            self.console.print(f"[yellow]🔍 Testing OpenSky Network API for: {icao_code}[/yellow]")
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.external_apis['opensky']['url']}/{icao_code.upper()}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        airport_data = {
                            "icao": data.get("ICAO", "N/A"),
                            "name": data.get("Name", "N/A"),
                            "city": data.get("City", "N/A"),
                            "country": data.get("Country", "N/A"),
                            "latitude": float(data.get("Position", {}).get("latitude", 0)),
                            "longitude": float(data.get("Position", {}).get("longitude", 0)),
                            "altitude": data.get("Position", {}).get("altitude", "N/A"),
                            "source": "OpenSky Network API"
                        }
                        
                        self.console.print("[green]✅ OpenSky Network API data retrieved[/green]")
                        return airport_data
            
            self.console.print("[red]❌ No data found in OpenSky Network API[/red]")
            return None
            
        except Exception as e:
            self.console.print(f"[red]❌ OpenSky Network API test failed: {e}[/red]")
            return None
    
    def display_airport_data(self, airport_data: Dict[str, Any]):
        """Display airport data in a beautiful format."""
        if not airport_data:
            self.console.print("[red]❌ No airport data to display[/red]")
            return
        
        # Create main airport info table
        table = Table(title=f"✈️ Airport Information: {airport_data.get('icao', 'N/A')}", 
                      show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        # Add airport information
        table.add_row("ICAO Code", str(airport_data.get("icao", "N/A")))
        table.add_row("IATA Code", str(airport_data.get("iata", "N/A")))
        table.add_row("Name", str(airport_data.get("name", "N/A")))
        table.add_row("Country", str(airport_data.get("country", "N/A")))
        
        if airport_data.get("region"):
            table.add_row("Region", str(airport_data["region"]))
        if airport_data.get("municipality"):
            table.add_row("Municipality", str(airport_data["municipality"]))
        if airport_data.get("city"):
            table.add_row("City", str(airport_data["city"]))
        
        # Coordinates
        lat = airport_data.get("latitude", 0)
        lon = airport_data.get("longitude", 0)
        table.add_row("Latitude", f"{lat:.6f}°")
        table.add_row("Longitude", f"{lon:.6f}°")
        table.add_row("Coordinates", f"{lat:.6f}, {lon:.6f}")
        
        # Additional info
        if airport_data.get("elevation_ft"):
            table.add_row("Elevation", f"{airport_data['elevation_ft']} ft")
        if airport_data.get("altitude"):
            table.add_row("Altitude", f"{airport_data['altitude']} m")
        if airport_data.get("type"):
            table.add_row("Type", str(airport_data["type"]))
        if airport_data.get("timezone"):
            table.add_row("Timezone", str(airport_data["timezone"]))
        if airport_data.get("gmt_offset"):
            table.add_row("GMT Offset", str(airport_data["gmt_offset"]))
        
        table.add_row("Data Source", str(airport_data.get("source", "Unknown")))
        
        self.console.print(table)
        
        # Display coordinate visualization
        self.display_coordinate_info(lat, lon)
        
        # Display raw JSON data
        self.display_raw_json(airport_data)
    
    def display_coordinate_info(self, lat: float, lon: float):
        """Display coordinate information and hemisphere details."""
        hemisphere_ns = "North" if lat >= 0 else "South"
        hemisphere_ew = "East" if lon >= 0 else "West"
        
        # Convert to DMS (Degrees, Minutes, Seconds)
        def decimal_to_dms(decimal_deg):
            degrees = int(abs(decimal_deg))
            minutes = int((abs(decimal_deg) - degrees) * 60)
            seconds = ((abs(decimal_deg) - degrees) * 60 - minutes) * 60
            return degrees, minutes, seconds
        
        lat_deg, lat_min, lat_sec = decimal_to_dms(lat)
        lon_deg, lon_min, lon_sec = decimal_to_dms(lon)
        
        coord_table = Table(title="📍 Coordinate Details", show_header=True, header_style="bold blue")
        coord_table.add_column("Format", style="cyan")
        coord_table.add_column("Latitude", style="green")
        coord_table.add_column("Longitude", style="yellow")
        
        coord_table.add_row(
            "Decimal Degrees",
            f"{lat:.6f}°",
            f"{lon:.6f}°"
        )
        coord_table.add_row(
            "Degrees, Minutes, Seconds",
            f"{lat_deg}° {lat_min}' {lat_sec:.2f}\" {hemisphere_ns}",
            f"{lon_deg}° {lon_min}' {lon_sec:.2f}\" {hemisphere_ew}"
        )
        coord_table.add_row(
            "Hemisphere",
            hemisphere_ns,
            hemisphere_ew
        )
        
        self.console.print(coord_table)
    
    def display_raw_json(self, data: Dict[str, Any]):
        """Display raw JSON data in a formatted panel."""
        json_data = json.dumps(data, indent=2, default=str)
        panel = Panel(
            json_data,
            title="📄 Raw JSON Data",
            expand=False,
            border_style="dim"
        )
        self.console.print(panel)
    
    async def test_all_apis(self, icao_code: str) -> List[Dict[str, Any]]:
        """Test all available APIs for airport data."""
        self.console.print(Panel(
            f"[bold white]Testing all aviation APIs for airport: {icao_code.upper()}[/bold white]",
            title="🧪 Aviation API Tester",
            border_style="blue"
        ))
        
        results = []
        
        # Test Supabase (primary source)
        supabase_data = await self.test_supabase_airport_data(icao_code)
        if supabase_data:
            results.append(supabase_data)
        
        # Test external APIs
        aviation_stack_data = await self.test_aviation_stack_api(icao_code)
        if aviation_stack_data:
            results.append(aviation_stack_data)
        
        opensky_data = await self.test_opensky_api(icao_code)
        if opensky_data:
            results.append(opensky_data)
        
        return results
    
    def compare_results(self, results: List[Dict[str, Any]]):
        """Compare results from different APIs."""
        if len(results) <= 1:
            return
        
        self.console.print(Panel(
            "[bold yellow]Comparing data from multiple sources[/bold yellow]",
            title="🔍 Data Comparison",
            border_style="yellow"
        ))
        
        # Compare key fields
        comparison_table = Table(title="📊 API Comparison", show_header=True, header_style="bold magenta")
        comparison_table.add_column("Field", style="cyan")
        
        for i, result in enumerate(results):
            comparison_table.add_column(f"Source {i+1}\n({result.get('source', 'Unknown')})", style="white")
        
        # Compare common fields
        common_fields = ["icao", "iata", "name", "country", "latitude", "longitude"]
        
        for field in common_fields:
            row = [field.upper()]
            for result in results:
                value = result.get(field, "N/A")
                if isinstance(value, float):
                    value = f"{value:.6f}"
                row.append(str(value))
            comparison_table.add_row(*row)
        
        self.console.print(comparison_table)
    
    async def interactive_mode(self):
        """Run in interactive mode for testing multiple airports."""
        self.console.print(Panel(
            "[bold green]🛩️ Welcome to AviFlux Aviation API Tester![/bold green]\n\n"
            "Enter ICAO codes to test aviation APIs and retrieve airport data.\n"
            "Type 'quit' to exit, 'help' for commands.",
            title="✈️ Interactive Mode",
            border_style="green"
        ))
        
        while True:
            try:
                icao_code = Prompt.ask("\n[bold cyan]Enter ICAO code (or 'quit' to exit)[/bold cyan]")
                
                if icao_code.lower() == 'quit':
                    self.console.print("[yellow]👋 Thanks for using AviFlux Aviation API Tester![/yellow]")
                    break
                elif icao_code.lower() == 'help':
                    self.show_help()
                    continue
                elif len(icao_code) != 4:
                    self.console.print("[red]❌ ICAO codes must be exactly 4 characters[/red]")
                    continue
                
                # Test all APIs
                results = await self.test_all_apis(icao_code.upper())
                
                if results:
                    # Display first result (usually Supabase - most complete)
                    self.display_airport_data(results[0])
                    
                    # Compare if multiple results
                    if len(results) > 1:
                        self.compare_results(results)
                else:
                    self.console.print(f"[red]❌ No data found for airport code: {icao_code.upper()}[/red]")
                    self.suggest_alternatives(icao_code)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]👋 Exiting Aviation API Tester[/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]❌ Error: {e}[/red]")
    
    def show_help(self):
        """Show help information."""
        help_text = """
[bold cyan]Available Commands:[/bold cyan]
• Enter any 4-letter ICAO code (e.g., KJFK, EGLL, OMDB)
• 'quit' - Exit the application
• 'help' - Show this help message

[bold cyan]Supported APIs:[/bold cyan]
• AviFlux Supabase Database (Primary source)
• Aviation Stack API (if configured)
• OpenSky Network API (Free)

[bold cyan]Example ICAO Codes:[/bold cyan]
• KJFK - John F. Kennedy International Airport
• EGLL - London Heathrow Airport
• OMDB - Dubai International Airport
• NZAA - Auckland International Airport
• YSSY - Sydney Kingsford Smith Airport
        """
        self.console.print(Panel(help_text, title="📚 Help", border_style="blue"))
    
    def suggest_alternatives(self, icao_code: str):
        """Suggest alternative ICAO codes if not found."""
        suggestions = {
            "JFK": "KJFK",
            "LHR": "EGLL", 
            "LAX": "KLAX",
            "DXB": "OMDB",
            "SYD": "YSSY"
        }
        
        suggestion = suggestions.get(icao_code.upper())
        if suggestion:
            self.console.print(f"[yellow]💡 Did you mean: {suggestion}?[/yellow]")


async def main():
    """Main function to run the aviation API tester."""
    parser = argparse.ArgumentParser(description="AviFlux Aviation API Tester")
    parser.add_argument("icao", nargs="?", help="ICAO airport code to test")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--all-apis", "-a", action="store_true", help="Test all available APIs")
    
    args = parser.parse_args()
    
    tester = AviationAPITester()
    
    if args.interactive or not args.icao:
        await tester.interactive_mode()
    else:
        # Single airport test
        icao_code = args.icao.upper()
        
        if len(icao_code) != 4:
            tester.console.print("[red]❌ ICAO codes must be exactly 4 characters[/red]")
            return
        
        if args.all_apis:
            results = await tester.test_all_apis(icao_code)
            if results:
                tester.display_airport_data(results[0])
                if len(results) > 1:
                    tester.compare_results(results)
            else:
                tester.console.print(f"[red]❌ No data found for: {icao_code}[/red]")
        else:
            # Test primary source (Supabase)
            result = await tester.test_supabase_airport_data(icao_code)
            if result:
                tester.display_airport_data(result)
            else:
                tester.console.print(f"[red]❌ No data found for: {icao_code}[/red]")


if __name__ == "__main__":
    # Install required packages if not available
    try:
        import rich
    except ImportError:
        print("Installing required package: rich")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
        import rich
    
    asyncio.run(main())