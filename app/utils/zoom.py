import base64
import requests
import time
from app.utils.config import load_config

config = load_config()

# Access configuration variables
ZOOM_ACCOUNT_ID = config['zoom_account_id']
ZOOM_CLIENT_ID = config['zoom_client_id']
ZOOM_CLIENT_SECRET = config['zoom_client_secret']
ZOOM_OAUTH_ENDPOINT = "https://zoom.us/oauth/token"

# Initialize cached token and expiration time variables
cached_zoom_token = None
zoom_token_expiration = None

def get_zoom_token():
    global cached_zoom_token, zoom_token_expiration

    #  Check if the token is cached and not expired
    if cached_zoom_token and zoom_token_expiration and zoom_token_expiration > time.time():
        return {
            'access_token': cached_zoom_token,
            'expires_in': zoom_token_expiration - time.time(),
            'header_config': {
                'Authorization': f'Bearer {cached_zoom_token}',
                'Content-Type': 'application/json'
            },
            'error': None
        }
    try:
        # Create the authorization header
        auth_string = f"{ZOOM_CLIENT_ID}:{ZOOM_CLIENT_SECRET}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # Prepare the data for the POST request
        data = {
            'grant_type': 'account_credentials',
            'account_id': ZOOM_ACCOUNT_ID
        }
        # Make the POST request
        response = requests.post(ZOOM_OAUTH_ENDPOINT, headers=headers, data=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Parse the JSON response
        result = response.json()
        access_token = result.get('access_token')
        expires_in = result.get('expires_in')

        # Update the cached token and expiration
        cached_zoom_token = access_token
        zoom_token_expiration = time.time() + expires_in

        header_config = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
        return {
            'access_token': access_token, 
            'expires_in': expires_in,
            'header_config': header_config, 
            'error': None}
    except requests.RequestException as error:
        return {
            'access_token': None, 
            'expires_in': None, 
            'error': str(error)}
