from fastapi import FastAPI
import aio_pika
from aio_pika.pool import Pool
import logging
from contextlib import asynccontextmanager
from app.utils.logging import setup_logging
from app.routes.alerts import create_alert_router
from app.routes.queues import create_queue_router
from app.routes.services import create_service_router
from app.utils.config import load_config
from app.utils.rabbitmq import init_connection_pool, close_connection_pool, listen_queues

# Load configuration
config = load_config()
setup_logging()

# Setup lifespan events 
@asynccontextmanager
async def lifespan(app: FastAPI):
    global connection_pool
    try:
        logging.info("Initializing RabbitMQ connection pool")
        # Initialize the RabbitMQ connection pool
        connection_pool = await init_connection_pool()
        
        # Start listening to queues using the initialized connection pool
        await listen_queues()
        
        #logging.info("Startup completed successfully")
        logging.info("FastAPI app initialized and ready to handle requests")
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        raise
    yield
    try:
        logging.info("Closing RabbitMQ connection pool")
        # Close the RabbitMQ connection pool
        await close_connection_pool()
        
        logging.info("Shutdown completed successfully")
    except Exception as e:
        logging.error(f"Failed to shut down application: {e}")
        raise

# Initialize the FastAPI application with metadata from the configuration
app = FastAPI(
    title=config["title"],
    description=config["description"],
    debug=config["debug_mode"],  # Enable debug mode if true in YAML
    lifespan=lifespan
)

# Global variable to hold the connection pool for RabbitMQ
connection_pool: Pool[aio_pika.Connection] = None

# Register routers with the FastAPI application
logging.info("Registering routes for alerts, queues, and alert routers")
create_alert_router(app)
create_queue_router(app)
create_service_router(app)

