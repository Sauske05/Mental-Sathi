from django.db import models
from users.models import User
import datetime
# Create your models here.
class SentimentModel(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_name')
    sentiment_data  = models.CharField(max_length=120, )
    recommendation_text = models.TextField()
    user_query = models.TextField()
    date_time = models.DateTimeField(default=datetime.datetime.now())
    query_sentiment = models.CharField(max_length=120, default='')