import csv
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from src.config import DATA_DIR

class DataLoader:
    """
    Data Loader module providing indexed lookup for Olist E-commerce CSV datasets.
    Implements singleton caching for high-performance memory lookups.
    """

    _instance = None

    def __new__(cls, data_dir: Path = DATA_DIR):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, data_dir: Path = DATA_DIR):
        if self._initialized:
            return
        self.data_dir = data_dir
        
        # Indexed storage
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.order_items: Dict[str, List[Dict[str, Any]]] = {}
        self.order_payments: Dict[str, List[Dict[str, Any]]] = {}
        self.order_reviews: Dict[str, List[Dict[str, Any]]] = {}
        self.customers: Dict[str, Dict[str, Any]] = {}
        self.products: Dict[str, Dict[str, Any]] = {}
        self.sellers: Dict[str, Dict[str, Any]] = {}
        
        self._load_all_datasets()
        self._initialized = True

    def _load_all_datasets(self):
        """Loads and indexes CSV files into memory."""
        # 1. Orders
        orders_file = self.data_dir / "olist_orders_dataset.csv"
        if orders_file.exists():
            with open(orders_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.orders[row["order_id"]] = row

        # 2. Order Items
        items_file = self.data_dir / "olist_order_items_dataset.csv"
        if items_file.exists():
            with open(items_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    oid = row["order_id"]
                    if oid not in self.order_items:
                        self.order_items[oid] = []
                    self.order_items[oid].append(row)

        # 3. Order Payments
        payments_file = self.data_dir / "olist_order_payments_dataset.csv"
        if payments_file.exists():
            with open(payments_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    oid = row["order_id"]
                    if oid not in self.order_payments:
                        self.order_payments[oid] = []
                    self.order_payments[oid].append(row)

        # 4. Order Reviews
        reviews_file = self.data_dir / "olist_order_reviews_dataset.csv"
        if reviews_file.exists():
            with open(reviews_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    oid = row["order_id"]
                    if oid not in self.order_reviews:
                        self.order_reviews[oid] = []
                    self.order_reviews[oid].append(row)

        # 5. Customers
        customers_file = self.data_dir / "olist_customers_dataset.csv"
        if customers_file.exists():
            with open(customers_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.customers[row["customer_id"]] = row

        # 6. Products
        products_file = self.data_dir / "olist_products_dataset.csv"
        if products_file.exists():
            with open(products_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.products[row["product_id"]] = row

        # 7. Sellers
        sellers_file = self.data_dir / "olist_sellers_dataset.csv"
        if sellers_file.exists():
            with open(sellers_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.sellers[row["seller_id"]] = row

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve order record by order_id."""
        return self.orders.get(order_id)

    def get_items(self, order_id: str) -> List[Dict[str, Any]]:
        """Retrieve order items for a given order_id."""
        return self.order_items.get(order_id, [])

    def get_payments(self, order_id: str) -> List[Dict[str, Any]]:
        """Retrieve order payment rows for a given order_id."""
        return self.order_payments.get(order_id, [])

    def get_reviews(self, order_id: str) -> List[Dict[str, Any]]:
        """Retrieve order review rows for a given order_id."""
        return self.order_reviews.get(order_id, [])

    def get_seller(self, seller_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve seller information by seller_id."""
        return self.sellers.get(seller_id)

    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve product information by product_id."""
        return self.products.get(product_id)

    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve customer information by customer_id."""
        return self.customers.get(customer_id)

    def verify_evidence_exists(self, evidence_id: str) -> bool:
        """
        Validates whether an evidence_id exists in the database.
        Format types:
          - order:<order_id>
          - item:<order_id>:<order_item_id>
          - payment:<order_id>:<payment_sequential>
          - seller:<seller_id>
          - policy:<root_cause_code>
        """
        parts = evidence_id.split(":")
        if not parts:
            return False
        
        prefix = parts[0]
        if prefix == "order" and len(parts) == 2:
            return parts[1] in self.orders
        elif prefix == "item" and len(parts) == 3:
            oid, item_seq = parts[1], parts[2]
            items = self.get_items(oid)
            return any(str(item.get("order_item_id")) == str(item_seq) for item in items)
        elif prefix == "payment" and len(parts) == 3:
            oid, pmt_seq = parts[1], parts[2]
            pmts = self.get_payments(oid)
            return any(str(pmt.get("payment_sequential")) == str(pmt_seq) for pmt in pmts)
        elif prefix == "seller" and len(parts) == 2:
            return parts[1] in self.sellers
        elif prefix == "policy" and len(parts) == 2:
            valid_codes = {
                "SELLER_HANDOFF_AFTER_LIMIT",
                "CARRIER_DELIVERED_AFTER_ESTIMATE",
                "ORDER_CANCELED_AFTER_PAYMENT",
                "ORDER_UNAVAILABLE_AFTER_PAYMENT",
                "MULTIPLE_PAYMENTS_RECONCILED",
                "DELIVERY_WITHIN_ESTIMATE"
            }
            return parts[1] in valid_codes
        return False
