import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { safePostRequest } from "@/api/flightpath";

export default function Hero() {
    const [icaoCodes, setIcaoCodes] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    function isValidICAOList(str: string) {
        const trimmedStr = str.trim();
        const regex = /^([A-Z]{4})(\s*,\s*[A-Z]{4})+$/;
        return regex.test(trimmedStr);
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!isValidICAOList(icaoCodes)) {
            alert(
                "Invalid ICAO codes. Use format: KJFK, KORD, KSFO. \nEach code must be 4 letters, uppercase, and separated by commas. \nMinimum two codes required."
            );
            return;
        }

        setLoading(true);
        try {
            const response = await safePostRequest(icaoCodes);
            navigate(`/plan/${response.plan_id}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="flex-1 flex flex-col items-center justify-center text-center px-4 mb-25">
            <h1 className="text-7xl font-bold text-blue-600 mb-3">
                Flight Path Planner
            </h1>
            <p className="mb-8 text-muted-foreground">
                Enter your route using ICAO airport codes (comma separated).
            </p>

            <div className="relative w-full flex justify-center">
                {/* Highlight Background */}
                <div className="absolute inset-0 flex justify-center">
                    <div className="w-full max-w-lg h-32 bg-gradient-to-r from-blue-500/20 via-blue-600/20 to-blue-500/20 rounded-2xl blur-2xl" />
                </div>

                {/* Foreground Form */}
                <form
                    onSubmit={handleSubmit}
                    className="relative flex gap-2 w-full max-w-lg p-4 bg-background border rounded-2xl shadow-md"
                >
                    <Input
                        type="text"
                        placeholder="KJFK, KORD, KSFO"
                        value={icaoCodes}
                        onChange={(e) =>
                            setIcaoCodes(e.target.value.toUpperCase())
                        }
                        autoFocus
                        className="flex-1"
                    />
                    <Button type="submit" disabled={loading}>
                        {loading ? "Loading..." : "Search"}
                    </Button>
                </form>
            </div>
        </main>
    );
}
