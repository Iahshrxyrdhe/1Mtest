import os
import duckdb
from fastapi import FastAPI, Query

app = FastAPI()

# --- CONFIG ---
# Hum token ko sidha URL mein add karenge as a parameter
HF_TOKEN = os.getenv("HF_TOKEN")
BASE_URL = "https://huggingface.co/datasets/tfqdeadlo/Test/resolve/main/data.parquet"

# Agar token hai toh URL ke aage jod do, varna simple rehne do
if HF_TOKEN:
    DATA_PATH = f"{BASE_URL}?token={HF_TOKEN}"
else:
    DATA_PATH = BASE_URL

@app.get("/")
def home():
    return {"status": "DuckDB Engine Live", "mode": "Direct_Link_Streaming"}

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    con = duckdb.connect()
    try:
        # Extensions load karo
        con.execute("INSTALL httpfs; LOAD httpfs;")
        
        # Simple Query: Bina kisi header setting ke
        # ILIKE search ko case-insensitive banata hai
        query = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE name ILIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 20
        """
        
        df = con.execute(query).df()
        results = df.to_dict(orient="records")
        
        return {
            "success": True,
            "count": len(results),
            "data": results
        }
        
    except Exception as e:
        return {
            "success": False, 
            "error": str(e),
            "tip": "Check if column names 'name' and 'phoneNumber' exist in your parquet file."
        }
    finally:
        con.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
