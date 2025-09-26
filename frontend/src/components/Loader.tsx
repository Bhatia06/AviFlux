import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { LoaderCircle } from "lucide-react";

// Example filler texts
const fillerTexts = [
    "Fetching epic data...",
    "Summoning AI magic...",
    "Almost there...",
    "Loading your awesomeness...",
    "Brewing some coffee...",
    "Crunching numbers...",
];

export function Loader() {
    const [text, setText] = useState(fillerTexts[0]);

    useEffect(() => {
        const interval = setInterval(() => {
            const randomText =
                fillerTexts[Math.floor(Math.random() * fillerTexts.length)];
            setText(randomText);
        }, 1500); // change text every 1.5s

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
            <Card className="flex flex-col items-center justify-center p-10 shadow-2xl rounded-2xl max-w-md">
                <CardContent className="flex flex-col items-center gap-6">
                    <LoaderCircle className="w-20 h-20 text-blue-500 animate-spin" />
                    <p className=" text-center text-lg">{text}</p>
                </CardContent>
            </Card>
        </div>
    );
}
