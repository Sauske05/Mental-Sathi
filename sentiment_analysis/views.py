from asgiref.sync import sync_to_async
from django.shortcuts import render
import json
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import httpx
import asyncio

from users.models import User
from .bert_model.configure import *
from .bert_model.tokenizer import *
from .bert_model.model import *
from django.apps import apps
from .models import SentimentModel as SentimentDB
from sentiment_analysis.apps import SentimentAnalysisConfig
from django.db import transaction

from .serializers import SentimentSerializer
# Create your views here.
def get_user_sentiment_data(request, user_name):
    try:
        sentiment_obj = SentimentDB.objects.filter(user_name=user_name)
    except SentimentDB.DoesNotExist:
        return HttpResponse(status=404)
    if request.method == "GET":
        serializer = SentimentSerializer(sentiment_obj, many = True)
        print(f'This is the serialized data: {JsonResponse(serializer.data, safe=False)}')
        return JsonResponse(serializer.data, safe=False)


def sentiment_page(request):
    return render(request, 'sentiment_tracker.html')


async def bert_inference(input_text, bert_model):
    label_dict = {0 : 'Anxiety', 1 : 'Depression', 2 : 'Normal', 3 : 'Suicidal', 4 : 'Personality disorder'}
    tokenizer_obj = Tokenizer()
    tokenized_input = tokenizer_obj.tokenize([input_text], 100)
    input_ids = tokenized_input['input_ids'].unsqueeze(0)
    print(input_ids.size())
    input_mask_ids = tokenized_input['attention_mask'].unsqueeze(0)
    print(input_mask_ids.size())
    input_mask = input_mask_ids.transpose(-1,-2)
    input_attn_mask = ((input_mask @ input_mask.transpose(-1,-2)).unsqueeze(1))
    bert_model.eval()
    model_pred = bert_model(input_ids, input_attn_mask)
    model_idx = torch.argmax(model_pred[0]).item() #torch.argmax(model_pred.squeeze())
    if model_idx in label_dict.keys():
        return  label_dict[model_idx]
@sync_to_async
def process_initial_data(request, feelings_text, emotion, bert_analysis):
    try:
        with transaction.atomic():
            user_name_session = request.session['user_id']
            user_name = User.objects.get(user_name=user_name_session)
            sentiment_obj = SentimentDB(
                user_name=user_name,
                sentiment_data=emotion,
                recommendation_text='',  # Will update later
                user_query=feelings_text,
                query_sentiment=bert_analysis
            )
            sentiment_obj.save()
            return sentiment_obj.id  # Return ID to retrieve later
    except Exception as e:
        print(f"Error saving initial data: {e}")
        return None

@sync_to_async
def update_sentiment_record(sentiment_id, bot_response_):
    if sentiment_id:
        try:
            with transaction.atomic():
                sentiment_obj = SentimentDB.objects.get(id=sentiment_id)
                sentiment_obj.recommendation_text = bot_response_
                sentiment_obj.save()
        except Exception as e:
            print(f"Error updating sentiment record: {e}")
@csrf_exempt
async def sentiment_process(request):
    if request.method == "POST":
            try:
                data = json.loads(request.body)
                feelings_text = data.get("feelingsText")
                emotion = data.get("selectedEmotion")
                bert_model = SentimentAnalysisConfig.bert_model
                bert_analysis = await bert_inference(feelings_text, bert_model)

                sentiment_id = await process_initial_data(request, feelings_text, emotion, bert_analysis)

                prompt_data = {
                    "prompt": f"###System: You are an intelligent and empathetic chatbot capable of providing personalized suggestions to improve the well-being of the user. Your goal is to offer three practical and mood-boosting activities based on the user's current emotional state. Respond with three activities that can help improve someone's mood today. ###User: I'm feeling {emotion} today. {feelings_text} ###Response: ",
                    "max_tokens": 512,
                    "temperature": 0.7
                }

                print(f'Sending data: {json.dumps(prompt_data)}')

                # Create streaming response
                async def stream_llm_response():
                    url = 'http://localhost:2001/recommendation_analysis'
                    timeout = httpx.Timeout(120.0)
                    full_response = ''
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        async with client.stream("POST", url, json=prompt_data) as response:
                            async for chunk in response.aiter_text():
                                # Yield each chunk as it arrives
                                full_response += chunk
                                yield chunk
                    print()
                    await update_sentiment_record(sentiment_id, full_response)
                # Return a streaming response to the frontend
                return StreamingHttpResponse(stream_llm_response(), content_type='text/plain')

            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)