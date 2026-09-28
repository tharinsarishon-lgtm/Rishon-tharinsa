"""Domain classes for FoodieExpress: Customer, Order and Bill."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from config import (
    DELIVERY_CHARGE_PER_KM,
    DISCOUNT_RATES,
    FREE_DELIVERY_THRESHOLD,
)


@dataclass
class Customer:
    """A FoodieExpress customer."""

    name: str
    customer_id: int | None = None


@dataclass
class Bill:
    """Itemised breakdown of an order. All money values are in rupees."""

    customer_name: str
    order_type: str
    food_cost: float
    discount_rate: float
    discount_amount: float
    delivery_fee: float
    free_delivery: bool
    delivery_category: str
    total_payable: float

    def as_text(self) -> str:
        """Return the bill as a formatted multi-line string (2 decimals)."""
        lines = [
            f"Customer Name     : {self.customer_name}",
            f"Order Type        : {self.order_type}",
            f"Food Cost         : Rs. {self.food_cost:,.2f}",
            f"Discount ({self.discount_rate * 100:.0f}%)    : "
            f"- Rs. {self.discount_amount:,.2f}",
            f"Delivery Fee      : Rs. {self.delivery_fee:,.2f}"
            + ("  (FREE DELIVERY)" if self.free_delivery else ""),
            f"Delivery Category : {self.delivery_category}",
            f"TOTAL PAYABLE     : Rs. {self.total_payable:,.2f}",
        ]
        return "\n".join(lines)


class Order:
    """One customer order and the rules used to price it."""

    def __init__(
        self,
        customer: Customer,
        order_type: str,
        item_count: int,
        price_per_item: float,
        delivery_option: str,
        distance_km: float,
        discount_eligible: bool,
    ) -> None:
        self.customer = customer
        self.order_type = order_type
        self.item_count = item_count
        self.price_per_item = price_per_item
        self.delivery_option = delivery_option
        # A pick-up order travels no distance, so it is stored as 0 km.
        self.distance_km = distance_km if self.is_home_delivery() else 0.0
        self.discount_eligible = discount_eligible
        self.order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def is_home_delivery(self) -> bool:
        """True when the food has to be delivered to the customer."""
        return self.delivery_option == "Home Delivery"

    def calculate_food_cost(self) -> float:
        """Food cost = number of items x price per item."""
        return round(self.item_count * self.price_per_item, 2)

    def get_discount_rate(self) -> float:
        """Return 0.10 for Premium, 0.20 for VIP, otherwise 0.00.

        The customer must also be marked as eligible for a discount.
        """
        if not self.discount_eligible:
            return 0.00
        return DISCOUNT_RATES.get(self.order_type, 0.00)

    def calculate_discount(self) -> float:
        """Discount is applied to the food cost only, not to delivery."""
        return round(self.calculate_food_cost() * self.get_discount_rate(), 2)

    def qualifies_for_free_delivery(self) -> bool:
        """Food cost strictly ABOVE Rs. 5,000 gets free delivery."""
        return self.calculate_food_cost() > FREE_DELIVERY_THRESHOLD

    def calculate_delivery_fee(self) -> float:
        """Rs. 50 per km, unless it is a pick-up or free delivery applies."""
        if not self.is_home_delivery() or self.qualifies_for_free_delivery():
            return 0.00
        return round(self.distance_km * DELIVERY_CHARGE_PER_KM, 2)

    def get_delivery_category(self) -> str:
        """Group the delivery distance into a readable category."""
        if not self.is_home_delivery():
            return "Self Pick-up (no delivery needed)"
        if self.distance_km <= 5:
            category = "Short Distance (0 - 5 km)"
        elif self.distance_km <= 10:
            category = "Medium Distance (5 - 10 km)"
        else:
            category = "Long Distance (10 - 20 km)"
        return f"{category} - Valid, within 20 km limit"

    def calculate_total(self) -> float:
        """Total = food cost - discount + delivery fee."""
        total = (self.calculate_food_cost()
                 - self.calculate_discount()
                 + self.calculate_delivery_fee())
        return round(total, 2)

    def generate_bill(self) -> Bill:
        """Build the itemised bill shown in the GUI and saved to the DB."""
        return Bill(
            customer_name=self.customer.name,
            order_type=self.order_type,
            food_cost=self.calculate_food_cost(),
            discount_rate=self.get_discount_rate(),
            discount_amount=self.calculate_discount(),
            delivery_fee=self.calculate_delivery_fee(),
            free_delivery=(self.is_home_delivery()
                           and self.qualifies_for_free_delivery()),
            delivery_category=self.get_delivery_category(),
            total_payable=self.calculate_total(),
        )
