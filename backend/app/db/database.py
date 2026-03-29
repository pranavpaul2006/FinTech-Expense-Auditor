import sqlite3
import os

# Define where the database file will live
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "claims.db")

def init_db():
    """Creates the SQLite database and the claims table if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create the schema for our FinTech app
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT,
            merchant_name TEXT,
            total_amount REAL,
            currency TEXT,
            justification TEXT,
            ai_status TEXT,
            ai_reasoning TEXT,
            policy_referenced TEXT,
            human_status TEXT DEFAULT 'PENDING',
            auditor_comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ SQLite Database initialized successfully!")

def save_claim(receipt_data: dict, justification: str, audit_verdict: dict, employee_name: str = "Test Employee"):
    """Saves a processed receipt into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO claims (
            employee_name, merchant_name, total_amount, currency, justification, 
            ai_status, ai_reasoning, policy_referenced, human_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        employee_name,
        receipt_data.get('merchant_name', 'Unknown'),
        receipt_data.get('total_amount', 0.0),
        receipt_data.get('currency', 'USD'),
        justification,
        audit_verdict.get('status', 'UNKNOWN'),
        audit_verdict.get('reasoning', ''),
        audit_verdict.get('policy_referenced', ''),
        'PENDING' # The human hasn't reviewed it yet!
    ))
    
    conn.commit()
    claim_id = cursor.lastrowid
    conn.close()
    return claim_id 


if __name__ == "__main__":
    init_db()