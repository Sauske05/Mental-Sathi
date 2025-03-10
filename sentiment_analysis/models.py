from django.db import models
from users.models import CustomUser
import datetime
# Create your models here.
class SentimentModel(models.Model):
    user_name = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field='email')
    sentiment_data  = models.CharField(max_length=120, )
    recommendation_text = models.TextField()
    user_query = models.TextField()
    sentiment_score = models.FloatField(default = None)
    date_time = models.DateTimeField(default=datetime.datetime.now())
    query_sentiment = models.CharField(max_length=120, default='')

