import os
import duckdb
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIG ---
MD_TOKEN = os.getenv("MOTHERDUCK_TOKEN")
DATA_PATH = "https://huggingface.co/datasets/tfqdeadlo/Bom/resolve/main/data.parquet"

@app.get("/")
def home():
    return {"status": "Engine Ready", "mode": "Native DuckDB"}

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    con = None
    try:
        # MotherDuck Native Connection
        # Isse HTTP 404 ka chakkar hi khatam ho jayega
        con = duckdb.connect(f"md:?motherduck_token={MD_TOKEN}")
        
        query = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE CAST(name AS VARCHAR) ILIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 50
        """
        
        # Result fetch karna
        res = con.execute(query).fetchall()
        
        # Column names nikalna
        columns = [desc[0] for desc in con.description]
        results = [dict(zip(columns, row)) for row in res]
        
        return {
            "success": True,
            "count": len(results),
            "data": results
        }
            
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if con:
            con.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
