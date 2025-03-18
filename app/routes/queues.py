from fastapi import FastAPI, HTTPException, Depends
from app.utils.config import load_config
from app.utils.auth import validate_api_key
from app.schemas.queues import Queue
import logging
from app.utils.logging import setup_logging

# Initialize logger
setup_logging()
config = load_config()

# Ensure queues are loaded correctly
try:
    queues = config["queues"]
except KeyError as e:
    logging.error(f"Configuration error: {e}")
    raise SystemExit("Failed to load queues configuration")

def create_queue_router(app: FastAPI):
    @app.get("/queues", response_model=list[Queue], summary="List all queues")
    async def list_all_queues(api_key: str = Depends(validate_api_key)):
        """
        Retrieve a list of all queues.
        """
        return queues
    
    @app.get("/queues/{queue_id}", response_model=Queue, summary="Get a queue by ID")
    async def get_queue(queue_id: int, api_key: str = Depends(validate_api_key)):
        """
        Retrieve a specific queue by its ID.

        Parameters:
        - **queue_id**: The unique identifier of the queue.
        """
        selected_queue = next((queue for queue in queues if queue["id"] == queue_id), None)
        if not selected_queue: 
            raise HTTPException(status_code=404, detail="Queue Not Found")
        return selected_queue