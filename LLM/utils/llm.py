import os
from dotenv import load_dotenv
from utils.log import logger
from openai import OpenAI
import google.generativeai as genai

load_dotenv()


# OpenAI
try:

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in .env")

    openai_client = OpenAI(api_key=openai_api_key)
    logger.info(f"OpenAI  client initialized successfully.")

except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    openai_client = None

# Gemini
try:

    gemini_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set in .env")

    genai.configure(api_key=gemini_api_key)
    gemini_model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))
    logger.info("Gemini model initialized successfully.")

except Exception as e:
    logger.error(f"Failed to initialize Gemini model: {e}")
    gemini_model = None