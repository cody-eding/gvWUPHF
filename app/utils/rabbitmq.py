import aio_pika
from aio_pika.pool import Pool
import asyncio
import logging
from app.utils.gateway import on_message
from app.utils.config import load_config

# load the configuration
config = load_config()

def get_connection_pool() -> Pool[aio_pika.Connection]:
    return connection_pool

async def init_connection_pool():
    """
    Initializes the RabbitMQ connection pool.
    
    This function sets up a connection pool with a maximum size of 20 connections
    using the provided configuration settings.
    """
    global connection_pool
    try:
        loop = asyncio.get_event_loop()
        connection_pool = Pool(
            lambda: aio_pika.connect_robust(config['rabbitmq_conn'], loop=loop),
            max_size=20
        )
        logging.info("Connection pool initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize connection pool: {e}")
        raise
    
async def close_connection_pool():
    """
    Closes the RabbitMQ connection pool.
    
    This function ensures that all connections in the pool are properly closed
    and logs the completion of this operation.
    """
    global connection_pool
    try:
        if connection_pool:
            await connection_pool.close()
            logging.info("Connection pool closed successfully")
            connection_pool = None
    except Exception as e:
        logging.error(f"Failed to close connection pool: {e}")
        raise
        
async def listen_queues():
    """
    Declares and sets up consumers for the specified queues.
    
    This function acquires a connection from the pool, declares each queue,
    and attaches a message consumer to it using the `on_message` callback.
    """
    try:
        async with connection_pool.acquire() as connection:
            channel = await connection.channel()
            for queue in config['queues']:
                declared_queue = await channel.declare_queue(queue['name'])
                await declared_queue.consume(on_message)
            logging.info("Queues and consumers set up successfully")
    except Exception as e:
        logging.error(f"Failed to set up queues and consumers: {e}")
        raise