import os
import duckdb
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS allow kar rahe hain taaki agar tu frontend se connect kare toh error na aaye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIG ---
# Token Render ke dashboard se aayega
MD_TOKEN = os.getenv("MOTHERDUCK_TOKEN")
# Naya verified path jo humne set kiya tha
DATA_PATH = "https://huggingface.co/datasets/tfqdeadlo/Bom/resolve/main/data.parquet"

@app.get("/")
def home():
    return {
        "status": "MotherDuck Engine Live",
        "database": "Bom_476MB",
        "endpoint": "/search?q=YOUR_QUERY"
    }

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    con = None
    try:
        # MotherDuck cloud connection (Compatible with v1.1.3)
        con = duckdb.connect(f"md:?motherduck_token={MD_TOKEN}")
        
        # Search Query:
        # Hum columns ko VARCHAR mein cast kar rahe hain taaki search fail na ho
        # 'name' aur 'phoneNumber' columns ko scan karega
        query = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE CAST(name AS VARCHAR) ILIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 50
        """
        
        # Execute and convert to Dictionary
        df = con.execute(query).df()
        results = df.to_dict(orient="records")
        
        return {
            "success": True, 
            "query": q,
            "count": len(results), 
            "data": results
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
    # Render automatic PORT assign karta hai
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
