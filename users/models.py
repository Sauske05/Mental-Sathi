from django.db import models

# Create your models here.
class User(models.Model):
    user_name = models.CharField(max_length = 120, primary_key=True)
    password = models.CharField(max_length=120)
    email = models.CharField(max_length=120)