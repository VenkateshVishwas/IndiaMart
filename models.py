from pydantic import BaseModel
from typing import List


# Raw data models
class Buyer(BaseModel):
    buyer_id: str
    name: str
    state: str
    city: str
    search_history: List[str]
    past_orders: List[str]


class Supplier(BaseModel):
    supplier_id: str
    supplier_name: str
    category: str
    rating: float
    response_time_ms: int
    state: str
    city: str
    products_offered: List[str]


# Processed data models (with encoded fields)
class ProcessedBuyer(BaseModel):
    buyer_id: str
    name: str
    state: str
    state_encoded: int
    city: str
    search_history: List[str]
    search_history_encoded: List[int]
    past_orders: List[str]
    past_orders_encoded: List[int]


class ProcessedSupplier(BaseModel):
    supplier_id: str
    supplier_name: str
    category: str
    category_encoded: int
    rating: float
    response_time_ms: int
    state: str
    state_encoded: int
    city: str
    products_offered: List[str]
    products_offered_encoded: List[int]


class SupplierMatch(BaseModel):
    supplier: "ProcessedSupplier"
    score: float
    location_score: float
    search_score: float
    orders_score: float
    rating_score: float
    response_score: float
