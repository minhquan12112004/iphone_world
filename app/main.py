from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.api.v1.api import api_router
from app.core.redis_client import redis_client

app = FastAPI(
    title=settings.app_name,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Exception Handlers
setup_exception_handlers(app)

# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)

@app.on_event("startup")
async def startup_event():
    await redis_client.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await redis_client.disconnect()
