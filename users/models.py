from django.db import models
from django.contrib.auth.hashers import make_password
# Create your models here.
class User(models.Model):
    user_name = models.CharField(max_length = 120, primary_key=True)
    password = models.CharField(max_length=120)
    email = models.CharField(max_length=120)

    def save(self, *args, **kwargs):
        # Check if the password is already hashed
        if not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)  # Hash the password
        super().save(*args, **kwargs)