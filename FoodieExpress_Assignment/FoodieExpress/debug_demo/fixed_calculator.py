"""Activity 4.2 - the same calculator after the bugs were fixed.

Compare this file with buggy_calculator.py to see every fix.
"""

DELIVERY_CHARGE_PER_KM = 50
FREE_DELIVERY_THRESHOLD = 5000
MAX_DELIVERY_DISTANCE_KM = 20
DISCOUNT_RATES = {"Regular": 0.00, "Premium": 0.10, "VIP": 0.20}


def read_distance(distance_text):
    try:
        distance_km = float(distance_text)
    except ValueError:
        raise ValueError("Delivery distance must be a number.") from None
    if not 0 < distance_km <= MAX_DELIVERY_DISTANCE_KM:
        raise ValueError("Delivery distance must be between 0 and 20 km.")
    return distance_km


def calculate_bill(item_count, price_per_item, order_type, distance_text):
    food_cost = item_count * price_per_item
    discount_rate = DISCOUNT_RATES[order_type]
    discount = food_cost * discount_rate
    distance_km = read_distance(distance_text)
    if food_cost > FREE_DELIVERY_THRESHOLD:
        delivery_fee = 0
    else:
        delivery_fee = distance_km * DELIVERY_CHARGE_PER_KM
    total = food_cost - discount + delivery_fee
    return food_cost, discount, delivery_fee, total


if __name__ == "__main__":
    tests = [
        (3, 1000, "Premium", "4"),     # Test 1: Premium, 4 km
        (5, 1000, "Regular", "10"),    # Test 2: exactly Rs. 5,000
        (2, 500, "Regular", "35"),     # Test 3: beyond 20 km
        (2, 500, "Regular", "abc"),    # Test 4: letters for distance
    ]
    for test in tests:
        try:
            print(test, "->", calculate_bill(*test))
        except ValueError as error:
            print(test, "-> rejected:", error)
