# utils.py
from twilio.rest import Client
import os
from dotenv import load_dotenv
load_dotenv()


def send_otp_sms(phone_number, otp):
    client = Client(os.getenv('TWILIGHT_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))

    message = client.messages.create(
        body=f'Your OTP for password reset is: {otp}',
        messaging_service_sid=os.getenv('TWILIO_SERVICE_SID'),
        to=phone_number
    )
    return message.sid