import requests

def send_whatsapp_message(from_number, to_number, message):
    # WhatsApp Business API endpoint
    url = 'https://graph.facebook.com/v16.0/{whatsapp-business-id}/messages'  # Replace {whatsapp-business-id} with your business ID

    # Authentication (use your WhatsApp API access token)
    headers = {
        'Authorization': 'Bearer {your-access-token}',  # Replace with your access token
        'Content-Type': 'application/json',
    }

    # Message payload
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message,
        },
    }

    # Send the request
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f'Message sent successfully to {to_number}')
    else:
        print(f'Failed to send message: {response.text}')