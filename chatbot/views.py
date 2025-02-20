from django.shortcuts import render, redirect
from django.urls import reverse
# Create your views here.



def chat_redirect(request):
    session_id = request.session.session_key
    if not session_id:
        request.session.save()
        session_id = request.session.session_key

    # Get user ID (or set to "guest" if not authenticated)
    user = request.user
    user_id = user.id if user.is_authenticated else "guest"

    # Create a unique room name
    room_name = f"{session_id}_{user_id}"

    # Redirect to the dynamically generated chat room
    return redirect(chat_room, room_name = room_name)


def chat_room(request, room_name):
    return render(request, "chatbot/test.html", {"room_name": room_name})