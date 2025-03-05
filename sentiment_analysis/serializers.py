from rest_framework import serializers
from .models import SentimentModel

class SentimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentimentModel
        fields = '__all__'