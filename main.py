import os
import duckdb
from fastapi import FastAPI, Query

app = FastAPI()

# --- CONFIG ---
# MotherDuck token Render ke 'Environment Variables' mein add kar dena
MD_TOKEN = os.getenv("MOTHERDUCK_TOKEN")

# Naya verified path
DATA_PATH = "https://huggingface.co/datasets/tfqdeadlo/Bom/resolve/main/data.parquet"

@app.get("/")
def home():
    return {"status": "Engine Live", "dataset": "Bom_476MB", "message": "Ready to search!"}

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    try:
        # MotherDuck cloud connection
        con = duckdb.connect(f"md:?motherduck_token={MD_TOKEN}")
        
        # Optimized query for large Parquet
        # Column names (name, phoneNumber) apne data ke hisaab se check kar lena
        query = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE CAST(name AS VARCHAR) ILIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 50
        """
        
        df = con.execute(query).df()
        results = df.to_dict(orient="records")
        
        return {"success": True, "count": len(results), "data": results}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if 'con' in locals():
            con.close()
