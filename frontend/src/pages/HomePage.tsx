import Header from "@/components/Header";
import Hero from "@/components/Hero";
import Footer from "@/components/Footer";
import { AIChatbot } from "@/components/ChatBot";

export default function HomePage() {
    return (
        <div className="min-h-screen flex flex-col bg-background text-foreground">
            <Header></Header>
            <AIChatbot></AIChatbot>
            <Hero></Hero>
            <Footer></Footer>
        </div>
    );
}
