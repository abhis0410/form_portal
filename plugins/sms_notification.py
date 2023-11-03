"""
-----------------This Code is written by-----------------
---------------------Abhinav Singla----------------------
"""

#Code Starts Here
from twilio.rest import Client

def send_sms_notification(form, response):
    twilio_account_sid = ''
    twilio_auth_token = ''
    twilio_phone_number = ''

    client = Client(twilio_account_sid, twilio_auth_token)

    customer_phone_number = response.customer_phone  # Update this with your data structure

    sms_message = f"Thank you for participating in our exercise! Your details: Name: {response.customer_name}, Email: {response.customer_email}, Address: {response.customer_address}"

    message = client.messages.create(
        body=sms_message,
        from_=twilio_phone_number,
        to=customer_phone_number
    )

    return f"SMS sent with message SID: {message.sid}"

