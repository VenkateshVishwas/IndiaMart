from typing import List
from models import ProcessedBuyer, ProcessedSupplier, SupplierMatch


class SupplierMatcher:
    WEIGHT_LOCATION = 0.40
    WEIGHT_SEARCH = 0.20
    WEIGHT_ORDERS = 0.20
    WEIGHT_RATING = 0.10
    WEIGHT_RESPONSE = 0.10

    MAX_RATING = 5.0
    MAX_RESPONSE_TIME = 3000

    def calculate_location_score(self, buyer: ProcessedBuyer, supplier: ProcessedSupplier) -> float:
        """Same city = 1.0, same state = 0.5, else 0.0"""
        if buyer.city == supplier.city:
            return 1.0
        elif buyer.state == supplier.state:
            return 0.5
        return 0.0

    def calculate_search_score(self, buyer: ProcessedBuyer, supplier: ProcessedSupplier) -> float:
        """Overlap between search_history and products_offered"""
        if not buyer.search_history:
            return 0.0
        buyer_searches = set(buyer.search_history)
        supplier_products = set(supplier.products_offered)
        matches = buyer_searches.intersection(supplier_products)
        return len(matches) / len(buyer.search_history)

    def calculate_orders_score(self, buyer: ProcessedBuyer, supplier: ProcessedSupplier) -> float:
        """Overlap between past_orders and products_offered"""
        if not buyer.past_orders:
            return 0.0
        buyer_orders = set(buyer.past_orders)
        supplier_products = set(supplier.products_offered)
        matches = buyer_orders.intersection(supplier_products)
        return len(matches) / len(buyer.past_orders)

    def calculate_rating_score(self, supplier: ProcessedSupplier) -> float:
        """Normalize rating to 0-1"""
        return min(supplier.rating / self.MAX_RATING, 1.0)

    def calculate_response_score(self, supplier: ProcessedSupplier) -> float:
        """Inverse normalize response time (lower is better)"""
        score = 1 - (supplier.response_time_ms / self.MAX_RESPONSE_TIME)
        return max(0.0, score)

    def calculate_scores(self, buyer: ProcessedBuyer, supplier: ProcessedSupplier) -> SupplierMatch:
        """Calculate all scores and return a SupplierMatch object"""
        location_score = self.calculate_location_score(buyer, supplier)
        search_score = self.calculate_search_score(buyer, supplier)
        orders_score = self.calculate_orders_score(buyer, supplier)
        rating_score = self.calculate_rating_score(supplier)
        response_score = self.calculate_response_score(supplier)

        total_score = (
            self.WEIGHT_LOCATION * location_score +
            self.WEIGHT_SEARCH * search_score +
            self.WEIGHT_ORDERS * orders_score +
            self.WEIGHT_RATING * rating_score +
            self.WEIGHT_RESPONSE * response_score
        )

        return SupplierMatch(
            supplier=supplier,
            score=round(total_score, 4),
            location_score=round(location_score, 4),
            search_score=round(search_score, 4),
            orders_score=round(orders_score, 4),
            rating_score=round(rating_score, 4),
            response_score=round(response_score, 4),
        )

    def get_top_suppliers(
        self,
        buyer: ProcessedBuyer,
        suppliers: List[ProcessedSupplier],
        top_n: int = 10
    ) -> List[SupplierMatch]:
        """Return top N suppliers sorted by score descending"""
        matches = [self.calculate_scores(buyer, supplier) for supplier in suppliers]
        matches.sort(key=lambda x: x.score, reverse=True)
        return matches[:top_n]
