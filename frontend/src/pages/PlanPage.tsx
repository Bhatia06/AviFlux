import { useNavigate } from "react-router-dom";

export default function PlanPage() {
    const navigate = useNavigate();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const fakeId = "UUID-12345"; // replace with backend call
        navigate(`/plan/${fakeId}`);
    };

    return (
        <div className="p-6">
            <h1 className="text-xl font-bold mb-4">Create a Flight Plan</h1>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Enter departure ICAO"
                    className="border p-2 mr-2"
                />
                <input
                    type="text"
                    placeholder="Enter destination ICAO"
                    className="border p-2 mr-2"
                />
                <button className="bg-blue-600 text-white px-4 py-2 rounded">
                    Submit
                </button>
            </form>
        </div>
    );
}
