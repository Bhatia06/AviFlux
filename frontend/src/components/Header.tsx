"use client";

import {
    NavigationMenu,
    NavigationMenuItem,
    NavigationMenuList,
    NavigationMenuLink,
} from "@/components/ui/navigation-menu";
import { Button } from "@/components/ui/button";
import { ModeToggle } from "@/components/mode-toggle";
import { GithubIcon, Menu, UserCircle, LogOut } from "lucide-react";
import Logo from "../assets/Logo.png";
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/context/AuthContext";
import { useNavigate, useLocation } from "react-router-dom";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { scrollToFeatures } from "@/utils/scroll";

export default function Header() {
    const { user, signOut } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleSignOut = async () => {
        await signOut();
        navigate("/");
    };

    const handleFeaturesClick = (e: React.MouseEvent) => {
        e.preventDefault();
        if (location.pathname === "/") {
            scrollToFeatures();
        } else {
            navigate("/?scrollTo=features");
        }
    };

    return (
        <header className="border-b">
            <div className="container mx-auto flex items-center justify-between p-2">
                {/* Left side - Logo */}
                <NavigationMenu>
                    <NavigationMenuList>
                        <NavigationMenuItem>
                            <NavigationMenuLink href="/">
                                <span className="font-bold text-xl flex items-center gap-2">
                                    <img
                                        src={Logo}
                                        alt="Logo"
                                        className="h-10"
                                    />
                                    AviFlux
                                </span>
                            </NavigationMenuLink>
                        </NavigationMenuItem>
                    </NavigationMenuList>
                </NavigationMenu>

                {/* Desktop Nav */}
                <NavigationMenu className="hidden md:flex">
                    <NavigationMenuList>
                        <NavigationMenuItem>
                            <NavigationMenuLink href="/about">
                                <span className="font-semibold">About</span>
                            </NavigationMenuLink>
                        </NavigationMenuItem>
                        {user && (
                            <NavigationMenuItem>
                                <NavigationMenuLink href="/plan">
                                    <span className="font-semibold">Plans</span>
                                </NavigationMenuLink>
                            </NavigationMenuItem>
                        )}
                        <NavigationMenuItem>
                            <NavigationMenuLink
                                href="#features"
                                onClick={handleFeaturesClick}
                            >
                                <span className="font-semibold">Features</span>
                            </NavigationMenuLink>
                        </NavigationMenuItem>
                        <NavigationMenuItem>
                            <NavigationMenuLink href="/plan">
                                <span className="font-semibold">Plan</span>
                            </NavigationMenuLink>
                        </NavigationMenuItem>
                    </NavigationMenuList>
                </NavigationMenu>

                {/* Right side actions (desktop only) */}
                <div className="hidden md:flex items-center gap-4">
                    {user ? (
                        <DropdownMenu>
                            <DropdownMenuTrigger>
                                <Avatar>
                                    <AvatarImage
                                        src={user.user_metadata?.avatar_url}
                                    />
                                    <AvatarFallback>
                                        {user.email?.charAt(0).toUpperCase()}
                                    </AvatarFallback>
                                </Avatar>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                                <DropdownMenuLabel>
                                    {user.email}
                                </DropdownMenuLabel>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem
                                    onClick={() => navigate("/profile")}
                                >
                                    <UserCircle className="mr-2 h-4 w-4" />
                                    Profile
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={handleSignOut}>
                                    <LogOut className="mr-2 h-4 w-4" />
                                    Sign Out
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    ) : (
                        <Button variant="outline" size="sm" asChild>
                            <a href="/login">Login</a>
                        </Button>
                    )}
                    <Button size="sm" asChild>
                        <a
                            href="https://github.com/Bhatia06/AviFlux"
                            target="_blank"
                        >
                            <GithubIcon className="h-4 w-4" />
                        </a>
                    </Button>
                    <ModeToggle />
                </div>

                {/* Mobile Menu */}
                <div className="md:hidden">
                    <Sheet>
                        <SheetTrigger asChild>
                            <Button variant="ghost" size="icon">
                                <Menu className="h-6 w-6" />
                            </Button>
                        </SheetTrigger>
                        <SheetContent side="right">
                            <SheetHeader>
                                <SheetTitle>
                                    {" "}
                                    <span className="font-bold text-xl flex items-center gap-2">
                                        <img
                                            src={Logo}
                                            alt="Logo"
                                            className="h-10"
                                        />
                                        AviFlux
                                    </span>
                                </SheetTitle>
                            </SheetHeader>
                            <div className="flex flex-col gap-4 mt-4">
                                <a href="/about" className="font-semibold">
                                    About
                                </a>
                                {user && (
                                    <a href="/plan" className="font-semibold">
                                        Plans
                                    </a>
                                )}
                                <a
                                    href="#features"
                                    className="font-semibold"
                                    onClick={handleFeaturesClick}
                                >
                                    Features
                                </a>
                                {user ? (
                                    <>
                                        <a
                                            href="/profile"
                                            className="font-semibold flex items-center gap-2"
                                        >
                                            <UserCircle className="h-4 w-4" />
                                            Profile
                                        </a>
                                        <Button
                                            variant="destructive"
                                            onClick={handleSignOut}
                                        >
                                            <LogOut className="h-4 w-4 mr-2" />
                                            Sign Out
                                        </Button>
                                    </>
                                ) : (
                                    <Button variant="outline" asChild>
                                        <a href="/login">Login</a>
                                    </Button>
                                )}
                                <Button asChild>
                                    <a
                                        href="https://github.com/Bhatia06/AviFlux"
                                        target="_blank"
                                    >
                                        <GithubIcon className="h-4 w-4" />
                                    </a>
                                </Button>
                                <ModeToggle />
                            </div>
                        </SheetContent>
                    </Sheet>
                </div>
            </div>
        </header>
    );
}
