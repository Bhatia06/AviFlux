import Header from "@/components/Header";
import Hero from "@/components/Hero";
import HomePageSections from "@/components/HomePageSections";
import Footer from "@/components/Footer";
import { AIChatbot } from "@/components/ChatBot";

export default function HomePage() {
    return (
        <div className="min-h-screen flex flex-col bg-background text-foreground">
            <Header></Header>
            <AIChatbot></AIChatbot>
            <div className="flex flex-col flex-1 gap-40 mt-40 ">
                <Hero></Hero>
                <HomePageSections></HomePageSections>
            </div>
            <Footer></Footer>
        </div>
    );
}
