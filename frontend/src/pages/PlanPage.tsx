import Header from "@/components/Header";
import Hero from "@/components/Hero";
import Footer from "@/components/Footer";

export default function PlanPage() {
    return (
        <div className="min-h-screen flex flex-col bg-background text-foreground">
            <Header></Header>
            <Hero></Hero>
            <Footer></Footer>
        </div>
    );
}
