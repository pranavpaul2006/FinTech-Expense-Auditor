import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import UploadFile
import json

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def extract_receipt_data(file: UploadFile) -> dict:
    image_bytes = await file.read()
    image_parts = [{"mime_type": file.content_type, "data": image_bytes}]
    
    prompt = """
    You are an expert financial auditor. Analyze the attached receipt document.
    Extract the merchant name, date, total amount, currency, and line items.
    
    CRITICAL RULES:
    1. If the receipt is not in English, translate the line item descriptions to English.
    2. Respond ONLY with a valid JSON object. No markdown, no conversational text.
    3. Ensure the JSON keys match: merchant_name, date, total_amount, currency, line_items (list of objects with description and amount), original_language, needs_translation, and is_readable.
    4. If the image is too blurry, dark, or cut off to confidently read the merchant or total, set "is_readable" to false. Otherwise, set it to true.
    5. ALL DATES MUST BE FORMATTED STRICTLY AS YYYY-MM-DD (e.g., 2026-04-02), regardless of how they appear.
    """
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content([prompt, image_parts[0]])
    
    # --- PDF BULLETPROOF EXTRACTION ---
    try:
        raw_text = response.text
    except ValueError:
        raw_text = "".join([part.text for part in response.candidates[0].content.parts])
        
    clean_json = raw_text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)