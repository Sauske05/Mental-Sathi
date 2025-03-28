from celery import shared_task
from django.core.mail import send_mail
import os
from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
from sentiment_analysis.views import report_generator
from django.core.mail import EmailMessage
from users.models import CustomUser
load_dotenv()
@shared_task
def test_celery():
    print('Celery run during server start up!')

@shared_task
def send_scheduled_email():
    subject = "Automated Report from MentalSathi"
    message = "Please find the attached report."
    from_email = os.getenv("APP_EMAIL")
    users = CustomUser.objects.all().values_list('email', flat=True)
    users = list(users)
    print('The list of users being sent the scheduled email: ', users)
    recipient_list = users

    # Generate the PDF report
    for email in recipient_list:
        pdf_content = report_generator(email)

        # Create a temporary file to store the generated PDF
        with NamedTemporaryFile(delete=False, suffix='.pdf') as tmpfile:
            tmpfile.write(pdf_content)  # Write the content to the temporary file
            tmpfile_path = tmpfile.name

        email = EmailMessage(
            subject,
            message,
            from_email,
            recipient_list
        )

        email.attach_file(tmpfile_path)

        email.send()

        os.remove(tmpfile_path)

        return f"Email with report sent successfully to {email}!"