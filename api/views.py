from django.shortcuts import render
from django.http import JsonResponse
import json
from users.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.serializers import UserSerializer
# Create your views here.

@api_view(['GET'])
def api_home(request):
    instance = User.objects.all()
    data = []
    # if model_data:
    #     for model in model_data:
    #         data= {
    #             'username' : model.user_name,
    #             'password' : model.password
    #         }
    #         list_val.append(data)
    if instance:
        for i in instance:
            data.append(UserSerializer(i).data)
    return Response(data)

