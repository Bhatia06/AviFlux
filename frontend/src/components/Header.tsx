import { NavigationMenu, NavigationMenuItem, NavigationMenuLink, NavigationMenuList } from "@radix-ui/react-navigation-menu";
import { Github } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";

export function Header() {
  return (
    <header className="border-b">
      <div className="container mx-auto flex h-16 items-center px-4">
        <NavigationMenu>
          <NavigationMenuList className="flex gap-6">
            <NavigationMenuItem>
              <NavigationMenuLink className="text-sm font-medium transition-colors hover:text-primary">
                About
              </NavigationMenuLink>
            </NavigationMenuItem>
            <NavigationMenuItem>
              <NavigationMenuLink className="text-sm font-medium transition-colors hover:text-primary">
                Blog
              </NavigationMenuLink>
            </NavigationMenuItem>
            <NavigationMenuItem>
              <NavigationMenuLink className="text-sm font-medium transition-colors hover:text-primary">
                Create Path
              </NavigationMenuLink>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>
        
        <div className="ml-auto flex items-center space-x-4">
          <ThemeToggle />
          <button className="text-sm font-medium transition-colors hover:text-primary">
            Login
          </button>
          <a
            href="#"
            target="_blank"
            rel="noreferrer"
            className="transition-colors hover:text-primary"
          >
            <Github className="h-5 w-5" />
          </a>
          {/* Logo placeholder */}
          <div className="h-8 w-8">
            {/* Add your logo here */}
          </div>
        </div>
      </div>
    </header>
  );
}