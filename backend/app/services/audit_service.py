import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

# Import the database search function you built earlier today
from services.policy_service import search_policy

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def audit_expense(receipt_data: dict, justification: str) -> dict:
    """
    Takes the extracted receipt data, searches the policy database, 
    and uses Gemini to determine if the expense is approved or rejected.
    """
    # 1. Figure out what rules to search for based on the items bought
    search_query = " ".join([item['description'] for item in receipt_data.get('line_items', [])])
    if not search_query:
        search_query = receipt_data.get('merchant_name', 'general expense')

    # 2. Fetch the relevant rules from your ChromaDB Vector Database
    relevant_policy_rules = search_policy(search_query)

    # 3. The Master Audit Prompt
    prompt = f"""
    You are an expert Corporate Financial Auditor.
    Review the following expense claim against the provided Corporate Policy rules.
    
    [EXTRACTED RECEIPT DATA]:
    {json.dumps(receipt_data, indent=2)}
    
    [EMPLOYEE JUSTIFICATION]:
    {justification}
    
    [RELEVANT CORPORATE POLICY RULES]:
    {relevant_policy_rules}
    
    Task:
    1. Determine if this expense strictly complies with the policy.
    2. Check for alcohol (strictly prohibited).
    3. Check limits based on the justification and items.
    
    Respond ONLY with a valid JSON object matching this exact structure:
    {{
        "status": "APPROVED" or "REJECTED" or "FLAGGED_FOR_REVIEW",
        "reasoning": "A 1-2 sentence explanation quoting the specific policy rule used.",
        "policy_referenced": "A short snippet of the rule you applied."
    }}
    """
    
    # We use the Pro model here because auditing requires deep logic
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)