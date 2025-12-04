from typing import List, Dict
from models import Buyer, Supplier, ProcessedBuyer, ProcessedSupplier


class DataPreprocessor:
    def __init__(self):
        self.state_encoder: Dict[str, int] = {}
        self.category_encoder: Dict[str, int] = {}
        self.product_encoder: Dict[str, int] = {}

    def normalize_text(self, text: str) -> str:
        """Trim whitespace and convert to lowercase."""
        return text.strip().lower()

    def fit(self, buyers: List[dict], suppliers: List[dict]) -> None:
        """Build label encoders from all data."""
        states = set()
        categories = set()
        products = set()

        # Collect from buyers
        for buyer in buyers:
            states.add(self.normalize_text(buyer["state"]))
            for item in buyer["search_history"]:
                products.add(self.normalize_text(item))
            for item in buyer["past_orders"]:
                products.add(self.normalize_text(item))

        # Collect from suppliers
        for supplier in suppliers:
            states.add(self.normalize_text(supplier["state"]))
            categories.add(self.normalize_text(supplier["category"]))
            for item in supplier["products_offered"]:
                products.add(self.normalize_text(item))

        # Create encoders (sorted for consistency)
        self.state_encoder = {state: idx for idx, state in enumerate(sorted(states))}
        self.category_encoder = {cat: idx for idx, cat in enumerate(sorted(categories))}
        self.product_encoder = {prod: idx for idx, prod in enumerate(sorted(products))}

    def preprocess_buyer(self, buyer: dict) -> ProcessedBuyer:
        """Clean and encode buyer data."""
        name = self.normalize_text(buyer["name"])
        state = self.normalize_text(buyer["state"])
        city = self.normalize_text(buyer["city"])

        search_history = [self.normalize_text(item) for item in buyer["search_history"]]
        past_orders = [self.normalize_text(item) for item in buyer["past_orders"]]

        return ProcessedBuyer(
            buyer_id=buyer["buyer_id"],
            name=name,
            state=state,
            state_encoded=self.state_encoder.get(state, -1),
            city=city,
            search_history=search_history,
            search_history_encoded=[self.product_encoder.get(item, -1) for item in search_history],
            past_orders=past_orders,
            past_orders_encoded=[self.product_encoder.get(item, -1) for item in past_orders],
        )

    def preprocess_supplier(self, supplier: dict) -> ProcessedSupplier:
        """Clean and encode supplier data."""
        supplier_name = self.normalize_text(supplier["supplier_name"])
        category = self.normalize_text(supplier["category"])
        state = self.normalize_text(supplier["state"])
        city = self.normalize_text(supplier["city"])

        products_offered = [self.normalize_text(item) for item in supplier["products_offered"]]

        return ProcessedSupplier(
            supplier_id=supplier["supplier_id"],
            supplier_name=supplier_name,
            category=category,
            category_encoded=self.category_encoder.get(category, -1),
            rating=supplier["rating"],
            response_time_ms=supplier["response_time_ms"],
            state=state,
            state_encoded=self.state_encoder.get(state, -1),
            city=city,
            products_offered=products_offered,
            products_offered_encoded=[self.product_encoder.get(item, -1) for item in products_offered],
        )
