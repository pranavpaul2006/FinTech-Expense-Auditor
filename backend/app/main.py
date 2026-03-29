from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our services
from services.ocr_service import extract_receipt_data
from services.audit_service import audit_expense

app = FastAPI(title="Policy Auditor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/upload-receipt")
async def upload_receipt(
    file: UploadFile = File(...), 
    justification: str = Form(...)
):
    try:
        # Step 1: AI reads the receipt (The Eyes)
        extracted_data = await extract_receipt_data(file)
        
        # Step 2: AI audits the data against the database (The Brain)
        audit_result = audit_expense(extracted_data, justification)
        
        # Step 3: Return the complete package to the frontend
        return {
            "status": "success",
            "justification": justification,
            "receipt_details": extracted_data,
            "audit_verdict": audit_result
        }
        
    except Exception as e:
        print(f"🔥 THE REAL ERROR IS: {repr(e)}") 
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)