from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DO_API_KEY"),
    base_url="https://inference.do-ai.run/v1"
)
