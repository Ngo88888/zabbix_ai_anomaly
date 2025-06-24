"""
Main entry point for the Zabbix AI Anomaly Detection application
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import BACKEND_HOST, BACKEND_PORT
from app.db.database import init_db

# Create FastAPI app
app = FastAPI(
    title="Zabbix AI Anomaly Detection API",
    description="API for detecting anomalies in Zabbix monitoring data",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """
    Initialize the database on startup
    """
    init_db()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=BACKEND_HOST,
        port=BACKEND_PORT,
        reload=True,
    ) 