import requests
import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
headers = {
    "X-HuggingFace-Token": HF_TOKEN,
    "Content-Type": "application/json"
}

data = {
    "text": "Bloodshed Gangstar",
    "width": 512,
    "height": 512
}

response = requests.post(
    "http://localhost:8000/api/generate-image",
    headers=headers,
    json=data
)

if response.status_code == 200:
    with open("output.png", "wb") as f:
        f.write(response.content)
    print("Image saved!")
else:
    print(f"Error: {response.json()}")