from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import httpx
# Create your views here.
def sentiment_page(request):
    return render(request, 'sentiment_tracker.html')

@csrf_exempt
async def sentiment_process(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            #print(f'This is the data- >{data}')
            feelings_text = data.get("feelingsText")
            emotion = data.get("selectedEmotion")
            #print(feelings_text)
            data = {
                "sentiment_keyword": emotion,
                "user_text": feelings_text,
            }
            print(f'Data: {json.dumps(data)}')
            url = 'http://localhost:8080/recommendation_analysis'
            headers = {"Content-Type": "application/json"}
            timeout = httpx.Timeout(120.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=data, headers=headers)
            #sentiment_response =  JsonResponse(response.json())
            #print(sentiment_response['response'])
            print(response.json())
            return JsonResponse(response.json())
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)