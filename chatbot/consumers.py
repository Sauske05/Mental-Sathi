import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
import httpx
from django.contrib.sessions.models import Session
from .models import Chat
from ai_models.inference_chat import prompt
import requests
import websockets
import asyncio
import torch


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()
        # self.model_path = '../ai_models/llama_3.2_3B_model'
        # self.model, self.tokenizer = load_model(self.model_path)
        # self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # self.streamer = TextStreamer(self.tokenizer, skip_prompt=True,skip_special_tokens=True )
        self.url = "ws://localhost:8080/chatbot"

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

        # Send user message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message_type": "user",
                "content": user_message
            }
        )

        # Stream bot response
        bot_response = ""
        async for chunk in self.stream_chatbot_response(user_message):
            #print(chunk)
            bot_response += chunk
            # Send each chunk to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message_type": "bot",
                    "content": chunk,
                    "is_complete": False
                }
            )
            await asyncio.sleep(0)

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

    # async def chat_message(self, event):
    #     user_message = event["user_message"]
    #     bot_message = event["bot_message"]
    #     await self.send(text_data=json.dumps({
    #         "user_message": user_message,
    #         "bot_message": bot_message,
    #     }))
    async def chat_message(self, event):
        """Handle chat messages and send them to WebSocket"""
        await self.send(text_data=json.dumps({
            "message_type": event["message_type"],
            "content": event["content"],
            "is_complete": event.get("is_complete", False)
        }))

    # async def stream_chatbot_response(self, user_input):
    #     # try:
    #     #     #response = inference(self.model, self.tokenizer, user_input, self.streamer, self.device)
    #     #     prompt_ = prompt(user_input)
    #     #     data = {"prompt" : prompt_}
    #     #     headers = {"Content-Type": "application/json"}
    #     #     response = requests.post(self.url, json = data,headers=headers)
    #     #     print(f"Response: {response.status_code}, {response.text}")
    #     #     return response.text
    #     # except Exception as e:
    #     #     return "Error getting response from chatbot."
    #     async with httpx.AsyncClient() as client:
    #         prompt_ = prompt(user_input)
    #         data = {"prompt": prompt_}
    #         headers = {"Content-Type": "application/json"}
    #         response = await client.post(self.url, json=data, headers = headers) as response:
    #         if response.status_code == 200:
    #             # Assuming the API supports chunked responses (streaming)
    #             async for chunk in response.aiter_text():
    #                 # Yield each chunk as it arrives
    #                 await asyncio.sleep(0.1)  # Optional delay for smoother streaming
    #                 yield chunk  # Send this chunk to the frontend
    #         else:
    #             # Handle errors or failure to fetch the response
    #             yield "Error: Failed to get response from LLM"

    async def stream_chatbot_response(self, user_input):
        async with httpx.AsyncClient() as client:
            prompt_ = prompt(user_input)
            data = {"prompt": prompt_}
            headers = {"Content-Type": "application/json"}

            # Set a custom timeout
            timeout = httpx.Timeout(200)  # 10 seconds, adjust as needed

            try:
                response = await client.post(self.url, json=data, headers=headers, timeout=timeout)
                print('This is the response')
                print(response.text)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Ensure the response is streamed
                for chunk in response.text:
                    #asyncio.sleep(0.1)
                   #asyncio.sleep(0.1)  # Optional delay for smoother streaming
                    yield chunk
            except httpx.ReadTimeout:
                yield "Error: The request timed out while waiting for the LLM's response."
            except httpx.HTTPStatusError as exc:
                yield f"Error: HTTP {exc.response.status_code} - {exc.response.text}"
            except Exception as exc:
                yield f"An unexpected error occurred: {str(exc)}"
