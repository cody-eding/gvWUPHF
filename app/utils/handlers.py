import smtplib
import logging
from fastapi import HTTPException
import requests
import json
import mistune
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from app.utils.config import load_config
from app.utils.zoom import get_zoom_token

config = load_config()

def send_zoom_webhook(webhook_url, authorization, message):
    """
    Sends a message to a Zoom Team chat.

    :param webhook_url: The URL of the MS Teams webhook.
    :param message: The message to be sent as a string or a dictionary with JSON payload.
    """
    headers = {
        'Authorization': authorization,
        'Content-Type': 'application/json'
    }

    payload = {
        "content": {
            "settings": {
                "default_sidebar_color": ("#FF0000" if message['severity'] == "critical" else
                                    "FFFF00" if message['severity'] == "warning" else
                                    "#00FF00" if message['severity'] == "ok" else
                                    "#0000FF")
            },
            "head": {
                "text": message['title'],
                "style": {
                    "bold": "true"
                }
            },
            "body": [
                {
                    "type": "message",
                    "is_markdown_support": "true",
                    "text": message['message']
                }
            ]
        }
    }

    # Conditionally add the "View More Details" entry
    if message.get('url'):
        payload["content"]["body"].append({
            "type": "message",
            "text": "View More Details",
            "link": message['url']
        })
        
    def get_zoom_jid_from_email(email):
        # get a zoom token
        zoom_token = get_zoom_token()  
        zoom_access_token = zoom_token['access_token']
        zoom_header_config = zoom_token['header_config']
        
        url = f"https://api.zoom.us/v2/users/{email}"
        # Make the API request
        response = requests.get(url, headers=zoom_header_config)
        
        if response.status_code == 200:
            user_data = response.json()
            # Extract the JID from the user data
            jid = user_data.get('jid')
            return jid
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    # Conditionally add the "View More Details" entry
    if message.get('tagged_users'):
        # Initialize an empty list
        user_list = []
        
        for user in message.get('tagged_users'):
            jid = get_zoom_jid_from_email(user['id'])
            user_list.append(f"<!{jid}|{user['name']}>")
            user_string = " ".join(user_list)
 
        payload["content"]["body"].insert(0, {
            "type": "message",
            "is_markdown_support": "true",
            "text": user_string
        })

            
    # Print the final payload
    print(payload)
    try:
        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        return {"status": "success", "message": "Message sent successfully!"}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")

def send_msteams_webhook(webhook_url, message):
    """
    Sends a message to an MS Teams webhook.

    :param webhook_url: The URL of the MS Teams webhook.
    :param message: The message to be sent as a string or a dictionary with JSON payload.
    """
    headers = {
        'Content-Type': 'application/json'
    }

    # Assuming message is a dictionary with keys 'title', 'severity', 'message', 'url', and 'tagged_users'
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": "null",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "Container",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": message['title'],
                                    "size": "Large",
                                    "weight": "Bolder"
                                }
                            ],
                            "style": ("attention" if message['severity'] == "critical" else
                                    "warning" if message['severity'] == "warning" else
                                    "good" if message['severity'] == "ok" else
                                    "accent"),
                            "bleed": True
                        },
                        {
                            "type": "TextBlock",
                            "text": message['message'],
                            "wrap": True
                        }
                    ],
                }
            }
        ]
    }

    # Conditionally add the actions key if url is not empty
    if message.get('url'):
        payload['attachments'][0]['content']['actions'] = [
            {
                "type": "Action.OpenUrl",
                "title": "View More Details",
                "url": message['url']
            }
        ]

    # Conditionally add the msteams key if tagged_users is not empty
    if message.get('tagged_users'):
        entities = [
            {
                "type": "mention",
                "text": f"<at>{user['name']}</at>",
                "mentioned": {
                    "id": user['id'],
                    "name": user['name']
                }
            }
            for user in message.get('tagged_users')
        ]
        payload['attachments'][0]['content']['msteams'] = {
            "entities": entities
        }


    # Optionally, add the tagged users to the body if they exist
    if message.get('tagged_users'):
        tagged_user_text = ' '.join(f"<at>{user['name']}</at>" for user in message['tagged_users'])
        payload['attachments'][0]['content']['body'].insert(1, {
            "type": "TextBlock",
            "text": tagged_user_text,
            "wrap": True
    })

    # Print the final payload
    #print(payload)
    try:
        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        return {"status": "success", "message": "Message sent successfully!"}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")


def send_smtp_email(recipient_email, message, use_tls=False):
    """Sends an email using SMTP.

    Args:
        sender_email (str): The sender's email address.
        sender_password (str): The sender's email password.
        recipient_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body of the email.
    """
    
    body = mistune.html(message['message'])

    # Create the sender's formatted address with a display name
    from_name = config['title']
    from_address = formataddr((from_name, config['smtp_from_address']))

    msg = MIMEMultipart()
    msg = MIMEText(body, 'html')
    if message.get('severity'):
        msg['Subject'] = f"{message['severity'].upper()} - {message['title']}"
    else:
        msg['Subject'] = message['title']   
    msg['From'] = from_address
    msg['To'] = recipient_email

    try:
        if use_tls:
            smtp_server = smtplib.SMTP_SSL(config['smtp_server'], config['smtp_port']) 
        else:
            smtp_server = smtplib.SMTP(config['smtp_server'], config['smtp_port']) 

        smtp_server.sendmail(config['smtp_server'], recipient_email, msg.as_string())
        logging.info("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")