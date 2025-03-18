from fastapi import FastAPI, HTTPException, Depends
from app.utils.config import load_config
from app.utils.auth import validate_api_key
from app.schemas.services import Service
import logging
from app.utils.logging import setup_logging

# Initialize logger
setup_logging()
config = load_config()

# Ensure queues are loaded correctly
try:
    services = config["services"]
except KeyError as e:
    logging.error(f"Configuration error: {e}")
    raise SystemExit("Failed to load services configuration")

def create_service_router(app: FastAPI):
    @app.get("/services", response_model=list[Service], summary="List all services")
    async def list_all_services(api_key: str = Depends(validate_api_key)):
        """
        Retrieve a list of all services.
        """
        return services

    @app.get("/services/{service_id}", response_model=Service, summary="Get a service by ID")
    async def list_service(service_id: int, api_key: str = Depends(validate_api_key)):
        """
        Retrieve a specific service by its ID.

        Parameters:
        - **service_id**: The unique identifier of the queue.
        """
        selected_service = next((service for service in services if service["id"] == service_id), None)
        if not selected_service: 
            raise HTTPException(status_code=404, detail="Service Not Found")
        return selected_service