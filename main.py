import os
import duckdb
from fastapi import FastAPI, Query

app = FastAPI()

# --- CONFIGURATION ---
DATA_PATH = "https://huggingface.co/datasets/tfqdeadlo/Test/resolve/main/data.parquet"
HF_TOKEN = os.getenv("HF_TOKEN")

@app.get("/")
def home():
    return {
        "status": "DuckDB Engine Live",
        "dataset": "tfqdeadlo/Test",
        "mode": "Direct_Parquet_Streaming"
    }

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    con = duckdb.connect()
    try:
        # 1. Extensions load karo
        con.execute("INSTALL httpfs; LOAD httpfs;")
        
        # 2. Authentication (Naya Secret Method)
        if HF_TOKEN:
            try:
                # DuckDB v0.10.0+ ke liye naya method
                con.execute(f"CREATE OR REPLACE SECRET (TYPE HTTP, TOKEN '{HF_TOKEN}');")
            except:
                # Purane versions ke liye fallback
                con.execute(f"SET http_headers = 'Authorization: Bearer {HF_TOKEN}';")

        # 3. Query Execution
        # ILIKE use kiya hai taaki Search Case-Insensitive ho (Bhai = bhai)
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
