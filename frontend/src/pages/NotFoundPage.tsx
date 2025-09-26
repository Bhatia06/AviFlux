import { Button } from "@/components/ui/button";

export default function NotFoundPage() {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-sky-50 to-blue-100 p-6 text-center">
            <h1 className="text-[12rem] font-extrabold text-blue-600 leading-none select-none drop-shadow-lg">
                404
            </h1>
            <h2 className="text-4xl md:text-6xl font-bold text-gray-800 mt-4">
                Oops! Page Not Found
            </h2>
            <p className="text-gray-600 mt-2 max-w-xl">
                The page you're looking for doesn’t exist or has been moved.
                Maybe try going back to the homepage?
            </p>

            <div className="mt-6 flex gap-4 flex-wrap justify-center">
                <Button
                    onClick={() => (window.location.href = "/")}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                    Go Home
                </Button>
                <Button
                    variant="outline"
                    onClick={() => window.history.back()}
                    className="text-blue-600 border-blue-600 hover:bg-blue-50"
                >
                    Go Back
                </Button>
            </div>
        </div>
    );
}
