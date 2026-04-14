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
# Nayi wali repo ka path
DATA_PATH = "https://huggingface.co/datasets/tfqdeadlo/Bom/resolve/main/data.parquet"

@app.get("/")
def home():
    return {"status": "Bridge Online", "method": "HTTP-Only"}

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    try:
        # MotherDuck API Endpoint (v1/sql)
        url = "https://api.motherduck.com/v1/sql"
        
        headers = {
            "Authorization": f"Bearer {MD_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Simple SQL Query
        sql_query = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE CAST(name AS VARCHAR) ILIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 50
        """
        
        # Request payload
        payload = {"query": sql_query}
        
        # Sending request to MotherDuck
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return {"success": False, "error": f"MD API Error {response.status_code}", "msg": response.text}

        res_json = response.json()
        
        # Parsing: MotherDuck usually returns data in result set
        # Agar structure 'data' ke andar 'rows' hai:
        rows = res_json.get("data", {}).get("rows", [])
        
        return {
            "success": True, 
            "query": q,
            "count": len(rows), 
            "data": rows
        }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
