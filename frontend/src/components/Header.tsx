"use client";

import {
    NavigationMenu,
    NavigationMenuItem,
    NavigationMenuList,
    NavigationMenuLink,
} from "@/components/ui/navigation-menu";
import { Button } from "@/components/ui/button";
import { ModeToggle } from "@/components/mode-toggle";
import { GithubIcon, Menu } from "lucide-react";
import Logo from "../assets/Logo.png";
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet";

export default function Header() {
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
                        <NavigationMenuItem>
                            <NavigationMenuLink href="#features">
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
                    <Button variant="outline" size="sm" asChild>
                        <a href="/login">Login</a>
                    </Button>
                    <Button size="sm" asChild>
                        <a href="https://github.com/your-repo" target="_blank">
                            <GithubIcon />
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
                                {/* Use plain anchors/buttons instead of NavigationMenuLink here */}
                                <a href="/about" className="font-semibold">
                                    About
                                </a>
                                <a href="#features" className="font-semibold">
                                    Features
                                </a>
                                <a href="/plan" className="font-semibold">
                                    Plan
                                </a>
                                <Button variant="outline" asChild>
                                    <a href="/login">Login</a>
                                </Button>
                                <Button asChild>
                                    <a
                                        href="https://github.com/your-repo"
                                        target="_blank"
                                    >
                                        <GithubIcon />
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
