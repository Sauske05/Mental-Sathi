from django.shortcuts import render

def index(request):
    return render(request, './index.html')


def header(request):
    return render(request, './header.html')