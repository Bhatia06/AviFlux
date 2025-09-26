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
import { ScrollArea } from "@/components/ui/scroll-area";
import { AIChatbot } from "@/components/ChatBot";

// Types
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
    weather_data: {
        time: string[];
        temperature_c: number[];
        humidity_percent: number[];
        wind_speed_kt: number[];
        pressure_hpa: number[];
    };
}
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartTooltip,
    ResponsiveContainer,
    Legend,
} from "recharts";

// Sample Data
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
    weather_data: {
        time: ["12Z", "13Z", "14Z", "15Z", "16Z", "17Z"],
        temperature_c: [15, 17, 18, 20, 19, 16],
        humidity_percent: [65, 63, 60, 58, 62, 70],
        wind_speed_kt: [10, 15, 18, 12, 20, 14],
        pressure_hpa: [1012, 1010, 1008, 1009, 1011, 1013],
    },
};

const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
        case "red":
            return "bg-red-500";
        case "amber":
            return "bg-yellow-500";
        case "green":
            return "bg-green-500";
        default:
            return "bg-gray-500";
    }
};

const getAirportIcon = (status: "VFR" | "IFR") => {
    const color = status === "VFR" ? "#22c55e" : "#ef4444"; // Using Tailwind colors
    return L.divIcon({
        className: "",
        html: `
            <div style="
                background: ${color};
                width: 16px;
                height: 16px;
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 0 10px rgba(0,0,0,0.3);
                position: relative;
            ">
                <div style="
                    position: absolute;
                    top: -4px;
                    left: -4px;
                    right: -4px;
                    bottom: -4px;
                    border-radius: 50%;
                    border: 2px solid ${color};
                    opacity: 0.5;
                "></div>
            </div>
        `,
        iconSize: [16, 16],
        iconAnchor: [8, 8],
    });
};

const FlightPlanSummary: React.FC = () => {
    const { route, summary, map_layers } = flightPlan;

    // Type-safe mapping functions
    const renderWeatherNotes = (notes: string[]) => {
        return notes.map((note: string, idx: number) => (
            <li key={idx} className="text-sm">
                {note}
            </li>
        ));
    };

    const renderRoute = (coordinates: [number, number][]) => {
        return coordinates.map((c: [number, number]): [number, number] => [
            c[1],
            c[0],
        ]);
    };

    const renderAirports = (airports: Airport[]) => {
        return airports.map((ap: Airport, idx: number) => (
            <Marker
                key={idx}
                position={[ap.coord[1], ap.coord[0]]}
                icon={getAirportIcon(ap.status)}
            >
                <Popup>
                    {ap.icao} - {ap.status}
                </Popup>
            </Marker>
        ));
    };

    const renderHazards = (hazards: Hazard[]) => {
        return hazards.map((hazard: Hazard, idx: number) => (
            <Polygon
                key={idx}
                positions={hazard.geojson.coordinates[0].map(
                    (coord: number[]) => [coord[1], coord[0]]
                )}
                color={hazard.severity === "high" ? "red" : "orange"}
            >
                <Popup>
                    {hazard.type.toUpperCase()} - {hazard.severity}
                </Popup>
            </Polygon>
        ));
    };

    const renderWeatherData = () => {
        return flightPlan.weather_data.time.map((t: string, i: number) => ({
            time: t,
            temperature: flightPlan.weather_data.temperature_c[i],
        }));
    };

    return (
        <div className="container mx-auto p-4 space-y-6">
            {/* Top Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Weather Summary Card */}
                <Card className="bg-card">
                    <CardHeader>
                        <CardTitle className="text-4xl font-bold">
                            Weather Summary
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ScrollArea className=" pr-4">
                            <ul className="list-disc pl-5 space-y-2">
                                {renderWeatherNotes(summary.text)}
                            </ul>
                        </ScrollArea>
                    </CardContent>
                </Card>

                {/* Flight Plan Details Card */}
                <Card className="bg-card">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle className="text-4xl">Flight Plan</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-end justify-between gap-2 text-sm ">
                            <div>
                                <p>Plan ID: {flightPlan.plan_id}</p>
                                <p>
                                    Generated At:{" "}
                                    {new Date(
                                        flightPlan.generated_at
                                    ).toLocaleString()}
                                </p>
                                <p>
                                    Departure:{" "}
                                    {new Date(
                                        route.departure_time
                                    ).toLocaleString()}
                                </p>
                                <p>Distance: {route.distance_nm} NM</p>
                                <p>
                                    Estimated Time: {route.estimated_time_min}{" "}
                                    min
                                </p>
                            </div>
                            <div className="flex flex-col items-center gap-4 justify-center relative">
                                <div className="relative mb-6">
                                    <span
                                        className={`absolute inset-0 rounded-full blur-lg ${getStatusColor(
                                            summary.risk_index
                                        )} `}
                                    ></span>

                                    <div
                                        className={`w-4 h-4 rounded-full ${getStatusColor(
                                            summary.risk_index
                                        )} m-auto`}
                                    ></div>
                                </div>

                                <div>
                                    <p>Flight GO/NO-GO</p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Map and Chatbot Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Map Section - Takes up 2/3 of the space on desktop */}
                <Card className="bg-card lg:col-span-2">
                    <CardHeader>
                        <CardTitle className="text-3xl">
                            Flight Route Map
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                        <div className="h-[500px] rounded-lg overflow-hidden">
                            <MapContainer
                                center={[39.8283, -98.5795]}
                                zoom={4}
                                style={{ height: "100%", width: "100%" }}
                                className="z-0"
                                zoomControl={false}
                            >
                                {/* Custom Dark Mode Map Style */}
                                <TileLayer
                                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                                    maxZoom={19}
                                />

                                {/* Route Line with Custom Styling */}
                                <Polyline
                                    positions={renderRoute(
                                        map_layers.route.coordinates
                                    )}
                                    color="#3b82f6"
                                    weight={3}
                                    opacity={0.8}
                                    dashArray="5, 10"
                                >
                                    <Tooltip className="bg-background/80 p-2 rounded-lg border border-border">
                                        <div className="font-medium">
                                            Distance: {route.distance_nm} NM
                                            <br />
                                            Estimated Time:{" "}
                                            {route.estimated_time_min} min
                                        </div>
                                    </Tooltip>
                                </Polyline>

                                {/* Render Airports using our type-safe function */}
                                {renderAirports(map_layers.airports)}

                                {/* Render Hazards using our type-safe function */}
                                {renderHazards(map_layers.hazards)}
                            </MapContainer>
                        </div>
                    </CardContent>
                </Card>

                <AIChatbot floating={false}></AIChatbot>
            </div>

            {/* Weather Charts */}
            <Card className="bg-card">
                <CardHeader>
                    <CardTitle>Weather Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Weather charts remain the same as in the original code */}
                        {/* Temperature Chart */}
                        <ResponsiveContainer width="100%" height={200}>
                            <LineChart data={renderWeatherData()}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="time" />
                                <YAxis unit="°C" />
                                <RechartTooltip />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="temperature"
                                    stroke="#ff7300"
                                />
                            </LineChart>
                        </ResponsiveContainer>

                        {/* Other charts follow the same pattern... */}
                        {/* Add the remaining charts here */}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default FlightPlanSummary;
