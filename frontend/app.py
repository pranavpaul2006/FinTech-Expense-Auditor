import streamlit as st
import requests
import pandas as pd
from PIL import Image
import datetime 

# Backend Endpoints
API_UPLOAD = "http://localhost:8000/api/upload-receipt"
API_CLAIMS = "http://localhost:8000/api/claims"
API_UPDATE = "http://localhost:8000/api/update-claim"

st.set_page_config(page_title="AI Expense Auditor", page_icon="🧾", layout="wide")

# --- SECURITY GATE (RBAC) ---
st.sidebar.title("🔐 Access Control")
# NEW: Added C-Suite Analytics to the radio menu
view_mode = st.sidebar.radio("Select Interface:", ["Employee Portal", "Finance Auditor Dashboard", "C-Suite Analytics"])

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

if view_mode in ["Finance Auditor Dashboard", "C-Suite Analytics"]:
    st.sidebar.markdown("---")
    pin = st.sidebar.text_input("Enter Admin PIN", type="password", help="AUDIT-2026")
    if pin == "AUDIT-2026":
        st.session_state.is_admin = True
        st.sidebar.success("Access Granted.")
    elif pin:
        st.session_state.is_admin = False
        st.sidebar.error("Invalid PIN.")
else:
    st.session_state.is_admin = False

# ==========================================
# VIEW 1: THE EMPLOYEE PORTAL
# ==========================================
if view_mode == "Employee Portal" or not st.session_state.is_admin:
    st.title("🧾 Employee Expense Portal")
    
    if 'employee_name' not in st.session_state:
        st.session_state.employee_name = None
        st.session_state.employee_id = None

    if st.session_state.employee_name is None:
        st.markdown("### 🔒 Employee Sign-In")
        col_login, _ = st.columns([1, 2])
        with col_login:
            emp_name_input = st.text_input("Full Name", placeholder="e.g., Pranav Paul")
            emp_id_input = st.text_input("Employee ID", placeholder="e.g., EMP-1042")
            if st.button("Access Portal", type="primary"):
                if emp_name_input.strip() == "" or emp_id_input.strip() == "":
                    st.error("Please enter both your Name and Employee ID.")
                else:
                    st.session_state.employee_name = emp_name_input.strip()
                    st.session_state.employee_id = emp_id_input.strip()
                    st.rerun() 
    else:
        st.success(f"👋 Welcome back, **{st.session_state.employee_name}**!")
        if st.button("Sign Out"):
            st.session_state.employee_name = None
            st.session_state.employee_id = None
            st.rerun()
            
        st.markdown("---")
        
        # --- NEW: TABBED VIEW FOR UPLOADS AND HISTORY ---
        tab_upload, tab_history = st.tabs(["📤 Submit New Claim", "🔔 My Claim Alerts"])

        with tab_upload:
            st.markdown("Upload your receipts here. Our AI auditor will process them instantly.")
            col1, col2 = st.columns([1, 1.2])

            with col1:
                st.subheader("Submit New Claim")
                uploaded_file = st.file_uploader("Upload Receipt (JPG, PNG, PDF)", type=["jpg", "jpeg", "png", "pdf"])
                justification = st.text_input("Business Justification", placeholder="e.g., Client lunch")
                claimed_date = st.date_input("Date of Expense", datetime.date.today())
                submit_button = st.button("Run AI Audit", type="primary", use_container_width=True)

            if submit_button:
                if not uploaded_file or not justification:
                    st.warning("⚠️ Please upload a receipt and provide a justification.")
                else:
                    with col2:
                        st.subheader("Audit Results")
                        if uploaded_file.type == "application/pdf":
                            st.info("📄 PDF Document Uploaded")
                        else:
                            image = Image.open(uploaded_file)
                            st.image(image, caption="Uploaded Receipt", use_column_width=True)
                        
                        with st.spinner("🧠 AI is auditing your claim..."):
                            try:
                                uploaded_file.seek(0)
                                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                                data = {
                                    "justification": justification, 
                                    "claimed_date": claimed_date.strftime("%Y-%m-%d"),
                                    "employee_name": st.session_state.employee_name,
                                    "employee_id": st.session_state.employee_id
                                }
                                
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
                                        
                                    st.info(f"**AI Reasoning:** {audit.get('reasoning')}")
                                    st.caption(f"**Policy Referenced:** {audit.get('policy_referenced')}")
                                else:
                                    st.error(f"Backend Error: {response.text}")
                            except Exception as e:
                                st.error(f"Connection Error: {e}")

        # --- NEW: HISTORY TAB LOGIC ---
        with tab_history:
            st.subheader("Your Submission History")
            try:
                res = requests.get(f"http://localhost:8000/api/my-claims/{st.session_state.employee_id}")
                if res.status_code == 200:
                    user_claims = res.json().get("claims", [])
                    if not user_claims:
                        st.info("You have no past claims.")
                    else:
                        for claim in user_claims:
                            final_status = claim['human_status'] if claim['human_status'] != 'PENDING' else claim['ai_status']
                            
                            if final_status == "APPROVED":
                                st.success(f"✅ **APPROVED:** {claim['merchant_name']} - ${claim['total_amount']}")
                            elif final_status == "REJECTED":
                                st.error(f"❌ **REJECTED:** {claim['merchant_name']} - ${claim['total_amount']} \n\n*Reason: {claim['ai_reasoning']}*")
                            else:
                                st.warning(f"⏳ **PENDING REVIEW:** {claim['merchant_name']} - ${claim['total_amount']}")
            except Exception as e:
                st.error("Could not load notifications.")

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
                display_df = df[['id', 'employee_name', 'merchant_name', 'total_amount', 'ai_status', 'human_status', 'auditor_comment', 'created_at']]
                
                st.dataframe(
                    display_df.style.map(
                        lambda x: 'background-color: #ffcccc' if x == 'FLAGGED_FOR_REVIEW' else ('background-color: #ccffcc' if x == 'APPROVED' else ''),
                        subset=['ai_status']
                    ),
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("---")
                st.subheader("✍️ Human Override Panel")
                
                colA, colB, colC = st.columns(3)
                with colA:
                    available_ids = display_df['id'].tolist()
                    selected_id = st.selectbox("Select Claim ID to Review", available_ids)
                
                if selected_id:
                    selected_claim = df[df['id'] == selected_id].iloc[0]
                    with st.expander(f"📄 View Full AI Audit File for Claim #{selected_id}", expanded=True):
                        st.markdown(f"**Employee Justification:** {selected_claim['justification']}")
                        st.markdown(f"**AI Reasoning:** {selected_claim['ai_reasoning']}")
                        st.info(f"**Corporate Policy Applied:** *\"{selected_claim['policy_referenced']}\"*")

                with colB:
                    new_status = st.selectbox("Final Human Verdict", ["APPROVED", "REJECTED", "NEEDS_MORE_INFO"])
                
                with colC:
                    auditor_comment = st.text_input("Auditor Comment", placeholder="e.g., Verified exchange rate.")
                
                if st.button("Submit Final Verdict", type="primary"):
                    if not auditor_comment:
                        st.warning("⚠️ A justification comment is required to override the AI.")
                    else:
                        update_payload = {"claim_id": selected_id, "new_status": new_status, "comment": auditor_comment}
                        update_res = requests.post(API_UPDATE, json=update_payload)
                        if update_res.status_code == 200:
                            st.success(f"✅ Claim #{selected_id} successfully updated!")
                            st.rerun() 
        else:
            st.error("Failed to load database.")
    except Exception as e:
        st.error(f"Could not connect to database endpoint: {e}")

# ==========================================
# VIEW 3: C-SUITE ANALYTICS
# ==========================================
elif view_mode == "C-Suite Analytics" and st.session_state.is_admin:
    st.title("📊 C-Suite Analytics Dashboard")
    st.markdown("High-level overview of corporate spending and AI auditing efficiency.")
    
    
    try:
        response = requests.get(API_CLAIMS)
        if response.status_code == 200:
            claims_data = response.json().get("data", [])
            if not claims_data:
                st.info("No data available yet. Have employees submit claims to populate charts.")
            else:
                df = pd.DataFrame(claims_data)
                
                # Convert total_amount to numeric just in case
                df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce').fillna(0)
                
                # Top Metrics
                col1, col2, col3 = st.columns(3)
                total_spend = df[df['ai_status'] == 'APPROVED']['total_amount'].sum()
                fraud_prevented = df[df['ai_status'] == 'REJECTED']['total_amount'].sum()
                total_claims = len(df)
                
                col1.metric("Total Approved Spend", f"${total_spend:,.2f}")
                col2.metric("Fraud / Violations Blocked", f"${fraud_prevented:,.2f}")
                col3.metric("Total Claims Processed", total_claims)
                
                st.markdown("---")
                
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    st.subheader("Spend by Merchant")
                    merchant_spend = df.groupby('merchant_name')['total_amount'].sum().sort_values(ascending=False).head(5)
                    st.bar_chart(merchant_spend)
                    
                with col_chart2:
                    st.subheader("AI Decision Breakdown")
                    status_counts = df['ai_status'].value_counts()
                    st.bar_chart(status_counts)
                    
    except Exception as e:
        st.error(f"Could not load analytics: {e}")