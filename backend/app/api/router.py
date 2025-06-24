"""
API router for the Zabbix AI Anomaly Detection application
"""
from fastapi import APIRouter
from .endpoints import router as endpoints_router

api_router = APIRouter()

api_router.include_router(endpoints_router, tags=["zabbix"]) 