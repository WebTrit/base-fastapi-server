from typing import List, Optional
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
import datetime

router = APIRouter(
        # no logging for health check
        # route_class=RouteWithLogging,
        prefix="", tags=["monitoring"])


@router.get("/health")
async def check_health():
    """Health check endpoint to verify the service is running"""
    return {
        "status": "healthy",
        "service": "base-fastapi",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

def initialize(config):
    """Initialize the module and the business logic module"""
    pass