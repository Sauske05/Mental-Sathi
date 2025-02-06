from django.shortcuts import render

# Create your views here.
from django.shortcuts import render


def index(request):
    return render(request, "chatbot/chatbot.html")


def room(request, room_name):
    return render(request, "chatbot/room.html", {"room_name": room_name})