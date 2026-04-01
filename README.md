# 🧾 AI-Powered FinTech Expense Auditor

An autonomous, full-stack enterprise application that utilizes Multimodal Vision LLMs and Retrieval-Augmented Generation (RAG) to process corporate expense receipts, extract structured data, and automatically audit claims against strict corporate policies. 

The system includes a stateful SQLite database and a Role-Based Access Control (RBAC) frontend, ensuring AI decisions are transparent and subject to a Human-in-the-Loop (HITL) review process by authorized Finance Auditors.



## 🚀 Key Features

* **Multimodal Data Extraction:** Upload raw receipt images. The AI automatically translates foreign languages, performs currency conversions, and extracts highly structured JSON data (Merchant, Date, Total, Taxes).
* **RAG-Powered Policy Auditing:** Queries a local ChromaDB vector database containing corporate policy documents to mathematically cross-reference extracted receipt data against specific company rules (e.g., Tier 1 City meal limits).
* **State Management:** Fully stateful application using a lightweight SQLite database to maintain an immutable audit trail of all processed claims.
* **Role-Based Access Control (RBAC):** UI segregation between the standard Employee Submission Portal and the secure Finance Auditor queue.
* **Human-in-the-Loop (HITL) Architecture:** An interactive dashboard that allows HR Admins to review AI-flagged claims, view the explicit AI reasoning and policy snippets, and issue final overrides with permanent database comments.

## 🛠️ Tech Stack

* **Frontend:** Streamlit, Pandas (Data processing)
* **Backend:** FastAPI, Python
* **AI & Machine Learning:** Google Gemini Flash (High-Speed Multimodal OCR & Logic), ChromaDB (Vector Search), SentenceTransformers (Embeddings)
* **Database:** SQLite (Relational State Management)

---

## 💻 Local Setup & Installation

To run this application locally, you will need two terminal windows running simultaneously (one for the backend API, one for the frontend UI).

### 1. Clone the Repository

git clone https://github.com/pranavpaul2006/FinTech-Expense-Auditor.git
cd POLICY-AUDITOR

### 2.Backend Setup
cd backend/app  
pip install -r requirements.txt  

Create a .env file inside the data folder and add your own Gemini API Key to run the OCR and Logic engine:  
GEMINI_API_KEY=your_api_key_here

python main.py  

### 2. Frontend setup

cd frontend  
pip install -r requirements.txt  
streamlit run app.py  

### Testing Guide for Evaluators
To fully evaluate the workflow and system architecture, please follow these steps:  

### Phase 1: The Employee Portal
1. Open the Streamlit frontend in your browser.

2. Ensure you are in the Employee Portal (default view).

3. Upload a sample receipt (e.g., a complex receipt with foreign currency or missing information).

4. Provide a business justification and click Run AI Audit.

5. Observe the AI extracting the data, applying corporate policy rules, and generating an initial status (APPROVED, REJECTED, or FLAGGED_FOR_REVIEW).

### Phase 2: The Human-in-the-Loop Override
1. In the left sidebar, switch the view to the Finance Auditor Dashboard.

2. When prompted for the Admin PIN, enter the demo credentials:
AUDIT-2026

3. Review the color-coded queue of pending claims pulled directly from the SQLite database.

4. Select a specific Claim ID from the dropdown menu to trigger the Audit Detail View. This pop-up will reveal the AI's exact reasoning and the corporate policy snippet used to make the decision.

5. Use the control panel to override the AI's decision (e.g., change from PENDING to APPROVED), leave a justification comment, and click Submit Final Verdict.

6. Observe the database table instantly update to reflect your immutable audit trail.