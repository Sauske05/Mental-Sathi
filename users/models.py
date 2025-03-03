import random
import string

from django.db import models
from django.contrib.auth.hashers import make_password
import datetime
import pytz
# Create your models here.


class User(models.Model):
    #user_id = models.CharField(max_length=10,primary_key=True, default=None)
    user_name = models.CharField(max_length = 120, primary_key = True)
    email = models.CharField(max_length=120, unique = True)
    password = models.CharField(max_length=120)
    #created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=datetime.datetime.now())

    def save(self, *args, **kwargs):
        # if not self.user_id:
        #     self.user_id = self.generate_user_id()
        # Check if the password is already hashed
        if not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    # @staticmethod
    # def generate_user_id():
    #     while True:
    #         new_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    #         if not User.objects.filter(user_id=new_id).exists():
    #             return new_id
NEPAL_TZ = pytz.timezone('Asia/Kathmandu')
class DashboardRecords(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, to_field='user_name')
    number_of_login_days = models.IntegerField()
    login_streak = models.IntegerField()
    positive_streak = models.IntegerField()
    last_login_date = models.DateTimeField(default=None, null=True)




