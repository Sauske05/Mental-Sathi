from django.db.models import Avg, Max
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from functools import wraps
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.contrib.sessions.models import Session
from .forms import LoginForm
from .models import CustomUser
from .models import DashboardRecords
from datetime import timedelta, datetime
from django.utils.timezone import now
from django.contrib.auth import get_user_model
import pytz
from django.db import transaction
from users.serializers import CustomUserSerializer
from sentiment_analysis.models import SentimentModel
NEPAL_TZ = pytz.timezone('Asia/Kathmandu')
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
                user = CustomUser.objects.get(email=email)
                dashboard_detail = DashboardRecords.objects.get(user_name=user)
                print(f'The email test: {user.email}')
                # Check password
                if check_password(password, user.password):
                    # Start session
                    request.session['user_id'] = user.email
                    #Updating the dashboard
                    current_time = datetime.now(NEPAL_TZ)

                    current_date = current_time.date()
                    last_login_date = dashboard_detail.last_login_date
                    #print(f'Current Date: {current_date}')
                    #print(f'Last Login Date: {last_login_date}')
                    if not last_login_date:
                        dashboard_detail.login_streak = 1
                        dashboard_detail.number_of_login_days =1
                    if last_login_date:
                        last_login_date = last_login_date.date()
                        if last_login_date == current_date:
                            pass
                        elif last_login_date == current_date - timedelta(days=1):
                            dashboard_detail.login_streak +=1
                            dashboard_detail.number_of_login_days +=1
                        else:
                            dashboard_detail.login_streak = 0
                            dashboard_detail.number_of_login_days +=1
                    dashboard_detail.last_login_date = current_date


                    dashboard_detail.save()
                    #messages.success(request, "Login successful!")
                    return redirect(user_dashboard, )  # Redirect to your homepage URL name
                else:
                    messages.error(request, "Invalid password.")
            except CustomUser.DoesNotExist:
                messages.error(request, "User does not exist.")

    # if isinstance(request.user, CustomUser):
    #     print(request.user)
    #     user_obj = request.user
    #     try:
    #         # Check if user exists
    #         user = CustomUser.objects.get(email=user_obj.email)
    #         print(f'User Object Check: {user}')
    #         dashboard_detail = DashboardRecords.objects.get(user_name=user)
    #         print(f'The email test: {user.email}')
    #         request.session['user_id'] = user.email
    #         # Updating the dashboard
    #         current_time = datetime.now(NEPAL_TZ)
    #
    #         current_date = current_time.date()
    #         last_login_date = dashboard_detail.last_login_date
    #
    #         if not last_login_date:
    #             dashboard_detail.login_streak = 1
    #             dashboard_detail.number_of_login_days = 1
    #         if last_login_date:
    #             last_login_date = last_login_date.date()
    #             if last_login_date == current_date:
    #                 pass
    #             elif last_login_date == current_date - timedelta(days=1):
    #                 dashboard_detail.login_streak += 1
    #                 dashboard_detail.number_of_login_days += 1
    #             else:
    #                 dashboard_detail.login_streak = 0
    #                 dashboard_detail.number_of_login_days += 1
    #         dashboard_detail.last_login_date = current_date
    #
    #         dashboard_detail.save()
    #         # messages.success(request, "Login successful!")
    #     except CustomUser.DoesNotExist:
    #         messages.error(request, "User does not exist.")
    #     return redirect(user_dashboard, )


    #return render(request, 'users/Login_page.html', {'form': form})
    return render(request, 'user_template/Login_page.html')


def view_login(request):
    return render(request, 'user_template/Login_page.html', context= {'name' : 'Arun', 'age' : '21'})
# Create your views here.

def get_user_data(request, user_name):
        try:
            #user_name = request.POST.get('user_name')
            user_obj = CustomUser.objects.get(first_name=user_name)
        except CustomUser.DoesNotExist:
            return HttpResponse(status=404)
        if request.method == "GET":
            serializer = CustomUserSerializer(user_obj)
            return JsonResponse(serializer.data, safe=False)
def homepage(request):
    user_id = request.session.get('user_id')
    if user_id:
        return render(request, 'homepage.html', {'user_id': user_id, 'session' : request.session})
    return redirect('login')


def admin_dashboard(request):
    return render(request, 'admin/index_.html')


def signup_authentication(func):
    @wraps(func)
    def wrapper(request, **kwargs):
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            retype_password = request.POST.get('re_password')
            agree_terms = request.POST.get('terms_checkbox')

            # Validation checks
            if not first_name or not last_name or not email or not password or not retype_password:
                message = 'All fields are required'
                # messages.error(request, "All fields are required.")
                return render(request, 'user_template/SignUp.html', {'message': message})

            # if len(password) < 8:
            #     message = "Password must be at least 8 characters long."
            #     return render(request, 'users/SignUp.html',{'message': message})

            if password != retype_password:
                message = "Passwords do not match."
                return render(request, 'user_template/SignUp.html', {'message': message})

            # if CustomUser.objects.filter(user_name=name).exists():
            #     message = "User already exists."
            #     return render(request, 'user_template/SignUp.html', {'message': message})

            if CustomUser.objects.filter(email=email).exists():
                message = "Email is already in use."
                return render(request, 'user_template/SignUp.html', {'message': message})

            # Terms and conditions checkbox validation
            if not agree_terms:
                message = "You must agree to the terms and conditions."
                return render(request, 'user_template/SignUp.html', {'message': message})

            request.clean_data = {
                'first_name' : first_name,
                'last_name' : last_name,
                'email' : email,
                'password' : password
            }
        return func(request, **kwargs)
    return wrapper
@signup_authentication
def signup(request):
    if request.method == 'POST':
        try:
            user_data = request.clean_data
            # print(f'This is the user_data {user_data.get("name")}')
            # #print(f'user_data {user_data.keys()}')
            with transaction.atomic():
                user = CustomUser(first_name=user_data.get("first_name"), last_name=user_data.get("last_name"), password=user_data.get("password"), email=user_data.get("email"))
                user.save()
                #User = get_user_model()
                user_filter = CustomUser.objects.get(email=user_data.get("email"))
                print(user_filter)
                dashboard_init = DashboardRecords(user_name=user_filter, login_streak=0, number_of_login_days=0, positive_streak=0)
                dashboard_init.save()
            messages.success(request, "Account created successfully! Please log in.")
            return render(request, 'user_template/Login_page.html')
        except Exception as e:
            message = f"An error occurred: {str(e)}"
            return render(request, 'user_template/SignUp.html', {'message' : message})

    return render(request, 'user_template/SignUp.html', {'message' : ''})



def buttons(request):
    return render(request, 'admin/buttons.html')

def card(request):
    return render(request, 'admin/cards.html')


def utilities_border(request):
    return render(request, 'admin/utilities-border.html')

def utilities_animation(request):
    return render(request, 'admin/utilities-animation.html')

def utilities_color(request):
    return render(request, 'admin/utilities-color.html')

def utilities_other(request):
    return render(request, 'admin/utilities-other.html')


def error_page(request):
    return render(request, 'admin/404.html')

def blank_page(request):
    return render(request, 'admin/blank.html')

def admin_charts(request):
    return render(request, 'admin/charts.html')

def admin_tables(request):
    #user_records = CustomUser.objects.all()
    user_records = CustomUser.objects.annotate(avg_sentiment=Avg('sentimentmodel__sentiment_score')).annotate(last_logged_in=Max('dashboardrecords__last_login_date'))
    return render(request, 'admin/tables.html', {'all_user_info_table' : user_records})

def user_dashboard(request):
    user_email = request.session.get('user_id')
    user = CustomUser.objects.get(email=user_email)
    print(user)
    print('Here')
    user_details = DashboardRecords.objects.get(user_name=user)
    return render(request, 'user_template/index.html', {'user_details' : user_details})

def user_profile(request):
    return render(request, 'user_template/profile.html')

def user_charts(request):
    return render(request, 'user_template/charts.html')

def user_error(request):
    return render(request, 'user_template/404.html')


from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')