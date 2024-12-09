from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.contrib.sessions.models import Session
from .forms import LoginForm
from .models import User


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                # Check if user exists
                user = User.objects.get(email=email)

                # Check password
                if check_password(password, user.password):
                    # Start session
                    request.session['user_id'] = user.user_name
                    messages.success(request, "Login successful!")
                    return redirect('homepage', )  # Redirect to your homepage URL name
                else:
                    messages.error(request, "Invalid password.")
            except User.DoesNotExist:
                messages.error(request, "User does not exist.")
    else:
        form = LoginForm()

    return render(request, 'users/Login_page.html', {'form': form})


def view_login(request):
    return render(request, 'users/Login_page.html', context= {'name' : 'Arun', 'age' : '21'})
# Create your views here.


def homepage(request):
    user_id = request.session.get('user_id')
    if user_id:
        return render(request, 'homepage.html', {'user_id': user_id, 'session' : request.session})
    return redirect('login')