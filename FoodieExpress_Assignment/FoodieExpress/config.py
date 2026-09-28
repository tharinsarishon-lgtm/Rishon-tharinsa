"""Business rules and constants for the FoodieExpress Order Management System.

Keeping every rule in one place means a change (for example, a new
delivery charge) only has to be made here and not across the whole code.
"""

APP_TITLE = "FoodieExpress Order Management System"
DATABASE_FILE = "foodieexpress.db"

# Delivery rules
DELIVERY_CHARGE_PER_KM = 50.00          # Rs. 50 per km
MAX_DELIVERY_DISTANCE_KM = 20.0         # orders cannot go beyond 20 km
FREE_DELIVERY_THRESHOLD = 5000.00       # food cost ABOVE this = free delivery
DELIVERY_OPTIONS = ("Home Delivery", "Self Pick-up")

# Discount rules (stored as fractions, not percentages)
DISCOUNT_RATES = {
    "Regular": 0.00,
    "Premium": 0.10,
    "VIP": 0.20,
}
ORDER_TYPES = tuple(DISCOUNT_RATES)

# Sensible limits used by the input validator
MAX_ITEMS_PER_ORDER = 100
MAX_PRICE_PER_ITEM = 100000.00
NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 50
