import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import make_password
import datetime
import pytz
from .manager import UserManager
# Create your models here.


class User(models.Model):
    user_name = models.CharField(max_length=120, primary_key=True)
    email = models.CharField(max_length=120, unique=True)
    password = models.CharField(max_length=120, blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    profile_picture = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField('email address',unique=True)
    profile_picture = models.URLField(blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['first_name', 'last_name']
    #objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

NEPAL_TZ = pytz.timezone('Asia/Kathmandu')
class DashboardRecords(models.Model):
    user_name = models.ForeignKey(CustomUser, on_delete=models.CASCADE, to_field='email')
    number_of_login_days = models.IntegerField()
    login_streak = models.IntegerField()
    positive_streak = models.IntegerField()
    last_login_date = models.DateTimeField(default=None, null=True)




