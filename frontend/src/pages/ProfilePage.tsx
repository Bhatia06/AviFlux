import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { LogOut, Mail, User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

export default function ProfilePage() {
    const { user, signOut, loading } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (!loading && !user) {
            navigate("/login");
        }
    }, [user, loading, navigate]);

    const handleSignOut = async () => {
        await signOut();
        navigate("/");
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-white" />
            </div>
        );
    }

    return (
        <div className="container mx-auto py-8 px-4">
            <h1 className="text-4xl font-bold mb-8">Profile</h1>

            <div className="grid gap-6 md:grid-cols-2">
                {/* User Info Card */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center gap-4">
                            <Avatar className="h-16 w-16">
                                <AvatarImage
                                    src={user?.user_metadata?.avatar_url}
                                />
                                <AvatarFallback>
                                    {user?.email?.charAt(0).toUpperCase()}
                                </AvatarFallback>
                            </Avatar>
                            <div>
                                <CardTitle>
                                    {user?.user_metadata?.full_name || "User"}
                                </CardTitle>
                                <CardDescription className="flex items-center gap-2">
                                    <Mail className="h-4 w-4" />
                                    {user?.email}
                                </CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div>
                                <h3 className="font-semibold mb-2">
                                    Account Details
                                </h3>
                                <div className="grid gap-2">
                                    <div className="flex items-center gap-2">
                                        <User className="h-4 w-4 opacity-70" />
                                        <span className="text-sm">
                                            Member since{" "}
                                            {new Date(
                                                user?.created_at || ""
                                            ).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Badge variant="secondary">
                                            {user?.role || "user"}
                                        </Badge>
                                    </div>
                                </div>
                            </div>

                            <Separator />

                            <div>
                                <h3 className="font-semibold mb-2">
                                    Authentication
                                </h3>
                                <div className="grid gap-2">
                                    <div className="flex items-center gap-2">
                                        <Badge variant="outline">
                                            Google Account
                                        </Badge>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                    <CardFooter>
                        <Button
                            variant="destructive"
                            onClick={handleSignOut}
                            className="w-full"
                        >
                            <LogOut className="h-4 w-4 mr-2" />
                            Sign Out
                        </Button>
                    </CardFooter>
                </Card>

                {/* Activity Card */}
                <Card>
                    <CardHeader>
                        <CardTitle>Recent Activity</CardTitle>
                        <CardDescription>
                            Your recent actions and updates
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {/* Placeholder for recent activity - you can expand this later */}
                            <div className="text-sm text-muted-foreground">
                                No recent activity to show
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
