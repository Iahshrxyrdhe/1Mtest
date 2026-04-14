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
    return {"status": "Bridge Online", "endpoint": "/search"}

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    try:
        # MotherDuck Standard SQL Endpoint
        url = "https://api.motherduck.com/v1/sql"
        
        headers = {
            "Authorization": f"Bearer {MD_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Casting and Searching
        sql_query = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE CAST(name AS VARCHAR) ILIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 50
        """
        
        # MotherDuck expects {"query": "SQL..."}
        payload = {"query": sql_query}
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return {
                "success": False, 
                "error": f"MD Error {response.status_code}",
                "details": response.text
            }

        res_json = response.json()
        
        # MotherDuck /v1/sql response structure parsing:
        # Data normally 'data' key ke andar 'rows' mein hota hai
        data_block = res_json.get("data", {})
        rows = data_block.get("rows", [])
        
        return {
            "success": True, 
            "query": q,
            "count": len(rows), 
            "data": rows
        }
            
    except Exception as e:
        return {"success": False, "error": f"Connection Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
