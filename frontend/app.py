import streamlit as st
import requests

# Backend URL
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Expense Auditor", layout="wide")

st.sidebar.title("Navigation")
view_mode = st.sidebar.radio("Select View", ["Employee Portal", "Finance Dashboard"])

if view_mode == "Employee Portal":
    st.title("💸 Submit an Expense")
    st.markdown("Upload your receipt and provide a business justification.")
    
    with st.form("expense_form"):
        receipt_file = st.file_uploader("Upload Receipt (Image or PDF)", type=["png", "jpg", "jpeg", "pdf"])
        justification = st.text_area("Business Purpose", placeholder="e.g., Dinner with a prospective client.")
        submitted = st.form_submit_button("Submit Claim")
        
        if submitted:
            if receipt_file and justification:
                with st.spinner("Uploading and analyzing..."):
                    # Send data to FastAPI
                    files = {"file": (receipt_file.name, receipt_file.getvalue(), receipt_file.type)}
                    data = {"justification": justification}
                    
                    try:
                        response = requests.post(f"{API_URL}/api/upload-receipt", files=files, data=data)
                        if response.status_code == 200:
                            st.success("Receipt sent to backend successfully!")
                            st.json(response.json())
                        else:
                            st.error(f"Error communicating with backend: {response.status_code}")
                    except requests.exceptions.ConnectionError:
                        st.error("Backend is down! Please start the FastAPI server.")
            else:
                st.warning("Please upload a receipt and provide a justification.")

elif view_mode == "Finance Dashboard":
    st.title("📊 Finance Auditor Dashboard")
    st.markdown("Review flagged claims and policy violations.")
    st.info("The interactive data table and side-by-side view will be built here in Phase 2.")