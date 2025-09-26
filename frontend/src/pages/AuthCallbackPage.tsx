import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { supabase } from "@/lib/supabase";

export default function AuthCallbackPage() {
    const navigate = useNavigate();
    const { setSession } = useAuth();

    useEffect(() => {
        // Get the auth code from URL
        const handleAuthCallback = async () => {
            const hashParams = new URLSearchParams(
                window.location.hash.substring(1)
            );
            const queryParams = new URLSearchParams(window.location.search);

            try {
                // Check if we have an error in the URL
                const errorInHash = hashParams.get("error");
                const errorInQuery = queryParams.get("error");
                if (errorInHash || errorInQuery) {
                    throw new Error(
                        errorInHash || errorInQuery || "Authentication failed"
                    );
                }

                // Exchange auth code for session
                const {
                    data: { session },
                    error,
                } = await supabase.auth.getSession();

                if (error) throw error;

                if (session) {
                    setSession(session);
                    // Redirect to home page or a protected route
                    navigate("/");
                }
            } catch (error) {
                console.error("Error during auth callback:", error);
                navigate("/login?error=Authentication failed");
            }
        };

        handleAuthCallback();
    }, [navigate, setSession]);

    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-white" />
        </div>
    );
}
