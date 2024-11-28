from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

def view_login(request):
    return render(request, 'users/Login_page.html', context= {'name' : 'Arun', 'age' : '21'})
# Create your views here.
