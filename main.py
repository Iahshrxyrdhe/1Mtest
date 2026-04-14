import os
import sqlite3
import pandas as pd
from fastapi import FastAPI, Query, BackgroundTasks
from datasets import load_dataset
from huggingface_hub import login

app = FastAPI()

# --- CONFIGURATION ---
DATASET_REPO = "tfqdeadlo/Test" 
HF_TOKEN = os.getenv("HF_TOKEN")
DB_PATH = "data_cache.db"

def create_fast_index():
    if os.path.exists(DB_PATH):
        print("✅ Database already exists.")
        return

    print("⏳ Background Indexing Started...")
    try:
        if not HF_TOKEN:
            print("❌ ERROR: HF_TOKEN missing!")
            return

        login(token=HF_TOKEN)
        ds = load_dataset(DATASET_REPO, split="train", streaming=True, token=HF_TOKEN)

        conn = sqlite3.connect(DB_PATH)
        
        # Batch processing to keep RAM under 512MB
        for batch in ds.iter(batch_size=50000):
            df = pd.DataFrame(batch)
            df.to_sql('users', conn, if_exists='append', index=False)
            print("📦 Batch added to SQLite...")

        # Speed booster indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON users(name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_phone ON users(phoneNumber)")
        conn.close()
        print("✅ Indexing Complete! Search is now super fast.")
    except Exception as e:
        print(f"❌ Indexing Error: {e}")

@app.on_event("startup")
async def startup_event():
    # Server ko turant start karne ke liye hum indexing ko 
    # startup mein nahi balki pehle request par ya background mein chalayenge
    print("🚀 Server is starting... use /init to build DB if not exists")

@app.get("/")
def home():
    db_status = "Ready" if os.path.exists(DB_PATH) else "Not Ready (Go to /init)"
    return {
        "status": "Online",
        "database": db_status,
        "usage": "/search?q=YourQuery",
        "setup": "/init (Run this if database is not ready)"
    }

@app.get("/init")
def init_db(background_tasks: BackgroundTasks):
    if os.path.exists(DB_PATH):
        return {"message": "Database already exists!"}
    background_tasks.add_task(create_fast_index)
    return {"message": "Indexing started in background. Please wait 2-5 minutes."}

@app.get("/search")
def search(q: str = Query(..., min_length=2)):
    if not os.path.exists(DB_PATH):
        return {"error": "Database not ready. Run /init first and wait a few minutes."}

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    search_term = f"%{q}%"
    
    query = """
    SELECT * FROM users 
    WHERE name LIKE ? 
    OR phoneNumber LIKE ? 
    OR aadharNumber LIKE ? 
    LIMIT 20
    """
    
    cursor = conn.execute(query, (search_term, search_term, search_term))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"count": len(results), "data": results}
