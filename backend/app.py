from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(title="AviFlux API", version="0.1.0")

# Allow browser apps (React dev servers) to call this API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # CRA default
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
def read_root():
    return {"message": "AviFlux API is running"}


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok"}


@app.get("/api/greet", tags=["demo"])
def greet(name: str = "World"):
    return {"greeting": f"Hello, {name}!"}


class EchoPayload(BaseModel):
    message: str


@app.post("/api/echo", tags=["demo"])
def echo(payload: EchoPayload):
    return {"you_sent": payload.message}


if __name__ == "__main__":
    # Run with: python app.py (from backend directory)
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

