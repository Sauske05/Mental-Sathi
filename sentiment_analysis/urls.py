from django.urls import path, include

from .views import *

urlpatterns = [

path('fetch_sentiment_data/<str:user_email>', get_user_sentiment_data, name='fetch_user_sentiment_data'),
path('sentiment-report/<str:user_id>/pdf/', generate_sentiment_report_pdf, name='sentiment_report_pdf'),

]