import logging
import uuid
import importlib
from typing import List
from fastapi import APIRouter, Depends, FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app_config import AppConfig

config = AppConfig()

VERSION = "0.1.1"
app = FastAPI(
    title="Basic FastAPI",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redocs",
    ignore_trailing_slash=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load main routes + additional routes defined in the configuration
routes_to_load = ["health"] + \
        config.get_conf_val("ROUTES", "ADD", default="").split(",")
for route_name in routes_to_load:
    route_name = route_name.strip()
    if route_name:
        try:
            # Import the router module dynamically
            router_module = importlib.import_module(f"routers.{route_name}")
            if hasattr(router_module, "initialize"):
                router_module.initialize(config)

            if hasattr(router_module, 'router'):
                app.include_router(router_module.router)
                logging.info(f"Successfully loaded router from {route_name}")
            else:
                logging.error(f"Router module {route_name} does not contain a 'router' attribute")
        except ImportError as e:
            logging.error(f"Failed to import router module {route_name}: {str(e)}")
        except Exception as e:
            logging.error(f"Error loading router from {route_name}: {str(e)}")


if __name__ == "__main__":
    pass