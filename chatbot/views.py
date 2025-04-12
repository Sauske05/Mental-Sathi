from django.shortcuts import render, redirect
from users import views as user_views
from MentalSathi import views as root_views
from django.urls import reverse
# Create your views here.
from users.models import CustomUser, UserProfile
def chat_redirect(request):
    session_id = request.session.session_key
    if not session_id:
        return redirect(root_views.index)

    user_id = request.session['user_id']
    #user_id = user if user is not None else "guest"

    # Create a unique room name
    room_name = f"{session_id}_{user_id}"
    #room_name = 'arun'

    return redirect(chat_room, room_name = room_name)


def chat_room(request, room_name):
    user_id = request.session['user_id']
    user_obj = CustomUser.objects.get(email=user_id)

    user_name = UserProfile.objects.filter(user_email=user_obj).first().first_name if UserProfile.objects.filter(
        user_email=user_obj).exists() else user_id

    return render(request, "chatbot/room.html", {"room_name": room_name, 'user_name': user_name,
                                                 'user_first_name': user_name})