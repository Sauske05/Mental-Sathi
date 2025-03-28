import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MentalSathi.settings')
CELERY_BROKER_URL = 'redis://localhost:6379/0'
app = Celery('MentalSathi', broker=CELERY_BROKER_URL, backend=CELERY_BROKER_URL)
app.conf.timezone = 'Asia/Kathmandu'
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    'send-email-every-day': {
        'task': 'users.tasks.send_scheduled_email',
        'schedule': crontab(hour='10', minute='0'),
    },
}