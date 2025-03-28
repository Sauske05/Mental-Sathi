from celery import shared_task
from django.core.mail import send_mail
import os
from dotenv import load_dotenv
load_dotenv()
@shared_task
def test_celery():
    print('Celery run during server start up!')

@shared_task
def send_scheduled_email():
    subject = "Automated Email from MentalSathi"
    message = "This is a scheduled email."
    from_email = os.getenv("APP_EMAIL")
    recipient_list = ["honkainew123@gmail.com"]

    send_mail(subject, message, from_email, recipient_list)
    return "Email sent successfully!"