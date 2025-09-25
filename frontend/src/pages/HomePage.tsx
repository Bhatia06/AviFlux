import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Header } from "../components/Header";
import { Footer } from "../components/Footer";

export default function HomePage() {
    const [icaoCodes, setIcaoCodes] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        // Simple ICAO validation: only letters/numbers and commas
        if (!/^[A-Z0-9, ]+$/.test(icaoCodes)) {
            alert("Invalid ICAO codes. Use format like: KJFK, KORD, KSFO");
            return;
        }

        setLoading(true);

        try {
            // Replace with real backend API call
            const response = await fakeApiCall(icaoCodes);

            // Navigate to /plan/:id with returned plan ID
            navigate(`/plan/${response.plan_id}`);
        } catch (err) {
            console.error(err);
            alert("Failed to fetch plan.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">
                <section className="container mx-auto flex flex-col items-center justify-center space-y-4 py-32 text-center">
                    <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl">
                        Your Flight Planning Assistant
                    </h1>
                    <p className="max-w-[700px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
                        Enter your ICAO codes to get started with your flight
                        plan.
                    </p>
                    <form
                        onSubmit={handleSubmit}
                        className="w-full max-w-sm space-y-2"
                    >
                        <input
                            type="text"
                            placeholder="Enter ICAO codes (e.g., KJFK, KORD, KSFO)"
                            value={icaoCodes}
                            onChange={(e) =>
                                setIcaoCodes(e.target.value.toUpperCase())
                            }
                            className="w-full rounded-md border border-gray-200 px-4 py-2 text-sm transition-colors placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-800 dark:bg-gray-950 dark:placeholder:text-gray-400"
                        />
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full rounded-md bg-blue-600 px-8 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:pointer-events-none disabled:opacity-50 dark:bg-blue-700 dark:hover:bg-blue-800"
                        >
                            {loading ? "Loading..." : "Generate Flight Plan"}
                        </button>
                    </form>
                </section>
            </main>
            <Footer />
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
