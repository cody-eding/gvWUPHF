import aio_pika
import json
import logging
from app.utils.config import load_config
from app.utils.handlers import send_smtp_email, send_msteams_webhook, send_zoom_webhook

# Load configuration
config = load_config()
valid_service_ids = {service['id'] for service in config['services']}

def validate_service(service_id):
    return service_id in valid_service_ids

async def on_message(message: aio_pika.IncomingMessage):
    try:
        logging.info("Received message in %s queue", message.routing_key)
        
        # Decode and parse the message body
        message_json = json.loads(message.body.decode("utf-8"))
        
        for service_id in message.headers.get('service_ids', []):
            if validate_service(service_id):
                selected_service = next(
                    (service for service in config['services'] if service["id"] == service_id),
                    None
                )
                
                if not selected_service:
                    logging.warning("Service with id %s not found", service_id)
                    continue
                
                logging.info("Selected service id=%s, type=%s", selected_service['id'], selected_service['type'])
                
                if selected_service['type'] == 'zoom':
                    send_zoom_webhook(selected_service['recipient'], selected_service['authorization'], message_json)
                elif selected_service['type'] == 'msteams':
                    send_msteams_webhook(selected_service['recipient'], message_json)
                elif selected_service['type'] == 'smtp':
                    send_smtp_email(selected_service['recipient'], message_json)
            else:
                logging.warning("Invalid service id: %s", service_id)
        
        await message.ack()
    except Exception as e:
        logging.error("An error occurred while processing the message: %s", e)
        await message.nack(requeue=True)  # Requeue the message for further processing
