import { useEffect } from "react";
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import HomePageSections from "@/components/HomePageSections";
import Footer from "@/components/Footer";
import { AIChatbot } from "@/components/ChatBot";
import { Toaster } from "@/components/ui/sonner";

export default function HomePage() {
    useEffect(() => {
        // Check if there's a scrollTo parameter in the URL
        const searchParams = new URLSearchParams(window.location.search);
        if (searchParams.get("scrollTo") === "features") {
            // Remove the query parameter
            window.history.replaceState(
                {},
                document.title,
                window.location.pathname
            );
            // Scroll to features section after a short delay to ensure content is loaded
            setTimeout(() => {
                const featuresSection = document.getElementById("features");
                if (featuresSection) {
                    featuresSection.scrollIntoView({ behavior: "smooth" });
                }
            }, 100);
        }
    }, []);

    return (
        <div className="min-h-screen flex flex-col bg-background text-foreground">
            <Header></Header>
            <Toaster />
            <AIChatbot floating></AIChatbot>
            <div className="flex flex-col flex-1 gap-40 mt-40 ">
                <Hero></Hero>
                <HomePageSections></HomePageSections>
            </div>
            <Footer></Footer>
        </div>
    );
}
