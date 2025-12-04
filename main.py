import json
from fastapi import FastAPI, HTTPException

from typing import List
from pydantic import BaseModel
from models import ProcessedBuyer, ProcessedSupplier, SupplierMatch


from preprocessor import DataPreprocessor
from matcher import SupplierMatcher


class RecommendRequest(BaseModel):
    buyer_id: str

app = FastAPI()

# Load data and initialize preprocessor
with open("Dataset/buyer_data.json", "r") as f:
    buyers_raw = json.load(f)

with open("Dataset/supplier_data.json", "r") as f:
    suppliers_raw = json.load(f)

preprocessor = DataPreprocessor()
preprocessor.fit(buyers_raw, suppliers_raw)

# Create lookup dictionaries with preprocessed data
buyers_db = {buyer["buyer_id"]: preprocessor.preprocess_buyer(buyer) for buyer in buyers_raw}
suppliers_db = {supplier["supplier_id"]: preprocessor.preprocess_supplier(supplier) for supplier in suppliers_raw}

# Initialize matcher
matcher = SupplierMatcher()
suppliers_list = list(suppliers_db.values())


@app.post("/recommend", response_model=List[SupplierMatch])
async def get_top_suppliers(request: RecommendRequest):
    if request.buyer_id not in buyers_db:
        raise HTTPException(status_code=404, detail="Buyer not found")
    buyer = buyers_db[request.buyer_id]
    return matcher.get_top_suppliers(buyer, suppliers_list, top_n=10)
