#!/usr/bin/env python3
"""
Compact endpoint tester for AviFlux backend.
Runs common GET and POST endpoints and prints key values.

Usage:
  cd backend
  python test_endpoints.py
"""

import asyncio
from datetime import datetime
import httpx

BASE_URL = "http://localhost:8000"
ORIGIN = "KJFK"
DEST = "KSFO"
MULTI_AIRPORTS = ["KJFK", "VAPO", "KDEN", "KSFO"]


async def run_tests():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=== AviFlux API quick test ===")

        # 1) Root
        r = await client.get(f"{BASE_URL}/")
        print(f"/ -> {r.status_code} {r.json() if r.headers.get('content-type','').startswith('application/json') else ''}")

        # 2) Health
        r = await client.get(f"{BASE_URL}/api/health")
        health = r.json()
        print(f"/api/health -> {r.status_code}; airports_loaded={health.get('airports_loaded')}")

        # 3) GET flight path summary (two-airport)
        r = await client.get(f"{BASE_URL}/api/flightpath/summary/{ORIGIN}/{DEST}")
        if r.status_code == 200:
            data = r.json()
            print(f"summary {ORIGIN}->{DEST}: distance_km={data['distance_km']}, points={data['path_points_total']}")
        else:
            print(f"summary {ORIGIN}->{DEST}: HTTP {r.status_code} -> {r.text}")

        # 4) GET path (get_path.py formatted)
        r = await client.get(f"{BASE_URL}/api/path/{ORIGIN}/{DEST}")
        if r.status_code == 200:
            data = r.json()
            if data.get('success'):
                path = data['data']['path']
                dep = data['data']['departure']
                arr = data['data']['arrival']
                print(f"get_path {dep['icao']}->{arr['icao']}: {path['total_distance_nm']} nm, coords={len(path['coordinates'])}")
            else:
                print(f"get_path error: {data.get('error')}")
        else:
            print(f"get_path HTTP {r.status_code}: {r.text}")

        # 5) POST flight plan generate (2 inputs)
        payload = {
            "origin_icao": ORIGIN,
            "destination_icao": DEST,
            "departure_time": datetime.utcnow().isoformat() + "Z",
        }
        r = await client.post(f"{BASE_URL}/api/flightplan/generate", json=payload)
        if r.status_code == 200:
            data = r.json()
            if data.get('success') and data.get('data'):
                fp = data['data']
                route_str = "->".join(fp['route']['airports'])
                print(
                    f"flightplan id={fp['plan_id']} route={route_str} "
                    f"dist_nm={fp['route']['distance_nm']} time_min={fp['route']['estimated_time_min']} "
                    f"risk={fp['summary']['risk_index']}"
                )
            else:
                print(f"flightplan error: {data.get('error')}")
        else:
            print(f"flightplan HTTP {r.status_code}: {r.text}")

        # 6) POST multi-leg route summary (JSON, optional circular)
        payload = {"airports": MULTI_AIRPORTS, "circular": True}
        r = await client.post(f"{BASE_URL}/api/flightpath/summary/route", json=payload)
        if r.status_code == 200:
            data = r.json()
            ml_route = "->".join(data['airports'])
            print(
                f"multileg airports={ml_route} circular={data['circular']} "
                f"total_nm={data['total_distance_nm']} segments={len(data['segments'])}"
            )
            # Print first two segments for brevity
            for seg in data['segments'][:2]:
                print(f"  leg {seg['origin']}->{seg['destination']}: {seg['distance_nm']} nm, points={seg['points']}")
        else:
            print(f"multileg HTTP {r.status_code}: {r.text}")

        print("=== Done ===")


if __name__ == "__main__":
    asyncio.run(run_tests())
