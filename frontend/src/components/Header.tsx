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
            <div className="container mx-auto flex items-center justify-between p-4">
                <NavigationMenu>
                    <NavigationMenuList>
                        <NavigationMenuItem>
                            <NavigationMenuLink href="/">
                                <img
                                    src={Logo}
                                    alt="Logo Here"
                                    className="h-10"
                                />
                            </NavigationMenuLink>
                        </NavigationMenuItem>
                        <NavigationMenuItem>
                            <NavigationMenuLink href="/about">
                                About
                            </NavigationMenuLink>
                        </NavigationMenuItem>
                        <NavigationMenuItem>
                            <NavigationMenuLink href="/blog">
                                Blog
                            </NavigationMenuLink>
                        </NavigationMenuItem>
                        <NavigationMenuItem>
                            <NavigationMenuLink href="/plan">
                                Create Path
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
