import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

export default function PlanDetailPage() {
    const { id } = useParams();
    const [plan, setPlan] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchPlan() {
            try {
                // Replace with real backend API call
                const response = await fakePlanFetch(id!);
                setPlan(response);
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
        <div>
            <h1>Flight Plan {id}</h1>
            <pre>{JSON.stringify(plan, null, 2)}</pre>
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
