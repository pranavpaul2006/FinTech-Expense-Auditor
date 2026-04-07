# FinTech Ai Expense Auditor

## 🚩 The Problem
Corporate expense policies are often dense, multi-page documents that are difficult for employees to navigate, leading to frequent non-compliance and rejected claims. Manual auditing of these receipts against complex rules is a high-latency process for finance departments, often resulting in human error and reimbursement delays.

## 💡 The Solution
This project is an **AI-powered Expense Auditing System** that automates the verification of financial claims using **Retrieval-Augmented Generation (RAG)**. 

## ✨ Core Features
* **Intelligent OCR:** High-accuracy extraction of Date, Amount, Category, and Merchant from blurry or complex receipts.
* **RAG-Powered Policy Engine:** Uses **ChromaDB** to index 40+ pages of policy and retrieve only relevant rules for each claim.
* **Multi-Currency Support:** AI automatically detects and converts foreign currency based on policy guidelines.
* **Immutable Audit Trail:** Every decision (AI or Human) is logged in a persistent SQLite database for tax and compliance filing.
* **Real-time Logic:** Fast asynchronous communication between Streamlit and FastAPI using Docker networking.
* **Automated Budget Forecasting:** 30-day spending projections based on historical claim data.

## 🛠️ Tech Stack
* **Programming Language:** Python 3.10
* **Backend Framework:** FastAPI (Asynchronous ASGI)
* **Frontend Interface:** Streamlit
* **AI/LLM:** Google Gemini API (Generative AI)
* **Orchestration:** LangChain (RAG Framework)
* **Vector Database:** ChromaDB
* **DevOps:** Docker & Docker Compose (Containerization), Render (Cloud Hosting)

## 🚀 Setup Instructions

### 1. Prerequisites
* Ensure **Docker** and **Docker Compose** are installed on your machine.
* Obtain a **Google Gemini API Key** from the Google AI Studio.

### 2. Local Development (Docker)
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/pranavpaul2006/FinTech-Expense-Auditor.git  
    cd POLICY-AUDITOR  
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and add your API key:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key_here
    ```

3.  **Launch the Application:**
    ```bash
    docker-compose up --build
    ```
    * **Frontend UI:** `http://localhost:8501`
    * **Backend API:** `http://localhost:8000`

4. **Testing Guide for Evaluators:**

    ### 🏢 Phase 1: The Employee Portal (Submission)
    1. **Upload:** Employees upload a sample receipt (Image or PDF) via the Streamlit interface.
    2. **Justification:** Users provide a business reason for the expense.
    3. **AI Audit:** The system triggers Gemini 2.5 Flash to extract data and apply corporate policy rules.
    4. **Instant Status:** The claim is instantly categorized as **APPROVED**, **REJECTED**, or **FLAGGED_FOR_REVIEW**.

    ### 🛡️ Phase 2: Human-in-the-Loop Override (Audit)
    1. **Secure Access:** Auditors switch to the Dashboard using the Admin PIN: `AUDIT-2026`.
    2. **Detail View:** Auditors can see the AI's exact reasoning and the specific policy snippet used for the decision.
    3. **Manual Override:** Change statuses (e.g., PENDING to APPROVED) with a justification comment to maintain an immutable audit trail in the SQLite database.

    ### 📈 Phase 3: Executive Analytics (C-Suite)
    1. **Compliance Heatmap:** Aggregated data showing spending trends across departments.
    2. **Budget Leakage:** Real-time tracking of the total value of policy violations prevented.
    3. **AI Efficiency:** KPI dashboard showing the ratio of AI-processed vs. human-processed claims.

### 3. Cloud Deployment (Render)
To deploy this monorepo on Render, use the following configurations:

**Backend Service:**
* **Root Directory:** `backend`
* **Runtime:** `Docker`
* **Dockerfile Path:** `Dockerfile`
* **Environment Variables:** * `GOOGLE_API_KEY`: [Your Key]
    * `PYTHONPATH`: `/app/app` (Required for internal module resolution)

**Frontend Service:**
* **Root Directory:** `frontend`
* **Runtime:** `Docker`
* **Note:** Update the `API_URL` in `app.py` to point to your live Render backend URL before deploying.

