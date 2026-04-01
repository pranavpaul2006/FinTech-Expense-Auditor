import streamlit as st
import requests
import pandas as pd
from PIL import Image

# Backend Endpoints
API_UPLOAD = "http://localhost:8000/api/upload-receipt"
API_CLAIMS = "http://localhost:8000/api/claims"
API_UPDATE = "http://localhost:8000/api/update-claim"

# Page Configuration
st.set_page_config(page_title="AI Expense Auditor", page_icon="🧾", layout="wide")

# --- SECURITY GATE (RBAC) ---
st.sidebar.title("🔐 Access Control")
view_mode = st.sidebar.radio("Select Interface:", ["Employee Portal", "Finance Auditor Dashboard"])

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

if view_mode == "Finance Auditor Dashboard":
    st.sidebar.markdown("---")
    pin = st.sidebar.text_input("Enter Admin PIN", type="password", help="AUDIT-2026")
    if pin == "AUDIT-2026":
        st.session_state.is_admin = True
        st.sidebar.success("Access Granted. Welcome, Auditor.")
    elif pin:
        st.session_state.is_admin = False
        st.sidebar.error("Invalid PIN. Intrusion logged.")
else:
    st.session_state.is_admin = False


# ==========================================
# VIEW 1: THE EMPLOYEE PORTAL
# ==========================================
if view_mode == "Employee Portal" or not st.session_state.is_admin:
    st.title("🧾 Employee Expense Portal")
    st.markdown("Upload your receipts here. Our AI auditor will process them instantly.")

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("Submit New Claim")
        uploaded_file = st.file_uploader("Upload Receipt (JPG, PNG)", type=["jpg", "jpeg", "png"])
        justification = st.text_input("Business Justification", placeholder="e.g., Client lunch with John Doe")
        submit_button = st.button("Run AI Audit", type="primary", use_container_width=True)

    if submit_button:
        if not uploaded_file or not justification:
            st.warning("⚠️ Please upload a receipt and provide a justification.")
        else:
            with col2:
                st.subheader("Audit Results")
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Receipt", use_column_width=True)
                
                with st.spinner("🧠 AI is auditing your claim..."):
                    try:
                        uploaded_file.seek(0)
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        
                        data = {"justification": justification, "employee_name": "Jopaa (You)"}
                        
                        response = requests.post(API_UPLOAD, files=files, data=data)
                        
                        if response.status_code == 200:
                            result = response.json()
                            audit = result["audit_verdict"]
                            
                            status = audit.get("status", "UNKNOWN")
                            if status == "APPROVED":
                                st.success(f"✅ AI DECISION: {status}")
                            elif status == "REJECTED":
                                st.error(f"❌ AI DECISION: {status}")
                            else:
                                st.warning(f"⚠️ AI DECISION: {status}")
                                
                            st.info(f"**Policy Referenced:** {audit.get('policy_referenced')}")
                            st.caption(f"Claim ID #{result.get('claim_id')} saved to database.")
                        else:
                            st.error(f"Backend Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")


# ==========================================
# VIEW 2: THE SECURE AUDITOR DASHBOARD
# ==========================================
elif view_mode == "Finance Auditor Dashboard" and st.session_state.is_admin:
    st.title("🛡️ Finance Auditor Queue")
    st.markdown("Review AI-flagged claims and provide final human authorization.")

    try:
        response = requests.get(API_CLAIMS)
        if response.status_code == 200:
            claims_data = response.json().get("data", [])
            
            if not claims_data:
                st.info("🎉 No pending claims in the queue! Go grab a coffee.")
            else:
                df = pd.DataFrame(claims_data)
                
                # Added 'auditor_comment' to the table view
                display_df = df[['id', 'employee_name', 'merchant_name', 'total_amount', 'ai_status', 'human_status', 'auditor_comment', 'created_at']]
                
                st.dataframe(
                    display_df.style.applymap(
                        lambda x: 'background-color: #ffcccc' if x == 'FLAGGED_FOR_REVIEW' else ('background-color: #ccffcc' if x == 'APPROVED' else ''),
                        subset=['ai_status']
                    ),
                    use_container_width=True,
                    hide_index=True
                )
                
                # --- HUMAN-IN-THE-LOOP CONTROL PANEL ---
                st.markdown("---")
                st.subheader("✍️ Human Override Panel")
                st.markdown("Select a Claim ID from the table above to issue a final verdict.")
                
                colA, colB, colC = st.columns(3)
                
                with colA:
                    available_ids = display_df['id'].tolist()
                    selected_id = st.selectbox("Select Claim ID to Review", available_ids)
                
                # --- THE DYNAMIC DETAIL VIEW (POP-UP) ---
                if selected_id:
                    # Find the specific row in the database matching the ID
                    selected_claim = df[df['id'] == selected_id].iloc[0]
                    with st.expander(f"📄 View Full AI Audit File for Claim #{selected_id}", expanded=True):
                        st.markdown(f"**Employee Justification:** {selected_claim['justification']}")
                        st.markdown(f"**AI Reasoning:** {selected_claim['ai_reasoning']}")
                        st.info(f"**Corporate Policy Applied:** *\"{selected_claim['policy_referenced']}\"*")
                # ---------------------------------------------

                with colB:
                    new_status = st.selectbox("Final Human Verdict", ["APPROVED", "REJECTED", "NEEDS_MORE_INFO"])
                
                with colC:
                    auditor_comment = st.text_input("Auditor Comment", placeholder="e.g., Verified exchange rate.")
                
                if st.button("Submit Final Verdict", type="primary"):
                    if not auditor_comment:
                        st.warning("⚠️ A justification comment is required to override the AI.")
                    else:
                        with st.spinner("Saving to secure database..."):
                            update_payload = {
                                "claim_id": selected_id,
                                "new_status": new_status,
                                "comment": auditor_comment
                            }
                            update_res = requests.post(API_UPDATE, json=update_payload)
                            
                            if update_res.status_code == 200:
                                st.success(f"✅ Claim #{selected_id} successfully updated to {new_status}!")
                                st.rerun() 
                            else:
                                st.error("Failed to update database.")
                                
        else:
            st.error("Failed to load database.")
    except Exception as e:
        st.error(f"Could not connect to database endpoint: {e}")