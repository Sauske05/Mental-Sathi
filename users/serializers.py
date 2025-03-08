from rest_framework import serializers

from .models import User, CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_name',
            'email',
            'password',
            'created_at'
        ]
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ["password"]

