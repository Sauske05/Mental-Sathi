from django.shortcuts import render

# Create your views here.
def sentiment_page(request):
    return render(request, 'sentiment_tracker.html')