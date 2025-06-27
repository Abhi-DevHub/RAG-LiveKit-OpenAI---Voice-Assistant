import os
from dotenv import load_dotenv
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    models = openai.models.list()
    print("✅ Connected to OpenAI! Found models:", [m.id for m in models.data[:5]])  # Display first 5 models
except Exception as e:
    print("❌ Failed to connect:", e)

    