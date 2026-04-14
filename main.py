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
    return {"status": "HTTP Bridge Active", "engine": "MotherDuck Cloud"}

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    try:
        # MotherDuck HTTP API Endpoint
        # Note: 'my_db' is default, hum direct S3/HTTP link query kar rahe hain
        url = "https://api.motherduck.com/v1/sql"
        
        headers = {
            "Authorization": f"Bearer {MD_TOKEN}",
            "Content-Type": "application/json"
        }
        
        sql_query = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE CAST(name AS VARCHAR) ILIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 50
        """
        
        payload = {"query": sql_query}
        
        # Requesting MotherDuck Cloud
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        
        if response.status_code == 200:
            # MotherDuck API results ko format mein nikaalte hain
            # Res_data mein 'rows' aur 'schema' hota hai
            rows = res_data.get("data", {}).get("rows", [])
            return {"success": True, "count": len(rows), "data": rows}
        else:
            return {"success": False, "error": res_data.get("error", "API Error")}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
