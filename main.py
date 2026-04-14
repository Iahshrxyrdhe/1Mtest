import os
import duckdb
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Frontend connectivity ke liye
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
    return {
        "status": "MotherDuck Engine Active",
        "dataset": "Bom_476MB",
        "search_at": "/search?q=XYZ"
    }

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    con = None
    try:
        # MotherDuck cloud connection
        con = duckdb.connect(f"md:?motherduck_token={MD_TOKEN}")
        
        # Searching columns: 'name' and 'phoneNumber'
        # ILIKE is case-insensitive
        query = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE CAST(name AS VARCHAR) ILIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 50
        """
        
        # DuckDB native execution (No Pandas needed)
        cursor = con.execute(query)
        results = cursor.fetchall()
        
        # Column names fetch karo taaki dictionary bana sakein
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in results]
        
        return {
            "success": True, 
            "count": len(data), 
            "data": data
        }
        
    except Exception as e:
        return {
            "success": False, 
            "error": str(e)
        }
    finally:
        if con:
            con.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
