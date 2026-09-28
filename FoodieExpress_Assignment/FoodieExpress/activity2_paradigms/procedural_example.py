"""Activity 2 - PROCEDURAL example: order cost calculation.

The program is a sequence of functions called one after another from
main(). Data (plain variables) is passed into functions and results are
returned. There are no classes or objects.
"""

DELIVERY_CHARGE_PER_KM = 50.00
FREE_DELIVERY_THRESHOLD = 5000.00
DISCOUNT_RATES = {"Regular": 0.00, "Premium": 0.10, "VIP": 0.20}


def calculate_food_cost(item_count, price_per_item):
    return item_count * price_per_item


def calculate_discount(food_cost, order_type):
    return food_cost * DISCOUNT_RATES[order_type]


def calculate_delivery_fee(food_cost, distance_km):
    if food_cost > FREE_DELIVERY_THRESHOLD:
        return 0.00
    return distance_km * DELIVERY_CHARGE_PER_KM


def print_bill(name, food_cost, discount, delivery_fee):
    total = food_cost - discount + delivery_fee
    print(f"Customer     : {name}")
    print(f"Food cost    : Rs. {food_cost:.2f}")
    print(f"Discount     : Rs. {discount:.2f}")
    print(f"Delivery fee : Rs. {delivery_fee:.2f}")
    print(f"Total        : Rs. {total:.2f}")


def main():
    name = "Kamal Perera"
    food_cost = calculate_food_cost(4, 850.00)
    discount = calculate_discount(food_cost, "Premium")
    delivery_fee = calculate_delivery_fee(food_cost, 6.5)
    print_bill(name, food_cost, discount, delivery_fee)


main()
