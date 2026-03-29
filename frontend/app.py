import streamlit as st
import requests
from PIL import Image
import io

# Tell the frontend where the backend brain lives
API_URL = "http://localhost:8000/api/upload-receipt"

# 1. Page Configuration
st.set_page_config(page_title="AI Expense Auditor", page_icon="🧾", layout="wide")

# 2. Main Header
st.title("🧾 AI-Powered FinTech Auditor")
st.markdown("Upload an expense receipt. The AI will extract the data, translate foreign languages, and instantly audit it against the corporate policy.")

# 3. Layout: Two Columns
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Submit Expense Claim")
    uploaded_file = st.file_uploader("Upload Receipt (JPG, PNG)", type=["jpg", "jpeg", "png"])
    justification = st.text_input("Business Justification", placeholder="e.g., Client lunch with John Doe")
    submit_button = st.button("Run AI Audit", type="primary", use_container_width=True)

# 4. The Action Logic
if submit_button:
    if not uploaded_file or not justification:
        st.warning("⚠️ Please upload a receipt and provide a justification.")
    else:
        with col2:
            st.subheader("2. Audit Results")
            
            # Show the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Receipt", use_column_width=True)            
            with st.spinner("🧠 AI is extracting data and querying the vector database..."):
                try:
                    uploaded_file.seek(0)
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {"justification": justification}
                    
                    response = requests.post(API_URL, files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        audit = result["audit_verdict"]
                        receipt_data = result["receipt_details"]
                        
                        status = audit.get("status", "UNKNOWN")
                        if status == "APPROVED":
                            st.success(f"✅ STATUS: {status}")
                        elif status == "REJECTED":
                            st.error(f"❌ STATUS: {status}")
                        else:
                            st.warning(f"⚠️ STATUS: {status}")
                            
                        st.markdown(f"**AI Reasoning:** {audit.get('reasoning')}")
                        st.info(f"**Policy Rule Applied:** *\"{audit.get('policy_referenced')}\"*")
                        
                        with st.expander("View Raw Extracted Data (JSON)"):
                            st.json(receipt_data)
                            
                    else:
                        st.error(f"Backend Error: {response.status_code} - {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("🚨 CRITICAL: Could not connect to the backend. Is your FastAPI server running on port 8000?")