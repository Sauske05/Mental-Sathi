from django.db import models
import datetime
from users.models import User
from django.contrib.sessions.models import Session
from django.utils.timezone import now
# Create your models here.
class Chat(models.Model):
    #user_id = models.ForeignKey(, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=255)
    #assistant_text = models.TextField()
    #user_query = models.TextField()
    context = models.TextField()
    session_id = models.ForeignKey(Session, on_delete = models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
