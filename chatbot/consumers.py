import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
import httpx
from django.contrib.sessions.models import Session
from .models import Chat
from ai_models.inference_chat import prompt
import asyncio
import redis
import requests

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()
        self.url = "http://localhost:8080/chatbot"

    async def connect(self):
        print(self.scope)
        #self.user = self.scope['user']
        self.user_name = self.scope['session']['user_id']
        self.session_id = self.scope['session'].session_key
        print('This is the username--> ',self.user_name)
        if not self.session_id:
            await sync_to_async(self.scope['session'].create)()
            self.session_id = self.scope['session'].session_key

        #self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_name = f'{self.session_id}'
        #self.room_name =
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f'Channel Name : {self.channel_name}')
        print(f'Room Name : {self.room_name}')
        #asyncio.create_task(self.read_stream())

    #async def read_stream(self):

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data["message"]

        # Send user message to the group
        #print('Sending Message to Websocket')
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message_type": "user",
                "content": user_message
            }
        )
        await asyncio.sleep(0)
        #print('Message sent to websocket')
        #print('Reach check')
        #bot_response = ""
        # async for chunk in self.stream_chatbot_response(user_message):
        #     bot_response += chunk
        bot_response = await self.stream_chatbot_response(user_message)
        #print('This is the bot message \n')
        #print(bot_response)
        # Send final message indicating stream is complete

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message_type": "bot",
                "content": bot_response,
                "is_complete": True
            }
        )


    @sync_to_async
    def save_chat_message(self, user_query, bot_response):
        """Save chat messages in the database"""
        # user = self.user if self.user.is_authenticated else None
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
        """Handle chat messages and send them to WebSocket"""
        await self.send(text_data=json.dumps({
            "message_type": event["message_type"],
            "content": event["content"],
            "is_complete": event.get("is_complete", False)
        }))

    async def stream_chatbot_response(self, user_input):
            prompt_ = prompt(user_input)
            data = {"prompt": prompt_}
            headers = {"Content-Type": "application/json"}
            print('invoked stream chatbot')
            # Set a custom timeout
            timeout = httpx.Timeout(200)  # 10 seconds, adjust as needed
            try:
                response = requests.post(self.url, json=data, headers=headers)
                #print('This is the response')
                #print(response.text)

                # Ensure the response is streamed
                # for chunk in response.text:
                #     await asyncio.sleep(0.1)
                #     yield chunk
                return response.json()
            except httpx.ReadTimeout:
                return "Error: The request timed out while waiting for the LLM's response."
            except httpx.HTTPStatusError as exc:
                return f"Error: HTTP {exc.response.status_code} - {exc.response.text}"
            except Exception as exc:
                return f"An unexpected error occurred: {str(exc)}"
