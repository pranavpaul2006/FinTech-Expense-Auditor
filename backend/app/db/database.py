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
            employee_id TEXT,
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

def save_claim(employee_id, employee_name, merchant_name, total_amount, currency, justification, ai_status, ai_reasoning, policy_referenced):
    """Saves a processed receipt into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO claims (
            employee_id, employee_name, merchant_name, total_amount, currency, justification, 
            ai_status, ai_reasoning, policy_referenced, human_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        employee_id,
        employee_name,
        merchant_name,
        total_amount,
        currency,
        justification,
        ai_status,
        ai_reasoning,
        policy_referenced,
        'PENDING' # The human hasn't reviewed it yet!
    ))
    
    conn.commit()
    claim_id = cursor.lastrowid
    conn.close()
    return claim_id 

def get_all_claims():
    """Fetches all claims from the database for the Auditor Dashboard."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # This formats the rows as JSON dictionaries
    cursor = conn.cursor()
    # Sort them so the newest ones are at the top
    cursor.execute("SELECT * FROM claims ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_claim_status(claim_id: int, new_status: str, comment: str):
    """Allows a human auditor to override the AI and leave a comment."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE claims 
        SET human_status = ?, auditor_comment = ? 
        WHERE id = ?
    ''', (new_status, comment, claim_id))
    
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    init_db()