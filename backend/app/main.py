from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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
    """
    Endpoint to receive the receipt image and the employee's justification.
    Later, we will route this to Gemini for OCR and ChromaDB for policy checking.
    """
    return {
        "filename": file.filename,
        "justification": justification,
        "status": "Received - Awaiting AI Processing"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)