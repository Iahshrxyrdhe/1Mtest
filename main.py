import os
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Frontend accessibility ke liye
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
        "status": "MotherDuck API Bridge Live",
        "dataset": "Bom_476MB",
        "search_endpoint": "/search?q=XYZ"
    }

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    try:
        # MotherDuck Statements API - Sabse stable tarika
        url = "https://api.motherduck.com/v1/statements"
        
        headers = {
            "Authorization": f"Bearer {MD_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Optimized SQL for Parquet Search
        sql_query = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE CAST(name AS VARCHAR) ILIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 50
        """
        
        payload = {"statement": sql_query}
        
        # MotherDuck ko request bhej rahe hain
        response = requests.post(url, headers=headers, json=payload)
        
        # Error handling agar status code 200 nahi hai
        if response.status_code != 200:
            return {
                "success": False, 
                "error": f"MotherDuck API Error {response.status_code}",
                "details": response.text
            }

        res_json = response.json()
        
        # MotherDuck API response format: result -> data -> rows
        # Hum check kar rahe hain ki data sahi format mein hai ya nahi
        result_obj = res_json.get("result", {})
        data_obj = result_obj.get("data", {})
        rows = data_obj.get("rows", [])
        
        # Agar rows nahi hain lekin query success thi, toh khali list return hogi
        return {
            "success": True, 
            "query": q,
            "count": len(rows), 
            "data": rows
        }
            
    except Exception as e:
        return {
            "success": False, 
            "error": f"Internal Server Error: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    # Render automatic port assign karega
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
