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
    return {"status": "Native Engine Active", "version": "DuckDB-0.10.2"}

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    con = None
    try:
        # MotherDuck Native Connection
        # Ye version stable hai aur MotherDuck ko connect kar lega
        con = duckdb.connect(f"md:?motherduck_token={MD_TOKEN}")
        
        query = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE CAST(name AS VARCHAR) ILIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 50
        """
        
        # Result fetching
        df = con.execute(query).df()
        results = df.to_dict(orient="records")
        
        return {
            "success": True, 
            "count": len(results), 
            "data": results
        }
            
    except Exception as e:
        return {"success": False, "error": f"Native Error: {str(e)}"}
    finally:
        if con:
            con.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
