# app/utils/auth.py

from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from app.utils.config import load_config
import logging
from app.utils.logging import setup_logging

config = load_config()
valid_api_keys = config["api_keys"]

api_key_header = APIKeyHeader(name="X-API-Key")

def validate_api_key(api_key_header: str = Security(api_key_header)):
    """
    Validates the provided API key.

    Args:
        api_key_header (str): The API key extracted from the request header.

    Returns:
        bool: True if the API key is valid, raises HTTPException otherwise.
    
    Raises:
        HTTPException: If the API key is invalid.
    """
    logging.info(f"Validating API Key: {api_key_header}")
    
    valid_key = api_key_header in valid_api_keys
    if not valid_key:
        logging.error(f"Invalid API Key provided: {api_key_header}")
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    logging.info("API Key validation successful")
    return valid_key
