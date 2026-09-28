"""Unit tests for the FoodieExpress calculations, validation and database.

Run from the FoodieExpress folder with:  python -m unittest discover tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager  # noqa: E402
from models import Customer, Order  # noqa: E402
from validation import OrderValidator, ValidationError  # noqa: E402


def make_order(order_type="Regular", items=2, price=1000.0,
               option="Home Delivery", distance=4.0, eligible=True):
    return Order(Customer("Test User"), order_type, items, price, option,
                 distance, eligible)


class TestOrderCalculations(unittest.TestCase):

    def test_regular_order_has_no_discount(self):
        bill = make_order("Regular").generate_bill()
        self.assertEqual(bill.discount_amount, 0.00)
        self.assertEqual(bill.total_payable, 2200.00)   # 2000 + 4km*50

    def test_premium_discount_is_10_percent(self):
        bill = make_order("Premium", items=3).generate_bill()
        self.assertEqual(bill.discount_amount, 300.00)
        self.assertEqual(bill.total_payable, 2900.00)   # 3000-300+200

    def test_vip_discount_is_20_percent(self):
        bill = make_order("VIP", items=2, price=1500).generate_bill()
        self.assertEqual(bill.discount_amount, 600.00)

    def test_no_discount_when_not_eligible(self):
        bill = make_order("VIP", eligible=False).generate_bill()
        self.assertEqual(bill.discount_amount, 0.00)

    def test_exactly_5000_still_pays_delivery(self):
        bill = make_order(items=5, price=1000, distance=10).generate_bill()
        self.assertEqual(bill.delivery_fee, 500.00)
        self.assertFalse(bill.free_delivery)

    def test_above_5000_gets_free_delivery(self):
        bill = make_order(items=5, price=1000.01, distance=10).generate_bill()
        self.assertEqual(bill.delivery_fee, 0.00)
        self.assertTrue(bill.free_delivery)

    def test_pickup_has_no_delivery_fee(self):
        bill = make_order(option="Self Pick-up", distance=0).generate_bill()
        self.assertEqual(bill.delivery_fee, 0.00)


class TestValidation(unittest.TestCase):

    def valid_form(self, **changes):
        form = {"customer_name": "Nimal Perera", "order_type": "VIP",
                "item_count": "3", "price_per_item": "1200",
                "delivery_option": "Home Delivery", "distance_km": "8",
                "discount_eligible": True}
        form.update(changes)
        return form

    def test_valid_form_passes(self):
        clean = OrderValidator.validate_form(self.valid_form())
        self.assertEqual(clean["item_count"], 3)
        self.assertEqual(clean["distance_km"], 8.0)

    def test_rejects_bad_values(self):
        bad_inputs = [
            {"customer_name": ""},
            {"customer_name": "12345"},
            {"item_count": "0"},
            {"item_count": "2.5"},
            {"item_count": "-3"},
            {"price_per_item": "abc"},
            {"price_per_item": "-100"},
            {"price_per_item": "nan"},
            {"distance_km": "21"},
            {"distance_km": "0"},
            {"distance_km": ""},
        ]
        for change in bad_inputs:
            with self.subTest(change=change):
                with self.assertRaises(ValidationError):
                    OrderValidator.validate_form(self.valid_form(**change))

    def test_20_km_is_allowed(self):
        clean = OrderValidator.validate_form(self.valid_form(distance_km="20"))
        self.assertEqual(clean["distance_km"], 20.0)

    def test_pickup_ignores_distance(self):
        clean = OrderValidator.validate_form(self.valid_form(
            delivery_option="Self Pick-up", distance_km=""))
        self.assertEqual(clean["distance_km"], 0.0)


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.database = DatabaseManager(":memory:")

    def tearDown(self):
        self.database.close()

    def test_order_is_saved_and_retrieved(self):
        order = make_order("Premium", items=3)
        order_id = self.database.save_order(order, order.generate_bill())
        rows = self.database.fetch_order_history()
        self.assertEqual(rows[0]["order_id"], order_id)
        self.assertEqual(rows[0]["total_payable"], 2900.00)

    def test_customer_spending_adds_up(self):
        for _ in range(2):
            order = make_order("Regular")
            self.database.save_order(order, order.generate_bill())
        spent = self.database.get_customer_total_spending(
            order.customer.customer_id)
        self.assertEqual(spent, 4400.00)

    def test_sql_injection_text_is_stored_as_plain_text(self):
        order = Order(Customer("Robert'); DROP TABLE Orders;--"), "Regular",
                      1, 100.0, "Self Pick-up", 0, False)
        self.database.save_order(order, order.generate_bill())
        self.assertEqual(len(self.database.fetch_order_history()), 1)


if __name__ == "__main__":
    unittest.main()
