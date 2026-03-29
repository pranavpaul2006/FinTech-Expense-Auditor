from db.database import init_db, save_claim, get_all_claims, update_claim_status
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our services
from services.ocr_service import extract_receipt_data
from services.audit_service import audit_expense

# NEW: Import our database functions
from db.database import init_db, save_claim, get_all_claims
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

# NEW: Initialize the database the second the server boots up
init_db()

@app.post("/api/upload-receipt")
async def upload_receipt(
    file: UploadFile = File(...), 
    justification: str = Form(...),
    employee_name: str = Form("John Doe") # Default dummy employee
):
    try:
        # Step 1: AI reads the receipt
        extracted_data = await extract_receipt_data(file)
        
        # Step 2: AI audits the data
        audit_result = audit_expense(extracted_data, justification)
        
        # NEW: Step 3: Save the claim permanently to the SQLite database
        claim_id = save_claim(extracted_data, justification, audit_result, employee_name)
        
        # Step 4: Return the package to the frontend
        return {
            "status": "success",
            "claim_id": claim_id, # We now return the Database ID!
            "justification": justification,
            "receipt_details": extracted_data,
            "audit_verdict": audit_result
        }
        
    except Exception as e:
        print(f"🔥 THE REAL ERROR IS: {repr(e)}") 
        raise HTTPException(status_code=500, detail=str(e))

# NEW: Step 5: The endpoint for the Auditor Dashboard
@app.get("/api/claims")
async def fetch_claims():
    try:
        claims = get_all_claims()
        return {"status": "success", "data": claims}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NEW: Step 6: The Human Override Endpoint
@app.post("/api/update-claim")
async def update_claim(payload: ClaimUpdate):
    try:
        update_claim_status(payload.claim_id, payload.new_status, payload.comment)
        return {"status": "success", "message": f"Claim {payload.claim_id} updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)