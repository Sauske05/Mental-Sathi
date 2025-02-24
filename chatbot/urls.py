from django.urls import path

from . import views


urlpatterns = [
    path("", views.chat_redirect,name="chat_old", ),
path("<str:room_name>/", views.chat_room, name="room"),
]