"""Activity 2 - OBJECT-ORIENTED example: an Order class hierarchy.

Shows encapsulation (data + methods inside a class, protected
attributes), inheritance (Premium/VIP orders reuse Order) and
polymorphism (each subclass gives its own discount rate).
"""

from abc import ABC, abstractmethod


class Order(ABC):
    DELIVERY_CHARGE_PER_KM = 50.00
    FREE_DELIVERY_THRESHOLD = 5000.00

    def __init__(self, customer_name, item_count, price_per_item,
                 distance_km):
        self._customer_name = customer_name
        self._item_count = item_count
        self._price_per_item = price_per_item
        self._distance_km = distance_km

    @property
    def customer_name(self):
        return self._customer_name

    @abstractmethod
    def get_discount_rate(self):
        """Each type of order must say what discount it gets."""

    def food_cost(self):
        return self._item_count * self._price_per_item

    def discount(self):
        return self.food_cost() * self.get_discount_rate()

    def delivery_fee(self):
        if self.food_cost() > self.FREE_DELIVERY_THRESHOLD:
            return 0.00
        return self._distance_km * self.DELIVERY_CHARGE_PER_KM

    def total(self):
        return self.food_cost() - self.discount() + self.delivery_fee()

    def __str__(self):
        return (f"{type(self).__name__} for {self.customer_name}: "
                f"Rs. {self.total():.2f}")


class RegularOrder(Order):
    def get_discount_rate(self):
        return 0.00


class PremiumOrder(Order):
    def get_discount_rate(self):
        return 0.10


class VIPOrder(Order):
    def get_discount_rate(self):
        return 0.20


if __name__ == "__main__":
    orders = [
        RegularOrder("Nimal Silva", 2, 750.00, 4),
        PremiumOrder("Kamal Perera", 4, 850.00, 6.5),
        VIPOrder("Sachini Fernando", 6, 1200.00, 12),
    ]
    for order in orders:        # same method call, different behaviour
        print(order)
