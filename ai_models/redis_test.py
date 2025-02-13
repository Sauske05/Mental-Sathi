# import redis
# host = '127.0.0.1'
# port = 6379
# try:
#     r = redis.Redis(host=host, port=6379, decode_responses=True)
#     print("Redis Connection Test:", r.ping())  # Should print True
# except redis.ConnectionError as e:
#     print("Redis connection failed:", e)

import requests

url = "http://127.0.0.1:8080/chatbot"
data = {"prompt": "Hello"}
headers = {"Content-Type": "application/json"}
try:
    response = requests.post(url, json=data, headers=headers)
    print(response.status_code, response.text)
except Exception as e:
    print("Error:", e)
