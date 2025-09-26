import { createContext, useContext, useEffect, useState } from "react";
import type { Session, User } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";
import { authService } from "@/lib/auth";
import { toast } from "sonner";

interface AuthContextProps {
    session: Session | null;
    user: User | null;
    signInWithGoogle: () => Promise<void>;
    signOut: () => Promise<void>;
    loading: boolean;
    setSession: (session: Session | null) => void;
}

const AuthContext = createContext<AuthContextProps>({} as AuthContextProps);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [session, setSession] = useState<Session | null>(null);
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Initialize auth state
        const initAuth = async () => {
            try {
                // Get initial session and validate it
                const session = await authService.getSession();
                const isValid = session
                    ? await authService.validateToken()
                    : false;

                if (session && isValid) {
                    setSession(session);
                    const user = await authService.getUser();
                    setUser(user);
                } else if (session) {
                    // Token is invalid, try to refresh
                    const refreshed = await authService.refreshToken();
                    if (refreshed) {
                        const newSession = await authService.getSession();
                        setSession(newSession);
                        const user = await authService.getUser();
                        setUser(user);
                    }
                }
            } catch (error) {
                console.error("Auth initialization error:", error);
                toast.error(
                    "Authentication error. Please try logging in again."
                );
            } finally {
                setLoading(false);
            }
        };

        initAuth();

        // Listen for auth changes
        const {
            data: { subscription },
        } = authService.onAuthStateChange((session) => {
            setSession(session);
            if (session) {
                authService.getUser().then((user) => setUser(user));
            } else {
                setUser(null);
            }
            setLoading(false);
        });

        return () => subscription.unsubscribe();
    }, []);

    const signInWithGoogle = async () => {
        try {
            const { error } = await supabase.auth.signInWithOAuth({
                provider: "google",
                options: {
                    redirectTo: `${window.location.origin}/auth/callback`,
                    queryParams: {
                        access_type: "offline",
                        prompt: "consent",
                    },
                },
            });

            if (error) {
                toast.error("Failed to sign in with Google");
                throw error;
            }
        } catch (error) {
            console.error("Error:", error);
            throw error;
        }
    };

    const signOut = async () => {
        try {
            const { error } = await supabase.auth.signOut();
            if (error) {
                toast.error("Failed to sign out");
                throw error;
            }
            toast.success("Signed out successfully");
        } catch (error) {
            console.error("Error:", error);
            throw error;
        }
    };

    const value = {
        session,
        user,
        signInWithGoogle,
        signOut,
        loading,
        setSession,
    };

    return (
        <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
    );
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
