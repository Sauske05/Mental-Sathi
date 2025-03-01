from django.shortcuts import render
import json
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import httpx
import asyncio


# Create your views here.
def sentiment_page(request):
    return render(request, 'sentiment_tracker.html')


@csrf_exempt
async def sentiment_process(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            feelings_text = data.get("feelingsText")
            emotion = data.get("selectedEmotion")

            # Prepare the prompt for the LLM
            prompt_data = {
                "prompt": f"###System: You are an intelligent and empathetic chatbot capable of providing personalized suggestions to improve the well-being of the user. Your goal is to offer three practical and mood-boosting activities based on the user's current emotional state. Respond with three activities that can help improve someone's mood today. ###User: I'm feeling {emotion} today. {feelings_text} ###Response: ",
                "max_tokens": 512,
                "temperature": 0.7
            }

            print(f'Sending data: {json.dumps(prompt_data)}')

            # Create streaming response
            async def stream_llm_response():
                url = 'http://localhost:8080/recommendation_analysis'
                timeout = httpx.Timeout(120.0)

                async with httpx.AsyncClient(timeout=timeout) as client:
                    async with client.stream("POST", url, json=prompt_data) as response:
                        async for chunk in response.aiter_text():
                            # Yield each chunk as it arrives
                            yield chunk

            # Return a streaming response to the frontend
            return StreamingHttpResponse(stream_llm_response(), content_type='text/plain')

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)