import unittest
import pandas as pd

from src.quality import split_valid_and_rejected
from src.transform import transform_orders
from src.analytics import build_kpis

class TestDataPulsePipeline(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame([
            {"order_id": "A1", "order_date": "2026-01-01", "customer_id": "C1", "region": "North",
             "product": "Keyboard", "category": "Accessories", "quantity": 2, "unit_price": 500, "discount": 0.1},
            {"order_id": "A2", "order_date": "2026-01-02", "customer_id": "C2", "region": "South",
             "product": "Mouse", "category": "Accessories", "quantity": 1, "unit_price": 300, "discount": 0.0},
            {"order_id": "A3", "order_date": "bad-date", "customer_id": "C3", "region": "West",
             "product": "Monitor", "category": "Displays", "quantity": 1, "unit_price": 9000, "discount": 0.0},
        ])

    def test_validation_splits_invalid_rows(self):
        valid, rejected, report = split_valid_and_rejected(self.df)
        self.assertEqual(len(valid), 2)
        self.assertEqual(len(rejected), 1)
        self.assertIn("invalid_order_date", rejected.iloc[0]["rejection_reason"])
        self.assertGreater(len(report), 0)

    def test_revenue_calculation(self):
        valid, _, _ = split_valid_and_rejected(self.df)
        transformed = transform_orders(valid)
        self.assertAlmostEqual(transformed.loc[0, "net_revenue"], 900.0)
        self.assertAlmostEqual(transformed.loc[1, "net_revenue"], 300.0)

    def test_kpis(self):
        valid, _, _ = split_valid_and_rejected(self.df)
        transformed = transform_orders(valid)
        kpis = build_kpis(transformed)
        self.assertEqual(kpis["orders"], 2)
        self.assertEqual(kpis["customers"], 2)
        self.assertEqual(kpis["units_sold"], 3)

if __name__ == "__main__":
    unittest.main()
