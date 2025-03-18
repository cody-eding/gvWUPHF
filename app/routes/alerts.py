import logging
from fastapi import FastAPI, HTTPException, Depends
import aio_pika
from app.schemas.alerts import Alert
from app.utils.config import load_config
from app.utils.auth import validate_api_key
from app.utils.rabbitmq import get_connection_pool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration at module level for efficiency
config = load_config()

# Create a set of valid queue IDs for quick lookup
valid_queue_ids = {queue['id'] for queue in config['queues']}

def validate_queue(queue_id: str) -> bool:
    """Validate the queue id."""
    logger.debug(f"Validating queue ID: {queue_id}")
    return queue_id in valid_queue_ids

async def publish_alert(alert: Alert, queue_name: str, service_ids: list) -> None:
            
    """Publish an alert to RabbitMQ."""
    try:
        
        conn_pool = get_connection_pool()
        async with conn_pool.acquire() as connection:
            channel = await connection.channel()
            # Declare a queue to ensure it exists
            logger.info(f"Declaring queue: {queue_name}")
            await channel.declare_queue(queue_name)

            # Convert the alert to JSON and encode it as bytes
            message_body = (alert.model_dump_json()).encode("utf-8")
            logger.debug(f"Message body: {message_body}")

            # Publish the message to the queue with service_ids in headers
            logger.info(f"Publishing message to queue: {queue_name} with routing key: {queue_name}")
            await channel.default_exchange.publish(
                aio_pika.Message(body=message_body, headers={'service_ids': service_ids}),
                routing_key=queue_name
            )
    except Exception as e:
        logger.error(f"Error publishing alert: {e}", exc_info=True)
        raise

def create_alert_router(app: FastAPI) -> None:
    """Create the alert router."""
    @app.post("/alert/")
    async def create_alert(alert: Alert, api_key: str = Depends(validate_api_key)):
        """
        Create an alert and publish it to the specified queue.

        Parameters:
            alert (Alert): The alert data to be published.
        
        Returns:
            dict: A success message along with the created alert if successful.
        
        Raises:
            HTTPException: If the provided queue ID is invalid.
        """
        try:
            # Validate the queue_id in the alert
            if not validate_queue(alert.queue_id):
                logger.error(f"Invalid queue ID: {alert.queue_id}")
                raise HTTPException(status_code=400, detail="Invalid queue id.")
            
            # Find the queue details
            queue_details = next((queue for queue in config['queues'] if queue['id'] == alert.queue_id), None)
            if not queue_details:
                logger.error(f"No details found for queue ID: {alert.queue_id}")
                raise HTTPException(status_code=400, detail="No details found for queue id.")
            
            # Publish the alert
            logger.info(f"Publishing alert to queue: {alert.queue_id}")
            await publish_alert(alert, queue_details['name'], queue_details.get('service_ids', []))
            
            logger.info("Alert published successfully")
            return {"message": "Alert published successfully", "alert": alert.dict()}
        except Exception as e:
            logger.error(f"Error processing alert: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")