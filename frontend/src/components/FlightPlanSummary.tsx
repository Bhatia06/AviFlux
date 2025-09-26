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

export type FlightPlanResponse = {
    success: boolean;
    message: string;
    data: {
        plan_id: string;
        generated_at: string; // ISO timestamp
        route: {
            airports: string[]; // ICAO codes
            departure_time: string; // ISO timestamp
            distance_nm: number;
            estimated_time_min: number;
        };
        summary: {
            text: string[];
            risk_index: "green" | "yellow" | "red" | string;
        };
        risks: string[];
        map_layers: {
            route: {
                type: "LineString";
                coordinates: [number, number][]; // [lon, lat]
            };
            airports: {
                icao: string;
                status: "VFR" | "IFR" | "MVFR" | "LIFR" | string;
                coord: [number, number];
            }[];
            hazards: any[]; // could be refined later
        };
    };
    error: string | null;
};

function FlightPlanSummary({ flightPlan }: { flightPlan: FlightPlanResponse }) {
    const { route, summary, map_layers } = flightPlan.data;

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

    const calculateMapCenter = (): [number, number] => {
        const airports = map_layers.airports;
        if (airports.length < 2) return [39.8283, -98.5795]; // Default to center of US if not enough airports

        // Get departure and arrival coordinates
        const departure = airports[0];
        const arrival = airports[airports.length - 1];

        // Calculate center point between departure and arrival
        const centerLat = (departure.coord[1] + arrival.coord[1]) / 2;
        const centerLon = (departure.coord[0] + arrival.coord[0]) / 2;

        return [centerLat, centerLon];
    };

    const calculateZoomLevel = () => {
        const airports = map_layers.airports;
        if (airports.length < 2) return 4; // Default zoom

        // Calculate the distance between airports
        const departure = airports[0];
        const arrival = airports[airports.length - 1];

        // Simple distance calculation (not exact but good enough for zoom)
        const latDiff = Math.abs(departure.coord[1] - arrival.coord[1]);
        const lonDiff = Math.abs(departure.coord[0] - arrival.coord[0]);

        // Adjust zoom based on distance
        if (latDiff > 90 || lonDiff > 90) return 2; // Very long distance
        if (latDiff > 45 || lonDiff > 45) return 3; // Long distance
        if (latDiff > 20 || lonDiff > 20) return 4; // Medium distance
        if (latDiff > 10 || lonDiff > 10) return 5; // Short distance
        return 6; // Very short distance
    };

    const renderAirports = (
        airports: FlightPlanResponse["data"]["map_layers"]["airports"]
    ) => {
        return airports.map((ap, idx: number) => (
            <Marker
                key={idx}
                position={[ap.coord[1], ap.coord[0]]}
                icon={getAirportIcon(ap.status === "VFR" ? "VFR" : "IFR")}
            >
                <Popup>
                    {ap.icao} - {ap.status}
                </Popup>
            </Marker>
        ));
    };

    type Hazard = {
        type: string;
        severity: string;
        geojson: {
            coordinates: number[][][];
        };
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

    // const renderWeatherData = () => {
    //     return flightPlan.data.weather_data.time.map(
    //         (t: string, i: number) => ({
    //             time: t,
    //             temperature: flightPlan.data.weather_data.temperature_c[i],
    //             humidity: flightPlan.data.weather_data.humidity_percent[i],
    //             wind: flightPlan.data.weather_data.wind_speed_kt[i],
    //             pressure: flightPlan.data.weather_data.pressure_hpa[i],
    //         })
    //     );
    // };

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
                    <CardHeader>
                        <CardTitle className="text-4xl">Flight Plan</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-end justify-between gap-2 text-sm ">
                            <div>
                                <p>Plan ID: {flightPlan.data.plan_id}</p>
                                <p>
                                    Generated At:{" "}
                                    {new Date(
                                        flightPlan.data.generated_at
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
                            <div className="flex flex-col items-center gap-4 justify-center relative mb-4">
                                <div className="relative mb-6 mx-18">
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
                                    <p>
                                        {summary.risk_index
                                            .charAt(0)
                                            .toUpperCase() +
                                            summary.risk_index.slice(1)}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="bg-card lg:col-span-2">
                    <CardHeader>
                        <CardTitle className="text-3xl">
                            Flight Route Map
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                        <div className="h-[500px] rounded-lg overflow-hidden">
                            <MapContainer
                                center={calculateMapCenter()}
                                zoom={calculateZoomLevel()}
                                style={{ height: "100%", width: "100%" }}
                                className="z-0"
                                zoomControl={false}
                            >
                                <TileLayer
                                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                                    maxZoom={19}
                                />

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

                                {renderAirports(map_layers.airports)}

                                {renderHazards(map_layers.hazards)}
                            </MapContainer>
                        </div>
                    </CardContent>
                </Card>

                <AIChatbot floating={false}></AIChatbot>
            </div>
        </div>
    );
}

export default FlightPlanSummary;
