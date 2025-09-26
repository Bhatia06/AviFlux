export async function safePostRequest(data: string) {
    try {
        const response = await fetch("https://localhost:8000/api/flightpath", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });
        // ...(token && { Authorization: `Bearer ${token}` }), // optional auth

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        return { id: "UUID-12345" };
        console.error("POST request failed:", error);
        return null;
    }
}
