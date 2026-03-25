from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our new OCR service
from services.ocr_service import extract_receipt_data

app = FastAPI(title="Policy Auditor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Policy Auditor API is running."}

@app.post("/api/upload-receipt")
async def upload_receipt(
    file: UploadFile = File(...), 
    justification: str = Form(...)
):
    try:
        # 1. Pass the uploaded file to our AI engine
        extracted_data = await extract_receipt_data(file)
        
        # 2. Return the AI's findings directly to the frontend
        return {
            "status": "success",
            "justification": justification,
            "ai_extraction": extracted_data
        }
        
    except Exception as e:
        print(f"🔥 THE REAL ERROR IS: {repr(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)