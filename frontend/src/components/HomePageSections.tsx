import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Plane, Map, CloudSun, Activity } from "lucide-react";
import { useState } from "react";

export default function HomepageSections() {
    const [email, setEmail] = useState("");
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        // TODO: Hook this up to your backend or a service (like Formspree, Resend, or Firebase)
        setTimeout(() => {
            alert("Feedback submitted! Thank you.");
            setEmail("");
            setMessage("");
            setLoading(false);
        }, 1000);
    };

    return (
        <div className="flex flex-col gap-20 px-6 md:px-12 lg:px-24 py-16">
            {/* Features Section */}
            <section className="text-center" id="features">
                <h2 className="text-5xl font-bold mb-4 text-blue-600">
                    Key Features
                </h2>
                <p className="mb-10 text-muted-foreground max-w-2xl mx-auto">
                    Plan safer and faster with live weather, smart summaries,
                    and an interactive map at your fingertips.
                </p>

                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-2 lg:px-100">
                    <Card className="hover:shadow-lg transition">
                        <CardHeader>
                            <div className="flex items-center gap-2 justify-center mt-4">
                                <Plane className="h-8 w-8 text-blue-600" />
                                <CardTitle>Fast Flight Plans</CardTitle>
                            </div>
                        </CardHeader>
                        <CardContent>
                            Get a 5-line overview of your route instantly.
                        </CardContent>
                    </Card>

                    <Card className="hover:shadow-lg transition">
                        <CardHeader>
                            <div className="flex items-center gap-2 justify-center mt-4">
                                <CloudSun className="h-8 w-8 text-blue-600" />
                                <CardTitle>Weather & Risks</CardTitle>
                            </div>
                        </CardHeader>
                        <CardContent>
                            Live METARs, turbulence zones, and NOTAM indicators.
                        </CardContent>
                    </Card>

                    <Card className="hover:shadow-lg transition">
                        <CardHeader>
                            <div className="flex items-center gap-2 justify-center mt-4">
                                <Map className="h-8 w-8 text-blue-600" />
                                <CardTitle>Interactive Map</CardTitle>
                            </div>
                        </CardHeader>
                        <CardContent>
                            Visualize your flight path and check for route
                            discrepancies.
                        </CardContent>
                    </Card>

                    <Card className="hover:shadow-lg transition">
                        <CardHeader>
                            <div className="flex items-center gap-2 justify-center mt-4">
                                <Activity className="h-8 w-8 text-blue-600" />
                                <CardTitle>Risk Management</CardTitle>
                            </div>
                        </CardHeader>
                        <CardContent>
                            Warnings for traffic, alternates, and safety risks.
                        </CardContent>
                    </Card>
                </div>
            </section>

            <Separator />

            <section
                className="w-full max-w-2xl mx-auto py-8 px-6"
                id="contact"
            >
                <Card className="shadow-md">
                    <CardHeader className="text-center">
                        <CardTitle className="text-2xl font-bold text-blue-600">
                            Contact & Feedback
                        </CardTitle>
                        <p className="text-muted-foreground mt-2">
                            Have suggestions or found an issue? Let us know.
                        </p>
                    </CardHeader>
                    <CardContent>
                        <form
                            onSubmit={handleSubmit}
                            className="flex flex-col gap-4"
                        >
                            <Input
                                type="email"
                                placeholder="Your email (optional)"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                            <Textarea
                                placeholder="Write your feedback here..."
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                className="min-h-[120px]"
                                required
                            />
                            <Button
                                type="submit"
                                className="bg-blue-600 hover:bg-blue-700"
                                disabled={loading}
                            >
                                {loading ? "Sending..." : "Send Feedback"}
                            </Button>
                        </form>
                    </CardContent>
                </Card>
            </section>
        </div>
    );
}
