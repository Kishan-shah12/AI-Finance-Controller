import uvicorn
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import init_db, get_db
from app.providers.razorpay_provider import RazorpayProvider

# Routers
from app.api import evaluation, reconciliation, exceptions, agent, providers

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="ReconAI API", version="1.0.0", lifespan=lifespan)

# Configure CORS for Next.js frontend
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip().rstrip('/') for origin in allowed_origins_str.split(",") if origin.strip()]

# Always ensure local dev and known production Vercel origins are permitted as fallback if env var missed it
default_origins = [
    "http://localhost:3000",
    "https://reconai-3r0e9x0jx-kishan-sah-s-projects.vercel.app",
    "https://reconai-3r0e9x0jx-kishan-s-projects.vercel.app",
]
for origin in default_origins:
    if origin not in allowed_origins:
        allowed_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database handled by lifespan


# Include Routers
app.include_router(evaluation.router)
app.include_router(reconciliation.router)
app.include_router(exceptions.router)
app.include_router(agent.router)
app.include_router(providers.router)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "reconai_backend"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/health/dependencies")
def health_dependencies(db: Session = Depends(get_db)):
    dependencies = {}
    
    # 1. Database
    try:
        db.execute(text("SELECT 1"))
        dependencies["database"] = "HEALTHY"
    except Exception:
        dependencies["database"] = "ERROR"
        
    # 2. Synthetic Provider
    dependencies["synthetic_provider"] = "HEALTHY"
    
    # 3. Razorpay Provider
    try:
        rzp = RazorpayProvider()
        status = rzp.get_status()
        if not status["configured"]:
            dependencies["razorpay_provider"] = "NOT_CONFIGURED"
        elif status["reachable"]:
            dependencies["razorpay_provider"] = "HEALTHY"
        else:
            dependencies["razorpay_provider"] = "UNAVAILABLE"
    except Exception:
        dependencies["razorpay_provider"] = "ERROR"
        
    # 4. LLM Provider
    gemini_key = os.getenv("GEMINI_API_KEY")
    nemotron_key = os.getenv("NEMOTRON_API_KEY")
    if gemini_key or nemotron_key:
        dependencies["llm_provider"] = "HEALTHY" # Simplified check
    else:
        dependencies["llm_provider"] = "NOT_CONFIGURED"
        
    return dependencies

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
