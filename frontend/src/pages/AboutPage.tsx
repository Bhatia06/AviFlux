import Footer from "@/components/Footer";
import Header from "@/components/Header";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Plane, Map, CloudSun } from "lucide-react";

export default function AboutPage() {
    return (
        <>
            <Header></Header>
            <div className="max-w-3xl mx-auto px-6 py-16 text-center">
                <h1 className="text-4xl font-bold text-blue-600 mb-6">
                    About Flight Planner
                </h1>
                <p className="text-lg text-muted-foreground mb-12">
                    Flight planning is often buried in hundreds of pages of raw
                    weather and navigation data. We built Flight Planner to make
                    that process simple, fast, and safe — so pilots can focus on
                    flying, not paperwork.
                </p>

                {/* Features Summary */}
                <div className="grid gap-6 md:grid-cols-3 mb-12">
                    <Card className="shadow-sm">
                        <CardContent className="flex flex-col items-center p-6">
                            <Plane className="h-8 w-8 text-blue-600 mb-2" />
                            <p className="font-semibold">
                                Smart Flight Summaries
                            </p>
                            <p className="text-sm text-muted-foreground">
                                Get a clear 5-line overview of your route
                                instantly.
                            </p>
                        </CardContent>
                    </Card>

                    <Card className="shadow-sm">
                        <CardContent className="flex flex-col items-center p-6">
                            <CloudSun className="h-8 w-8 text-blue-600 mb-2" />
                            <p className="font-semibold">
                                Weather & Risk Alerts
                            </p>
                            <p className="text-sm text-muted-foreground">
                                Live METAR, NOTAM, turbulence and safety
                                indicators.
                            </p>
                        </CardContent>
                    </Card>

                    <Card className="shadow-sm">
                        <CardContent className="flex flex-col items-center p-6">
                            <Map className="h-8 w-8 text-blue-600 mb-2" />
                            <p className="font-semibold">
                                Interactive Route Map
                            </p>
                            <p className="text-sm text-muted-foreground">
                                Visualize your path and compare mid-flight
                                updates.
                            </p>
                        </CardContent>
                    </Card>
                </div>

                <Separator className="my-12" />

                {/* Mission */}
                <div className="text-center space-y-6">
                    <h2 className="text-6xl font-bold text-blue-600">
                        Our Mission
                    </h2>
                    <p className="text-muted-foreground">
                        We believe every pilot deserves tools that reduce
                        workload, improve situational awareness, and increase
                        flight safety. By summarizing complex datasets from{" "}
                        <a
                            href="https://aviationweather.gov/data/api/"
                            target="_blank"
                            className="underline text-blue-600"
                        >
                            official aviation weather sources
                        </a>
                        , we help pilots make better decisions in less time.
                    </p>
                    <p className="text-muted-foreground">
                        Whether you’re a student pilot, airline captain, or
                        instructor, Flight Planner is here to simplify your
                        pre-flight and in-flight planning.
                    </p>
                </div>
            </div>
            <Footer></Footer>
        </>
    );
}
