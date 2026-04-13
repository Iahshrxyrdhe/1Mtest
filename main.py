from fastapi import FastAPI, Query
from datasets import load_dataset
import os

app = FastAPI()

DATASET_REPO = "tfqdeadlo/Test"
HF_TOKEN = os.getenv("HF_TOKEN")

ds = load_dataset(DATASET_REPO, split="train", streaming=True, token=HF_TOKEN)

@app.get("/")
def home():
    return {"status": "API is Live", "search_endpoint": "/search?q=keyword"}

@app.get("/search")
def search(q: str = Query(..., min_length=2)):
    results = []
    search_query = q.lower()

    try:
        for item in ds:
            # Safe field access
            name = str(item.get("name", "")).lower()
            phone = str(item.get("phoneNumber", ""))
            aadhar = str(item.get("aadharNumber", ""))
            passport = str(item.get("passportNumber", "")).lower()

            if (
                search_query in name or
                search_query in phone or
                search_query in aadhar or
                search_query in passport
            ):
                results.append(item)

            if len(results) >= 15:
                break

        return {"data": results}

    except Exception as e:
        return {"error": str(e)}
