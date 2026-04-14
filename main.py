import os
import duckdb
from fastapi import FastAPI, Query

app = FastAPI()

# --- CONFIG ---
# Screenshot ke hisab se direct parquet link
DATA_PATH = "https://huggingface.co/datasets/tfqdeadlo/Test/resolve/main/data.parquet"
HF_TOKEN = os.getenv("HF_TOKEN")

@app.get("/")
def home():
    return {"status": "DuckDB Live", "dataset": "tfqdeadlo/Test", "file": "data.parquet"}

@app.get("/search")
def search(q: str = Query(..., min_length=3)):
    try:
        # 1. DuckDB instance initialize karo
        con = duckdb.connect()
        
        # 2. Remote reading extensions load karo
        con.execute("INSTALL httpfs; LOAD httpfs;")
        
        # 3. Agar repo private hai (ya token required hai)
        if HF_TOKEN:
            con.execute(f"SET http_headers = '{{ \"Authorization\": \"Bearer {HF_TOKEN}\" }}';")

        # 4. SQL Query (DuckDB sidha Parquet file ko table ki tarah read karega)
        # Note: 'name' aur 'phoneNumber' columns tere data mein hone chahiye
        query = f"""
            SELECT * FROM read_parquet('{DATA_PATH}') 
            WHERE name LIKE '%{q}%' 
            OR CAST(phoneNumber AS VARCHAR) LIKE '%{q}%'
            LIMIT 20
        """
        
        # 5. Pandas Dataframe ke zariye result nikalo
        df = con.execute(query).df()
        results = df.to_dict(orient="records")
        
        return {
            "success": True,
            "count": len(results),
            "data": results
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Render port setting
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
