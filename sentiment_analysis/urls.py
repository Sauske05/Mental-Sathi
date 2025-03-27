from django.urls import path, include

from .views import *

urlpatterns = [

path('fetch_sentiment_data/<str:user_email>', get_user_sentiment_data, name='fetch_user_sentiment_data'),
path('sentiment-report/<str:user_id>/pdf/', generate_sentiment_report_pdf, name='sentiment_report_pdf'),
path('fetch_sentimentScore/', fetch_sentimentScore, name='fetch_sentimentScore'),
path('fetch_bar_sentiment_data/', fetch_bar_sentiment_data, name = 'fetch_bar_sentiment_data'),
path('fetch_admin_table_data/', fetch_admin_table_data, name = 'fetch_admin_table_data'),
path('fetch_mood_saved_data/', fetch_mood_saved_data, name = 'fetch_mood_saved_data'),


]