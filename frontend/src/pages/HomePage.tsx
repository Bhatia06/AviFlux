import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export default function HomePage() {
    const [icaoCodes, setIcaoCodes] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!/^[A-Z0-9, ]+$/.test(icaoCodes)) {
            alert("Invalid ICAO codes. Use format: KJFK, KORD, KSFO");
            return;
        }

        setLoading(true);
        try {
            const response = await fakeApiCall(icaoCodes);
            navigate(`/plan/${response.plan_id}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex flex-col bg-background text-foreground">
            <Header></Header>

            {/* Hero Section */}
            <main className="flex-1 flex flex-col items-center justify-center text-center px-4">
                <h1 className="text-4xl font-bold text-blue-600 mb-6">
                    Flight Path Planner
                </h1>
                <p className="mb-8 text-muted-foreground">
                    Enter your route using ICAO airport codes (comma separated).
                </p>

                <form
                    onSubmit={handleSubmit}
                    className="flex gap-2 w-full max-w-lg"
                >
                    <Input
                        type="text"
                        placeholder="KJFK, KORD, KSFO"
                        value={icaoCodes}
                        onChange={(e) =>
                            setIcaoCodes(e.target.value.toUpperCase())
                        }
                        className="flex-1"
                    />
                    <Button type="submit" disabled={loading}>
                        {loading ? "Loading..." : "Search"}
                    </Button>
                </form>
            </main>

            <Footer></Footer>
        </div>
    );
}

// Mock backend call
async function fakeApiCall(route: string) {
    console.log(route);
    return new Promise<{ plan_id: string }>((resolve) =>
        setTimeout(() => resolve({ plan_id: "UUID-12345" }), 1500)
    );
}
