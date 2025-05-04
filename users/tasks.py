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

    for email in users:
        if email == 'admin@mentalsathi.com.np':
            continue

        # Generate the PDF report specific to this user
        pdf_content = report_generator(email)

        # Create a temporary file to store the generated PDF
        with NamedTemporaryFile(delete=False, suffix='.pdf') as tmpfile:
            tmpfile.write(pdf_content)
            tmpfile_path = tmpfile.name

        # Create and send the email to this specific user
        email_msg = EmailMessage(
            subject,
            message,
            from_email,
            [email]  # Send only to this user
        )
        email_msg.attach_file(tmpfile_path)
        email_msg.send()

        # Clean up the temporary file
        os.remove(tmpfile_path)

    # Return a success message after all emails are sent (optional for Celery tasks)
    return "All emails sent successfully!"