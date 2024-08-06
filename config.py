from os import environ as env
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    def __init__(self):
        self.hugging_face_api_key = env.get("hugging_face_api_key")
        self.hugging_face_model_api_endpoint = env.get("hugging_face_model_api_endpoint")
        self.openai_api_key = env.get("OPENAI_API_KEY")
config = Config()
