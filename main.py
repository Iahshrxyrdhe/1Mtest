import os
import duckdb
from fastapi import FastAPI, Query

app = FastAPI()

# --- CONFIG ---
# Direct 'download' link use kar rahe hain jo DuckDB ke liye best hai
DATA_PATH = "https://huggingface.co/datasets/tfqdeadlo/Test/data.parquet"
HF_TOKEN = os.getenv("HF_TOKEN")

@app.get("/")
def home():
    return {"status": "DuckDB Live", "mode": "Streaming"}

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    con = duckdb.connect()
    try:
        con.execute("INSTALL httpfs; LOAD httpfs;")
        
        # Token ko headers mein set karne ka sabse stable method for Render
        if HF_TOKEN:
            # Purana setting remove karke fresh set karte hain
            con.execute(f"SET http_keep_alive=false;") 
            con.execute(f"SET http_headers = 'Authorization: Bearer {HF_TOKEN}';")

        # Query
        query = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE name ILIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 20
        """
        
        df = con.execute(query).df()
        results = df.to_dict(orient="records")
        
        return {"success": True, "count": len(results), "data": results}
        
    except Exception as e:
        error_msg = str(e)
        # Agar Magic Bytes error abhi bhi aaye, toh link mein issue ho sakta hai
        return {
            "success": False, 
            "error": error_msg,
            "note": "If magic bytes error persists, try making the HF repo PUBLIC to test."
        }
    finally:
        con.close()
