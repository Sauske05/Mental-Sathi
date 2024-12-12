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
            #email = form.cleaned_data['email']
            #password = form.cleaned_data['password']
            email = request.POST.get('email')
            password = request.POST.get('password')

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
    # else:
    #     form = LoginForm()

    #return render(request, 'users/Login_page.html', {'form': form})
    return render(request, 'users/Login_page.html')


def view_login(request):
    return render(request, 'users/Login_page.html', context= {'name' : 'Arun', 'age' : '21'})
# Create your views here.


def homepage(request):
    user_id = request.session.get('user_id')
    if user_id:
        return render(request, 'homepage.html', {'user_id': user_id, 'session' : request.session})
    return redirect('login')


# def signup(request):
#     return render(request, 'users/SignUp.html')


def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        retype_password = request.POST.get('re_password')
        agree_terms = request.POST.get('terms_checkbox')

        # Validation checks
        if not name or not email or not password or not retype_password:
            message = 'All fields are required'
            #messages.error(request, "All fields are required.")
            return render(request, 'users/SignUp.html', {'message': message})

        # if len(password) < 8:
        #     message = "Password must be at least 8 characters long."
        #     return render(request, 'users/SignUp.html',{'message': message})

        if password != retype_password:
            message = "Passwords do not match."
            return render(request, 'users/SignUp.html',{'message': message})

        if User.objects.filter(email=email).exists():
            message = "Email is already in use."
            return render(request, 'users/SignUp.html',{'message': message})

        # Terms and conditions checkbox validation
        if not agree_terms:
            message = "You must agree to the terms and conditions."
            return render(request, 'users/SignUp.html', {'message' : message})

        try:
            user = User(user_name=name, password=password, email=email)
            user.save()
            messages.success(request, "Account created successfully! Please log in.")
            return render(request, 'users/Login_page.html')
        except Exception as e:
            message = f"An error occurred: {str(e)}"
            return render(request, 'users/SignUp.html', {'message' : message})

    return render(request, 'users/SignUp.html', {'message' : ''})