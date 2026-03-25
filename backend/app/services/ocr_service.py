import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import UploadFile
import json

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("CRITICAL: GEMINI_API_KEY is missing from .env file")

genai.configure(api_key=api_key)

async def extract_receipt_data(file: UploadFile) -> dict:
    
    image_bytes = await file.read()
    
    image_parts = [
        {
            "mime_type": file.content_type,
            "data": image_bytes
        }
    ]
    
    prompt = """
    You are an expert financial auditor. Analyze the attached receipt image.
    Extract the merchant name, date, total amount, currency, and line items.
    
    CRITICAL RULES:
    1. If the receipt is not in English, translate the line item descriptions to English.
    2. Respond ONLY with a valid JSON object. No markdown, no conversational text.
    3. Ensure the JSON keys match: merchant_name, date, total_amount, currency, line_items (list of objects with description and amount), original_language, needs_translation.
    """
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    response = model.generate_content([prompt, image_parts[0]])
    
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    
    return json.loads(clean_json)