import json

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Avg, Max
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from functools import wraps
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.contrib.sessions.models import Session
from .forms import LoginForm
from .models import CustomUser, UserProfile
from .models import DashboardRecords
from datetime import timedelta, datetime
from django.utils.timezone import now
from django.contrib.auth import get_user_model
import pytz
from django.db import transaction
from users.serializers import CustomUserSerializer
from sentiment_analysis.models import SentimentModel

NEPAL_TZ = pytz.timezone('Asia/Kathmandu')

def dashboard_update(user:CustomUser):
    dashboard_detail = DashboardRecords.objects.get(user_name=user)
    current_time = datetime.now(NEPAL_TZ)

    current_date = current_time.date()
    last_login_date = dashboard_detail.last_login_date
    # print(f'Current Date: {current_date}')
    # print(f'Last Login Date: {last_login_date}')
    if not last_login_date:
        dashboard_detail.login_streak = 1
        dashboard_detail.number_of_login_days = 1
    if last_login_date:
        last_login_date = last_login_date.date()
        if last_login_date == current_date:
            pass
        elif last_login_date == current_date - timedelta(days=1):
            dashboard_detail.login_streak += 1
            dashboard_detail.number_of_login_days += 1
        else:
            dashboard_detail.login_streak = 0
            dashboard_detail.number_of_login_days += 1
    dashboard_detail.last_login_date = current_date

    dashboard_detail.save()

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            # email = form.cleaned_data['email']
            # password = form.cleaned_data['password']
            email = request.POST.get('email')
            password = request.POST.get('password')

            try:
                # Check if user exists
                user = CustomUser.objects.get(email=email)
                #dashboard_detail = DashboardRecords.objects.get(user_name=user)
                print(f'The email test: {user.email}')
                # Check password
                if check_password(password, user.password):
                    # Start session
                    request.session['user_id'] = user.email
                    # Updating the dashboard
                    # current_time = datetime.now(NEPAL_TZ)
                    #
                    # current_date = current_time.date()
                    # last_login_date = dashboard_detail.last_login_date
                    # # print(f'Current Date: {current_date}')
                    # # print(f'Last Login Date: {last_login_date}')
                    # if not last_login_date:
                    #     dashboard_detail.login_streak = 1
                    #     dashboard_detail.number_of_login_days = 1
                    # if last_login_date:
                    #     last_login_date = last_login_date.date()
                    #     if last_login_date == current_date:
                    #         pass
                    #     elif last_login_date == current_date - timedelta(days=1):
                    #         dashboard_detail.login_streak += 1
                    #         dashboard_detail.number_of_login_days += 1
                    #     else:
                    #         dashboard_detail.login_streak = 0
                    #         dashboard_detail.number_of_login_days += 1
                    # dashboard_detail.last_login_date = current_date
                    #
                    # dashboard_detail.save()
                    # messages.success(request, "Login successful!")
                    dashboard_update(user)
                    return redirect(user_dashboard, )  # Redirect to your homepage URL name
                else:
                    messages.error(request, "Invalid password.")
            except CustomUser.DoesNotExist:
                messages.error(request, "User does not exist.")
        else:
            messages.error(request, "Form not valid!.")
    return render(request, 'user_template/Login_page.html')


def view_login(request):
    return render(request, 'user_template/Login_page.html', context={'name': 'Arun', 'age': '21'})


# Create your views here.

def get_user_data(request, user_name):
    try:
        # user_name = request.POST.get('user_name')
        user_obj = CustomUser.objects.get(first_name=user_name)
    except CustomUser.DoesNotExist:
        return HttpResponse(status=404)
    if request.method == "GET":
        serializer = CustomUserSerializer(user_obj)
        return JsonResponse(serializer.data, safe=False)


def homepage(request):
    user_id = request.session.get('user_id')
    if user_id:
        return render(request, 'homepage.html', {'user_id': user_id, 'session': request.session})
    return redirect('login')


def admin_dashboard(request):
    user_records = CustomUser.objects.annotate(avg_sentiment=Avg('sentimentmodel__sentiment_score')).annotate(
        last_logged_in=Max('dashboardrecords__last_login_date'))
    return render(request, 'admin/index_.html', {'all_user_info_table': user_records})


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
            phone_number = request.POST.get('phone_number')
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
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': password,
                'phone_number': phone_number,
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
                user = CustomUser(first_name=user_data.get("first_name"), last_name=user_data.get("last_name"),
                                  password=user_data.get("password"), email=user_data.get("email"), phone_number=user_data.get("phone_number"))
                user.save()
                # User = get_user_model()
                user_filter = CustomUser.objects.get(email=user_data.get("email"))
                print(user_filter)
                dashboard_init = DashboardRecords(user_name=user_filter, login_streak=0, number_of_login_days=0,
                                                  positive_streak=0)
                dashboard_init.save()

                user_profile_init = UserProfile(user_email=user_filter, first_name=user_filter.first_name, last_name = user_filter.last_name)
                user_profile_init.save()
            messages.success(request, "Account created successfully! Please log in.")
            return render(request, 'user_template/Login_page.html')
        except Exception as e:
            message = f"An error occurred: {str(e)}"
            return render(request, 'user_template/SignUp.html', {'message': message})

    return render(request, 'user_template/SignUp.html', {'message': ''})


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
    # user_records = CustomUser.objects.all()
    user_records = CustomUser.objects.annotate(avg_sentiment=Avg('sentimentmodel__sentiment_score')).annotate(
        last_logged_in=Max('dashboardrecords__last_login_date'))
    return render(request, 'admin/tables.html', {'all_user_info_table': user_records})


def user_dashboard(request):
    user_email = request.session.get('user_id')
    if user_email is None:
        messages.error(request, 'You are not logged in.')
        return redirect(login_view, )
    user = CustomUser.objects.get(email=user_email)
    #print(user)
    #print('Here')
    dashboard_update(user)
    user_details = DashboardRecords.objects.get(user_name=user)
    return render(request, 'user_template/index.html', {'user_details': user_details})


def user_profile(request):
    user_email = request.session.get('user_id')
    user = CustomUser.objects.get(email=user_email)
    profile_data = UserProfile.objects.get(user_email=user)
    return render(request, 'user_template/profile_test.html', {'profile_data': profile_data})


def user_charts(request):
    return render(request, 'user_template/charts.html')


def user_error(request):
    return render(request, 'user_template/404.html')


from django.contrib.auth import logout


def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')


def authenticate_user_profile_update(func):
    @wraps(func)
    def wrapper(request, **kwargs):
        try:
            if request.method == 'POST':
                user_data = {
                    'first_name': request.POST.get('first_name'),
                    'last_name': request.POST.get('last_name'),
                    'email': request.session.get('user_id'),
                    'phone': request.POST.get('phone_number'),
                    'bio': request.POST.get('bio'),
                    'twitter_url': request.POST.get('twitter_url'),
                    'linkedin_url': request.POST.get('linkedin_url'),
                    'github_url': request.POST.get('github_url'),
                }

                # Validate phone number (assuming numeric with optional country code)
                # if user_data['phone'] and not re.match(r'^\+?[\d\s-]+$', user_data['phone']):
                #     return JsonResponse({'error': 'Invalid phone number'}, status=400)
                #
                # # Validate URLs (if provided)
                # url_pattern = re.compile(
                #     r'^(https?://)?(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(/[\w-]*)*$'
                # )
                # for field, value in [('Twitter URL', user_data['twitter_url']), ('LinkedIn URL', user_data['linkedin_url']),
                #                      ('GitHub URL', user_data['github_url'])]:
                #     if value and not url_pattern.match(value):
                #         return JsonResponse({'error': f'Invalid {field}'}, status=400)

                kwargs.update(user_data)
        except Exception as e:
            return e
        return func(request, **kwargs)
    return wrapper

@csrf_exempt
@authenticate_user_profile_update
def user_profile_update(request, **kwargs):
    print('CHECK')
    if request.method == 'POST':
        try:
            first_name = kwargs.get('first_name')
            last_name = kwargs.get('last_name')
            email = kwargs.get('email')
            phone = kwargs.get('phone')
            bio = kwargs.get('bio')
            twitter_url = kwargs.get('twitter_url')
            linkedin_url = kwargs.get('linkedin_url')
            github_url = kwargs.get('github_url')

            print('Github URL:', github_url)
            with transaction.atomic():
                user = CustomUser.objects.get(email=email)
                user.first_name = first_name
                user.last_name = last_name
                user.save()

                profile = UserProfile.objects.get(user_email=user)
                profile.phone = phone
                profile.bio = bio
                profile.twitter = twitter_url
                profile.linkedin = linkedin_url
                profile.github = github_url
                profile.first_name = first_name
                profile.last_name = last_name
                profile.save()

            return JsonResponse({'message': 'Profile updated successfully'}, status=200)
        except CustomUser.DoesNotExist:
            print('Check')
            return JsonResponse({'error': 'User not found'}, status=404)

        except UserProfile.DoesNotExist:
            print('Check Again')
            return JsonResponse({'error': 'Profile of the user not created!'}, status=404)
        except Exception as e:
            print('Check Again Re')
            return JsonResponse({'error': str(e)}, status=500)
    print('CHECK LAST')
@csrf_exempt
def upload_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('image'):
        user_email = request.session.get('user_id')
        user = CustomUser.objects.get(email=user_email)
        user_profile_ = UserProfile.objects.get(user_email=user)

        # Delete old profile picture if not default
        if user_profile_.profile_picture and user_profile_.profile_picture.name != "profile_pictures/default.png":
            if default_storage.exists(user_profile_.profile_picture.name):
                default_storage.delete(user_profile_.profile_picture.name)

        # Save new file
        image_file = request.FILES['image']
        file_path = f'profile_pictures/user_{user_email}/{image_file.name}'

        default_storage.save(file_path, ContentFile(image_file.read()))

        # Update user profile
        user_profile_.profile_picture = file_path
        user_profile_.save()

        return JsonResponse({"success": True, "path": file_path})

    return JsonResponse({"success": False, "error": "Invalid request"})

@csrf_exempt
def user_password_update(request):
    print('Enters')
    if request.method == 'POST':
        print('POST')
        try:

            user_email = request.session.get('user_id')
            user = CustomUser.objects.get(email=user_email)
            current_password = request.POST.get('currentPassword')
            new_password = request.POST.get('newPassword')
            re_password = request.POST.get('confirmPassword')
            print(user)
            print(current_password)
            print(new_password)
            print(re_password)
            if check_password(current_password, user.password):
                print('Passwords match')
            else:
                print('Test here wtf??')
                message = 'The password you entered is incorrect.'
                return JsonResponse({'message': message})

            if new_password != re_password:
                message_2 = "The new password doesn't match."
                return JsonResponse({'message' : message_2})

            user.password = new_password
            user.save()
            print('Final')
            return JsonResponse({'success': True, 'message': 'Password updated successfully'})
        except CustomUser.DoesNotExist as e:
            return JsonResponse({'message': str(e)})


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import OTPRequest
from .forms import PhoneNumberForm, OTPVerificationForm, PasswordResetForm
from .utils import send_otp_sms
from django.contrib import messages


def request_otp(request):
    if request.method == 'POST':

        form = PhoneNumberForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            try:
                #user = CustomUser.objects.get(profile__phone_number=phone_number)  # Assuming phone number is in profile
                user_email = request.session.get('user_id')
                user = CustomUser.objects.get(email=user_email)
                otp_request = OTPRequest.objects.create(user=user, phone_number=phone_number)
                otp = otp_request.generate_otp()
                send_otp_sms(phone_number, otp)
                request.session['otp_request_id'] = otp_request.id
                return redirect('verify_otp')
            except CustomUser.DoesNotExist:
                messages.error(request, 'No user found with this phone number')
    else:
        form = PhoneNumberForm()
        user_phone = CustomUser.objects.filter(email=request.session.get('user_id')).values('phone_number')[0]
        print(f'Users phone numbere: {user_phone}')
    return render(request, 'user_template/request_otp.html', {'form': form})


def verify_otp(request):
    if 'otp_request_id' not in request.session:
        return redirect('user_template/request_otp.html')

    otp_request = OTPRequest.objects.get(id=request.session['otp_request_id'])

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['otp'] == otp_request.otp:
                otp_request.is_verified = True
                otp_request.save()
                return redirect('reset_password')
            else:
                messages.error(request, 'Invalid OTP')
    else:
        form = OTPVerificationForm()
    return render(request, 'user_template/verify_otp.html', {'form': form})


def reset_password(request):
    if 'otp_request_id' not in request.session:
        return redirect('request_otp')

    otp_request = OTPRequest.objects.get(id=request.session['otp_request_id'])
    if not otp_request.is_verified:
        return redirect('verify_otp')

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['new_password'] == form.cleaned_data['confirm_password']:
                user = otp_request.user
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                del request.session['otp_request_id']
                messages.success(request, 'Password reset successfully')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match')
    else:
        form = PasswordResetForm()
    return render(request, 'user_template/reset_password.html', {'form': form})
