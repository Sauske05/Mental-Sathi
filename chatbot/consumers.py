import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
import httpx
from django.contrib.sessions.models import Session
from django.http import StreamingHttpResponse
import os
from dotenv import load_dotenv
load_dotenv()
from .models import Chat
from ai_models.inference_chat import prompt
import asyncio
import redis
import requests

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()
        #self.url = "http://localhost:8080/chatbot"

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
        message_type = data.get('type')

        if message_type == 'user_message':
            user_input = data.get('message')
            action = data.get('action')

            if action == 'stream_response':
                # This is the key part - calling your function
                await self.stream_chatbot_response(user_input)


    @sync_to_async
    def save_chat_message(self, user_query, bot_response):
        """Save chat messages in the database"""
        user_email = self.scope['session']['user_id']
        session = Session.objects.get(session_key=self.session_id)
        print(user_email)
        print(session)
        Chat.objects.create(
            user_id=user_email,
            session_id=session,
            context = f"User : {user_query} \n Assistant : {bot_response}"
        )

    async def chat_message(self, event):
        """Handle chat messages and send them to WebSocket"""
        await self.send(text_data=json.dumps({
            "message_type": event["message_type"],
            "content": event["content"],
            "is_complete": event.get("is_complete", False)
        }))

    # async def stream_chatbot_response(self, user_input):
    #         #prompt_ = prompt(user_input)
    #         user_email = self.scope['session']['user_id']
    #         data = {"prompt": user_input, "user_id" : user_email}
    #         headers = {"Content-Type": "application/json"}
    #         print(f'The user id while streaming chatbot response : {user_email}')
    #         async def stream_llm_response():
    #             url = 'http://127.0.0.1:2001/chatbot'
    #             #url = os.getenv("CHAT_URL")
    #             timeout = httpx.Timeout(1000.0)
    #
    #             async with httpx.AsyncClient(timeout=timeout) as client:
    #                 assistant_response = ''
    #                 async with client.stream("POST", url, json=data, headers = headers) as response:
    #                     #print(f'This is the response -> {response}')
    #                     print(f'This is the response status > {response.status_code}')
    #
    #                     async for chunk in response.aiter_text():
    #                         # Yield each chunk as it arrives
    #                         print(chunk)
    #                         assistant_response = assistant_response + chunk
    #
    #                         yield chunk
    #                 if response.status_code == 200:
    #                     await self.save_chat_message(user_input, assistant_response)
    #                     print('Content Saved in the Database')
    #
    #
    #         async for token in stream_llm_response():
    #             #await self.send(text_data=token)
    #             await self.channel_layer.group_send(
    #                 self.room_group_name,
    #                 {
    #                     "type": "chat_message",
    #                     "message_type": "bot",
    #                     "content": token
    #                 }
    #             )
    #             await asyncio.sleep(0.05)
    #
    #         # Return a streaming response to the frontend
    #         #return StreamingHttpResponse(stream_llm_response(), content_type='text/plain')

    async def stream_chatbot_response(self, user_input):
        user_email = self.scope['session']['user_id']
        data = {"prompt": user_input, "user_id": user_email}
        headers = {"Content-Type": "application/json"}
        print(f'The user id while streaming chatbot response: {user_email}')
        url = 'http://localhost:2001/chatbot'
        timeout = httpx.Timeout(1000.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            assistant_response = []
            async with client.stream("POST", url, json=data, headers=headers) as response:
                print(f'This is the response status > {response.status_code}')
                async for chunk in response.aiter_text():
                    print(chunk)
                    assistant_response.append(chunk)
                    # Send the chunk to the WebSocket group
                    # await self.channel_layer.group_send(
                    #     self.room_group_name,
                    #     {
                    #         "type": "chat_message",
                    #         "message_type": "bot",
                    #         "content": chunk
                    #     }
                    # )
                    # Small delay to control streaming rate (optional)
                    #await asyncio.sleep(0.05)
            if response.status_code == 200:
                full_response = ''.join(assistant_response)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message_type": "bot",
                        "content": full_response
                    }
                )
                await self.save_chat_message(user_input, full_response)
                print('Content Saved in the Database')