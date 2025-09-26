import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
// import FlightPlanSummary from "./Test";
import FlightPlanSummary from "@/components/FlightPlanSummary";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

type Plan = {
    plan_id: string;
    route: string[];
    summary: string[];
    risk_index: string;
} | null;

export default function PlanDetailPage() {
    const { id } = useParams();
    const [plan, setPlan] = useState<Plan>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchPlan() {
            try {
                const response = await fakePlanFetch(id!);
                setPlan(response as Plan);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        }
        fetchPlan();
    }, [id]);

    if (loading) return <p>Loading plan {id}...</p>;
    if (!plan) return <p>Plan not found.</p>;

    return (
        <div className="min-h-screen flex flex-col bg-background text-foreground">
            <Header></Header>
            <FlightPlanSummary></FlightPlanSummary>
            <Footer></Footer>
        </div>
    );
}

// Mock backend call
async function fakePlanFetch(id: string) {
    return new Promise((resolve) =>
        setTimeout(
            () =>
                resolve({
                    plan_id: id,
                    route: ["KJFK", "KORD", "KSFO"],
                    summary: [
                        "Weather good at departure",
                        "Turbulence near ORD",
                    ],
                    risk_index: "amber",
                }),
            1500
        )
    );
}
