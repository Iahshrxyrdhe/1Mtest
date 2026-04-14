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
        # MotherDuck Statements API Endpoint
        url = "https://api.motherduck.com/v1/statements"
        
        headers = {
            "Authorization": f"Bearer {MD_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # SQL Query
        sql = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE CAST(name AS VARCHAR) ILIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 50
        """
        
        # MotherDuck specific payload format
        payload = {
            "statement": sql,
            "queryMode": "REGULAR"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            return {
                "success": False, 
                "error": f"MD API Error {response.status_code}",
                "details": response.text
            }

        res_json = response.json()
        
        # Parsing MotherDuck's nested response
        # Structure: result -> data -> rows
        result_obj = res_json.get("result", {})
        data_obj = result_obj.get("data", {})
        rows = data_obj.get("rows", [])
        
        return {
            "success": True, 
            "count": len(rows), 
            "data": rows
        }
            
    except Exception as e:
        return {"success": False, "error": f"Internal Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
