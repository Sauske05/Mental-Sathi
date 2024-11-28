from django.db import models
import datetime
from users.models import User
from django.contrib.sessions.models import Session
# Create your models here.
class Chat(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    assistant_text = models.TextField()
    user_query = models.TextField()
    session_id = models.ForeignKey(Session, on_delete = models.CASCADE)
    date_time = models.DateTimeField(default=datetime.datetime.now())
