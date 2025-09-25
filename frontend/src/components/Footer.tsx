export function Footer() {
  return (
    <footer className="border-t py-6 md:py-0">
      <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
        <div className="flex flex-col items-center gap-4 px-8 md:flex-row md:gap-2 md:px-0">
          <div className="h-8 w-8">
            {/* Add your logo here */}
          </div>
          <p className="text-center text-sm leading-loose md:text-left">
            Built by{" "}
            <a
              href="#"
              target="_blank"
              rel="noreferrer"
              className="font-medium underline underline-offset-4"
            >
              Your Name
            </a>
            . The source code is available on{" "}
            <a
              href="#"
              target="_blank"
              rel="noreferrer"
              className="font-medium underline underline-offset-4"
            >
              GitHub
            </a>
            .
          </p>
        </div>
        <div className="flex flex-col items-center gap-4 px-8 md:flex-row md:gap-2 md:px-0">
          <a
            href="#"
            className="text-sm font-medium underline underline-offset-4"
          >
            Terms & Conditions
          </a>
          <span className="text-sm text-muted-foreground">|</span>
          <a
            href="https://opensource.org/licenses/MIT"
            target="_blank"
            rel="noreferrer"
            className="text-sm font-medium underline underline-offset-4"
          >
            MIT License
          </a>
        </div>
      </div>
    </footer>
  );
}