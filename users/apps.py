from django.apps import AppConfig
from celery import current_app

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        import users.signals
        from users.tasks import test_celery
        current_app.send_task("users.tasks.test_celery")
