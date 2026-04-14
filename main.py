import os
import sqlite3
import pandas as pd
from fastapi import FastAPI, Query
from datasets import load_dataset
from huggingface_hub import login

app = FastAPI()

# --- CONFIGURATION ---
DATASET_REPO = "tfqdeadlo/Test" 
HF_TOKEN = os.getenv("HF_TOKEN")
DB_PATH = "data_cache.db"

def create_fast_index():
    if os.path.exists(DB_PATH):
        print("✅ Database already exists. Skipping indexing.")
        return

    print("⏳ Indexing shuru ho rahi hai... 512MB RAM ka dhyan rakh rahe hain...")
    
    if not HF_TOKEN:
        print("❌ ERROR: HF_TOKEN nahi mila! Render Environment Variables check karo.")
        return

    # Hugging Face Login
    login(token=HF_TOKEN)

    # Dataset loading in streaming mode (Memory efficient)
    ds = load_dataset(DATASET_REPO, split="train", streaming=True, token=HF_TOKEN)

    # SQLite Connection
    conn = sqlite3.connect(DB_PATH)
    
    # Data ko batches mein SQL mein daalna (Taki RAM crash na ho)
    batch_count = 0
    for batch in ds.iter(batch_size=50000):
        df = pd.DataFrame(batch)
        df.to_sql('users', conn, if_exists='append', index=False)
        batch_count += 1
        print(f"📦 Batch {batch_count} processed...")

    # 🔥 SPEED BOOSTER: Creating Indexes
    print("🚀 Creating Search Indexes (Fastest Search)...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON users(name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_phone ON users(phoneNumber)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_aadhar ON users(aadharNumber)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_passport ON users(passportNumber)")
    
    conn.close()
    print("✅ Indexing Complete! API is ready for Goli-ki-raftaar search.")

# Server start hote hi indexing chalu hogi
@app.on_event("startup")
async def startup_event():
    create_fast_index()

@app.get("/")
def home():
    return {
        "status": "Online",
        "message": "Super Fast API is ready",
        "usage": "/search?q=Nitesh"
    }

@app.get("/search")
def search(q: str = Query(..., min_length=2)):
    if not os.path.exists(DB_PATH):
        return {"error": "Database is still being created. Please wait 1 minute."}

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    search_term = f"%{q}%"
    
    # Instant SQL Query
    query = """
    SELECT * FROM users 
    WHERE name LIKE ? 
    OR phoneNumber LIKE ? 
    OR aadharNumber LIKE ? 
    OR passportNumber LIKE ?
    LIMIT 20
    """
    
    cursor = conn.execute(query, (search_term, search_term, search_term, search_term))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"total": len(results), "data": results}
