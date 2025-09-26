import {
    NavigationMenu,
    NavigationMenuItem,
    NavigationMenuList,
    NavigationMenuLink,
} from "@/components/ui/navigation-menu";
import { Button } from "./ui/button";
import { ModeToggle } from "@/components/mode-toggle";
import { GithubIcon } from "lucide-react";
import Logo from ".././assets/Logo.png";

export default function Header() {
    return (
        <header className="border-b">
            <div className="container mx-auto flex items-center justify-between p-2">
                <NavigationMenu>
                    <NavigationMenuList>
                        <NavigationMenuItem>
                            <NavigationMenuLink href="/">
                                <span className="font-bold text-xl flex items-center gap-2">
                                    <img
                                        src={Logo}
                                        alt="Logo Here"
                                        className="h-10"
                                    />
                                    AviFlux
                                </span>
                            </NavigationMenuLink>
                        </NavigationMenuItem>
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

                <div className="flex items-center gap-4">
                    <Button variant="outline" size="sm" asChild>
                        <a href="/login">Login</a>
                    </Button>
                    <Button size="sm" asChild>
                        <a href="https://github.com/your-repo" target="_blank">
                            <GithubIcon></GithubIcon>
                        </a>
                    </Button>
                    <ModeToggle></ModeToggle>
                </div>
            </div>
        </header>
    );
}
