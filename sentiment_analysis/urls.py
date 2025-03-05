from django.urls import path, include

from .views import *

urlpatterns = [

path('fetch_sentiment_data/<str:user_name>', get_user_sentiment_data, name='fetch_user_sentiment_data'),
]