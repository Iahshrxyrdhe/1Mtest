import os
import requests
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
    return {"status": "HTTP Bridge Active", "info": "No DuckDB library used"}

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    try:
        # MotherDuck v0 SQL Endpoint (Standard for simple requests)
        url = "https://api.motherduck.com/v0/sql"
        
        headers = {
            "Authorization": f"Bearer {MD_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Casting names and numbers to string for searching
        sql_query = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE CAST(name AS VARCHAR) ILIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 50
        """
        
        payload = {"query": sql_query}
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return {
                "success": False, 
                "error": f"MD Error {response.status_code}",
                "details": response.text
            }

        res_json = response.json()
        
        # MotherDuck response structure: rows normally directly inside result or data
        # Let's handle both common API formats
        data_block = res_json.get("result", res_json.get("data", {}))
        rows = data_block.get("rows", [])
        
        return {
            "success": True, 
            "count": len(rows), 
            "data": rows
        }
            
    except Exception as e:
        return {"success": False, "error": f"Python Exception: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
