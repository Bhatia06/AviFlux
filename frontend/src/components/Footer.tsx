export default function Footer() {
    return (
        <footer className="border-t mt-10">
            <div className="container mx-auto flex flex-col md:flex-row justify-between items-center p-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                    <img src="/your-logo.png" alt="Logo" className="h-6 w-6" />
                    <span>© 2025 Flight Planner</span>
                </div>
                <div>Built by Team BitFlux</div>
                <div className="flex gap-4">
                    <a href="/terms">Terms & Conditions</a>
                    <a href="/license">MIT License</a>
                </div>
            </div>
        </footer>
    );
}
