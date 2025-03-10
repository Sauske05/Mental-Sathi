from django.http import JsonResponse
from django.shortcuts import render

def index(request):
    return render(request, './index.html')


def header(request):
    return render(request, './header.html')

def get_session(request):
    user_email = request.session.get('user_id', None)
    print(f'This is the user_email : {user_email}')
    return JsonResponse({'userEmail': user_email})