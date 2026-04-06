import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from services.policy_service import search_policy

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# NEW: We added claimed_date to the required arguments
def audit_expense(receipt_data: dict, justification: str, claimed_date: str) -> dict:
    
    # --- 1. THE BLURRY CHECK ---
    if receipt_data.get("is_readable") is False or receipt_data.get("merchant_name", "Unknown") == "Unknown":
        return {
            "status": "REJECTED",
            "reasoning": "The uploaded document is blurry, cut off, or illegible. Please upload a clear copy.",
            "policy_referenced": "System Requirement: Legible Documentation"
        }

    # --- 2. THE DATE MISMATCH CHECK ---
    receipt_date = receipt_data.get("date", "")
    if receipt_date and claimed_date not in receipt_date: 
        return {
            "status": "FLAGGED_FOR_REVIEW",
            "reasoning": f"Date discrepancy detected. The employee claimed {claimed_date}, but the AI read {receipt_date}.",
            "policy_referenced": "Fraud Prevention: Expense dates must strictly match the receipt."
        }

    # 3. Standard Policy Audit
    search_query = " ".join([item['description'] for item in receipt_data.get('line_items', [])])
    if not search_query:
        search_query = receipt_data.get('merchant_name', 'general expense')

    relevant_policy_rules = search_policy(search_query)

    prompt = f"""
    You are an expert Corporate Financial Auditor. Review the claim against the policy rules.
    [EXTRACTED RECEIPT DATA]: {json.dumps(receipt_data, indent=2)}
    [EMPLOYEE JUSTIFICATION]: {justification}
    [RELEVANT CORPORATE POLICY RULES]: {relevant_policy_rules}
    
    Respond ONLY with a valid JSON object matching this exact structure:
    {{
        "status": "APPROVED" or "REJECTED" or "FLAGGED_FOR_REVIEW",
        "reasoning": "A 1-2 sentence explanation quoting the specific policy rule used.",
        "policy_referenced": "A short snippet of the rule you applied."
    }}
    """
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    
    # --- PDF BULLETPROOF EXTRACTION ---
    try:
        raw_text = response.text
    except ValueError:
        raw_text = "".join([part.text for part in response.candidates[0].content.parts])
        
    clean_json = raw_text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)