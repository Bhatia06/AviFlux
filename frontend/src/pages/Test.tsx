import React from "react";
import {
    MapContainer,
    TileLayer,
    Marker,
    Popup,
    Polyline,
    Polygon,
    Tooltip,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

// --- Types ---
interface Aircraft {
    type: string;
    cruise_alt_ft: number;
    fuel_kg: number;
    endurance_min: number;
}

interface Route {
    airports: string[];
    departure_time: string;
    aircraft: Aircraft;
    distance_nm: number;
    estimated_time_min: number;
}

interface Summary {
    text: string[];
    risk_index: string;
}

interface Hazard {
    type: string;
    severity: "low" | "medium" | "high";
    subtype?: string;
    location?: string;
    description?: string;
    geojson: { type: string; coordinates: number[][][] };
}

interface Airport {
    icao: string;
    status: "VFR" | "IFR";
    coord: [number, number]; // [lng, lat]
}

interface MapLayers {
    route: { type: string; coordinates: [number, number][] };
    airports: Airport[];
    hazards: Hazard[];
}

interface FlightPlan {
    plan_id: string;
    generated_at: string;
    route: Route;
    summary: Summary;
    risks: Hazard[];
    map_layers: MapLayers;
}

// --- Sample Data ---
const flightPlan: FlightPlan = {
    plan_id: "UUID-12345",
    generated_at: "2025-09-25T09:00:00Z",
    route: {
        airports: ["KJFK", "ORD", "KSFO"],
        departure_time: "2025-09-25T12:00:00Z",
        aircraft: {
            type: "A320",
            cruise_alt_ft: 35000,
            fuel_kg: 12000,
            endurance_min: 240,
        },
        distance_nm: 1780,
        estimated_time_min: 215,
    },
    summary: {
        text: [
            "Weather at departure (KJFK) is VFR.",
            "Convective SIGMET active near ORD between 15Z–18Z.",
            "Moderate turbulence expected at FL340 near Denver.",
            "Strong headwinds may extend arrival by 15 min.",
            "KSFO ceilings dropping after 18Z.",
        ],
        risk_index: "amber",
    },
    risks: [
        {
            type: "weather",
            subtype: "convective",
            location: "ORD",
            severity: "high",
            description: "Convective SIGMET active near ORD, 15Z–18Z",
            geojson: {
                type: "Polygon",
                coordinates: [
                    [
                        [-87.95, 41.95],
                        [-87.9, 41.95],
                        [-87.9, 41.99],
                        [-87.95, 41.99],
                        [-87.95, 41.95],
                    ],
                ],
            },
        },
    ],
    map_layers: {
        route: {
            type: "LineString",
            coordinates: [
                [-73.778, 40.641],
                [-87.907, 41.974],
                [-122.375, 37.618],
            ],
        },
        airports: [
            { icao: "KJFK", status: "VFR", coord: [-73.778, 40.641] },
            { icao: "KSFO", status: "IFR", coord: [-122.375, 37.618] },
        ],
        hazards: [
            {
                type: "sigmet",
                severity: "high",
                geojson: {
                    type: "Polygon",
                    coordinates: [
                        [
                            [-87.95, 41.95],
                            [-87.9, 41.95],
                            [-87.9, 41.99],
                            [-87.95, 41.99],
                            [-87.95, 41.95],
                        ],
                    ],
                },
            },
        ],
    },
};

// --- Helper: Marker Icon by Status ---
const getAirportIcon = (status: "VFR" | "IFR") => {
    return L.divIcon({
        className: "",
        html: `<div style="background:${
            status === "VFR" ? "green" : "red"
        };width:12px;height:12px;border-radius:50%;border:2px solid white"></div>`,
    });
};

// --- Component ---
const FlightPlanSummary: React.FC = () => {
    const { route, summary, map_layers } = flightPlan;

    return (
        <div className="flex flex-col lg:flex-row gap-4 p-4">
            {/* Left Panel: Cards */}
            <div className="flex-1 flex flex-col gap-4">
                {/* Flight Plan Card */}
                <Card>
                    <CardHeader>
                        <CardTitle>Flight Plan</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p>
                            <strong>Plan ID:</strong> {flightPlan.plan_id}
                        </p>
                        <p>
                            <strong>Generated At:</strong>{" "}
                            {new Date(flightPlan.generated_at).toLocaleString()}
                        </p>
                        <p>
                            <strong>Departure:</strong>{" "}
                            {new Date(route.departure_time).toLocaleString()}
                        </p>
                        <p>
                            <strong>Aircraft:</strong> {route.aircraft.type},
                            Cruise {route.aircraft.cruise_alt_ft} ft, Fuel{" "}
                            {route.aircraft.fuel_kg} kg
                        </p>
                        <p>
                            <strong>Risk Index:</strong>
                            <Badge
                                variant={
                                    summary.risk_index === "amber"
                                        ? "secondary"
                                        : summary.risk_index === "red"
                                        ? "destructive"
                                        : "default"
                                }
                            >
                                {summary.risk_index.toUpperCase()}
                            </Badge>
                        </p>
                        <p>
                            <strong>Distance:</strong> {route.distance_nm} NM
                        </p>
                        <p>
                            <strong>Estimated Time:</strong>{" "}
                            {route.estimated_time_min} min
                        </p>
                    </CardContent>
                </Card>

                {/* Summary Notes Card */}
                <Card>
                    <CardHeader>
                        <CardTitle>Summary Notes</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ScrollArea style={{ maxHeight: 150 }}>
                            <ul className="list-disc pl-5">
                                {summary.text.map((note, idx) => (
                                    <li key={idx}>{note}</li>
                                ))}
                            </ul>
                        </ScrollArea>
                    </CardContent>
                </Card>

                {/* Airports Card */}
                <Card>
                    <CardHeader>
                        <CardTitle>Airports</CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-wrap gap-2">
                        {map_layers.airports.map((ap, idx) => (
                            <Badge
                                key={idx}
                                variant={
                                    ap.status === "VFR"
                                        ? "default"
                                        : "destructive"
                                }
                            >
                                {ap.icao} - {ap.status}
                            </Badge>
                        ))}
                    </CardContent>
                </Card>

                {/* Hazards Card */}
                <Card>
                    <CardHeader>
                        <CardTitle>Hazards</CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-wrap gap-2">
                        {map_layers.hazards.map((hazard, idx) => (
                            <Badge
                                key={idx}
                                variant={
                                    hazard.severity === "high"
                                        ? "destructive"
                                        : "default"
                                }
                            >
                                {hazard.type.toUpperCase()} - {hazard.severity}
                            </Badge>
                        ))}
                    </CardContent>
                </Card>
            </div>

            {/* Right Panel: Map */}
            <div className="flex-1 min-h-[500px]">
                <MapContainer
                    center={[39.8283, -98.5795]}
                    zoom={4}
                    style={{ height: "100%", width: "100%" }}
                >
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution="&copy; OpenStreetMap contributors"
                    />

                    {/* Route line */}
                    <Polyline
                        positions={map_layers.route.coordinates.map((c) => [
                            c[1],
                            c[0],
                        ])}
                        color="blue"
                    >
                        <Tooltip>
                            Distance: {route.distance_nm} NM
                            <br />
                            Estimated Time: {route.estimated_time_min} min
                        </Tooltip>
                    </Polyline>

                    {/* Airports */}
                    {map_layers.airports.map((ap, idx) => (
                        <Marker
                            key={idx}
                            position={[ap.coord[1], ap.coord[0]]}
                            icon={getAirportIcon(ap.status)}
                        >
                            <Popup>
                                {ap.icao} - {ap.status}
                            </Popup>
                        </Marker>
                    ))}

                    {/* Hazards */}
                    {map_layers.hazards.map((hazard, idx) => (
                        <Polygon
                            key={idx}
                            positions={hazard.geojson.coordinates[0].map(
                                (coord) => [coord[1], coord[0]]
                            )}
                            color={
                                hazard.severity === "high" ? "red" : "orange"
                            }
                        >
                            <Popup>
                                {hazard.type.toUpperCase()} - {hazard.severity}
                            </Popup>
                        </Polygon>
                    ))}
                </MapContainer>
            </div>
        </div>
    );
};

export default FlightPlanSummary;
