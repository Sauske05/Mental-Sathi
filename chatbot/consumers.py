import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async

from django.contrib.sessions.models import Session
from .models import Chat
from ai_models.inference_chat import prompt
import requests

import torch
class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()
        # self.model_path = '../ai_models/llama_3.2_3B_model'
        # self.model, self.tokenizer = load_model(self.model_path)
        # self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # self.streamer = TextStreamer(self.tokenizer, skip_prompt=True,skip_special_tokens=True )
        self.url = "http://127.0.0.1:8080/chatbot"
    async def connect(self):
        self.user = self.scope['user']
        self.session_id = self.scope['session'].session_key

        if not self.session_id:
            await sync_to_async(self.scope['session'].create)()
            self.session_id = self.scope['session'].session_key

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data["message"]

        # Get response
        bot_response = await sync_to_async(self.get_chatbot_response)(user_message)

        # Save chat history to the database
        await self.save_chat_message(user_message, bot_response)

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "bot_message": bot_response,
             "user_message": user_message},
        )

    @sync_to_async
    def save_chat_message(self, user_query, bot_response):
        """Save chat messages in the database"""
        #user = self.user if self.user.is_authenticated else None
        user = self.scope["user"]
        if user.is_authenticated:
            user_id = user.id  # This will give you the user ID
        else:
            user_id = None  # If the user is not authenticated
        session = Session.objects.get(session_key=self.session_id)
        print(user)
        print(session)
        Chat.objects.create(
            user_id=user,
            session_id=session,
            user_query=user_query,
            assistant_text=bot_response,
        )

    async def chat_message(self, event):
        user_message = event["user_message"]
        bot_message = event["bot_message"]
        await self.send(text_data=json.dumps({
            "user_message": user_message,
            "bot_message": bot_message,
        }))

    def get_chatbot_response(self, user_input):
        try:
            #response = inference(self.model, self.tokenizer, user_input, self.streamer, self.device)
            prompt_ = prompt(user_input)
            data = {"prompt" : prompt_}
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.url, json = data,headers=headers)
            print(f"Response: {response.status_code}, {response.text}")
            return response.text
        except Exception as e:
            return "Error getting response from chatbot."