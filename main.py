from fastapi import FastAPI, Query
from datasets import load_dataset
import pandas as pd
import os

app = FastAPI()

# Hugging Face Repo ID (Apna wala dalo)
DATASET_REPO = "tfqdeadlo/Test"
HF_TOKEN = os.getenv("HF_TOKEN")

# Data load (Streaming mode memory nahi khayega)
ds = load_dataset(DATASET_REPO, split="train", streaming=True, token=HF_TOKEN)

@app.get("/")
def home():
    return {"status": "API is Live", "search_endpoint": "/search?q=keyword"}

@app.get("/search")
def search(q: str = Query(..., min_length=2)):
    results = []
    search_query = q.lower()
    
    # 10,000 rows ka batch check karega speed ke liye
    for batch in ds.iter(batch_size=10000):
        df = pd.DataFrame(batch)
        
        # In columns mein search karega (Name, Phone, Aadhaar, Passport)
        mask = (
            df['name'].str.contains(search_query, case=False, na=False) |
            df['phoneNumber'].astype(str).str.contains(search_query, na=False) |
            df['aadharNumber'].astype(str).str.contains(search_query, na=False) |
            df['passportNumber'].str.contains(search_query, case=False, na=False)
        )
        
        filtered_df = df[mask]
        if not filtered_df.empty:
            results.extend(filtered_df.to_dict(orient='records'))
            
        # Top 15 results milte hi rok dega (Taki API slow na ho)
        if len(results) >= 15:
            break
            
    return {"data": results}
