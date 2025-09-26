import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import GoogleLogo from ".././assets/logo-google.png";
import { useState } from "react";

export function GoogleSignInButton() {
    const { signInWithGoogle } = useAuth();
    const [isLoading, setIsLoading] = useState(false);

    const handleSignIn = async () => {
        try {
            setIsLoading(true);
            await signInWithGoogle();
        } catch (error) {
            console.error("Error signing in with Google:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Button
            variant="outline"
            onClick={handleSignIn}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 border-gray-700 hover:bg-gray-800"
        >
            <img src={GoogleLogo} alt="Google" className="w-5 h-5 invert" />
            Google
        </Button>
    );
}
