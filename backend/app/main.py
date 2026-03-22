from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import get_settings
from app.database import engine, Base
from app.routers.users import router as auth_router, profile_router
from app.routers.appointments import router as appointments_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CitaFácil API",
    description="One-click appointment booking for INM & SRE",
    version="1.0.0",
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(appointments_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "citafacil"}
