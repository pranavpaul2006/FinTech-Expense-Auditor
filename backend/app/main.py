from db.database import init_db, save_claim, get_all_claims, update_claim_status
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import uvicorn

from services.ocr_service import extract_receipt_data
from services.audit_service import audit_expense

class ClaimUpdate(BaseModel):
    claim_id: int
    new_status: str
    comment: str

app = FastAPI(title="Policy Auditor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

@app.post("/api/upload-receipt")
async def upload_receipt(
    file: UploadFile = File(...), 
    justification: str = Form(...),
    claimed_date: str = Form(...),
    employee_name: str = Form(...),
    employee_id: str = Form(...)
):
    try:
        # Step 1: Read the image
        extracted_data = await extract_receipt_data(file)
        
        time.sleep(2)

        merchant = extracted_data.get("merchant_name", "Unknown Merchant")
        total = extracted_data.get("total_amount", 0.0)
        currency = extracted_data.get("currency", "USD")

        # --- NEW: FRAUD RING DETECTOR (Duplicate Check) ---
        
        is_duplicate = False
        original_submitter = ""
        
        all_claims = get_all_claims()
        for claim in all_claims:
            # If the exact same merchant and amount exist in the DB...
            if claim['merchant_name'] == merchant and str(claim['total_amount']) == str(total):
                is_duplicate = True
                original_submitter = claim['employee_name']
                break
        
        if is_duplicate:
            # Instantly reject it without even doing a full policy audit
            audit_result = {
                "status": "REJECTED",
                "reasoning": f"FRAUD ALERT: A receipt for {merchant} totaling {total} was already submitted by {original_submitter}.",
                "policy_referenced": "Zero Tolerance Policy: Duplicate submissions are strictly prohibited."
            }
        else:
            # Step 2: If it's not a duplicate, run the normal AI Policy Audit
            audit_result = audit_expense(extracted_data, justification, claimed_date)
        
        # Unpack the Audit data
        status = audit_result.get("status", "UNKNOWN")
        reasoning = audit_result.get("reasoning", "No reasoning provided.")
        policy = audit_result.get("policy_referenced", "None")
        
        # Save to database
        claim_id = save_claim(
            employee_id, 
            employee_name, 
            merchant, 
            total, 
            currency, 
            justification, 
            status, 
            reasoning, 
            policy
        )
        
        return {
            "status": "success",
            "claim_id": claim_id, 
            "justification": justification,
            "receipt_details": extracted_data,
            "audit_verdict": audit_result
        }
        
    except Exception as e:
        print(f"🔥 THE REAL ERROR IS: {repr(e)}") 
        raise HTTPException(status_code=500, detail=str(e))

# --- NEW: ENDPOINT FOR EMPLOYEE HISTORY ---
@app.get("/api/my-claims/{emp_id}")
async def fetch_my_claims(emp_id: str):
    try:
        all_claims = get_all_claims()
        # Filter the database to only show claims matching the employee's ID
        my_claims = [claim for claim in all_claims if claim['employee_id'] == emp_id]
        return {"status": "success", "claims": my_claims}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/claims")
async def fetch_claims():
    try:
        claims = get_all_claims()
        return {"status": "success", "data": claims}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update-claim")
async def update_claim(payload: ClaimUpdate):
    try:
        update_claim_status(payload.claim_id, payload.new_status, payload.comment)
        return {"status": "success", "message": f"Claim {payload.claim_id} updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)