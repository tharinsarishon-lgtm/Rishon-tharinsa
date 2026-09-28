"""Activity 4.2 - early version of the calculator, kept for the
debugging demonstration. It contains the errors that were found with
breakpoints and step execution. The fixed logic is in models.py and
validation.py.
"""

DELIVERY_CHARGE_PER_KM = 50
FREE_DELIVERY_THRESHOLD = 5000
DISCOUNT_RATES = {"Regular": 0, "Premium": 10, "VIP": 20}


def calculate_bill(item_count, price_per_item, order_type, distance_text):
    food_cost = item_count * price_per_item
    discount_rate = DISCOUNT_RATES[order_type]
    discount = food_cost * discount_rate
    distance_km = float(distance_text)
    if food_cost >= FREE_DELIVERY_THRESHOLD:
        delivery_fee = 0
    else:
        delivery_fee = distance_km * DELIVERY_CHARGE_PER_KM
    total = food_cost - discount + delivery_fee
    return food_cost, discount, delivery_fee, total


if __name__ == "__main__":
    # Test 1: Premium order, 3 items x Rs. 1,000, 4 km
    print(calculate_bill(3, 1000, "Premium", "4"))
    # Test 2: exactly Rs. 5,000 of food, 10 km
    print(calculate_bill(5, 1000, "Regular", "10"))
    # Test 3: distance outside the 20 km limit
    print(calculate_bill(2, 500, "Regular", "35"))
    # Test 4: letters typed into the distance box
    print(calculate_bill(2, 500, "Regular", "abc"))
