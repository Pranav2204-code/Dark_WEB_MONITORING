"""API v1 router"""
from fastapi import APIRouter
from .threats import router as threats_router
from .rules import router as rules_router

api_router = APIRouter()

api_router.include_router(threats_router, prefix="/threats", tags=["threats"])
api_router.include_router(rules_router, prefix="/rules", tags=["monitoring-rules"])
