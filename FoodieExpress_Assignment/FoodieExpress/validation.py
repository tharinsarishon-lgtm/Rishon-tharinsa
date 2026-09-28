"""Input validation for the FoodieExpress order form.

Every value typed into the GUI arrives as text. The validator turns that
text into the correct data type and rejects anything that is empty,
the wrong type, negative, or outside the business limits.
"""

from __future__ import annotations

import math
import re

from config import (
    DELIVERY_OPTIONS,
    MAX_DELIVERY_DISTANCE_KM,
    MAX_ITEMS_PER_ORDER,
    MAX_PRICE_PER_ITEM,
    NAME_MAX_LENGTH,
    NAME_MIN_LENGTH,
    ORDER_TYPES,
)

NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'-]*$")


class ValidationError(Exception):
    """Raised when one or more form fields contain invalid data."""

    def __init__(self, errors: dict[str, str]) -> None:
        super().__init__("; ".join(errors.values()))
        self.errors = errors


class OrderValidator:
    """Checks raw form data and returns clean, correctly typed values."""

    @staticmethod
    def validate_name(raw_name: str) -> str:
        name = " ".join(raw_name.split())      # remove extra spaces
        if not name:
            raise ValueError("Customer name is required.")
        if not NAME_MIN_LENGTH <= len(name) <= NAME_MAX_LENGTH:
            raise ValueError(
                f"Customer name must be {NAME_MIN_LENGTH}-"
                f"{NAME_MAX_LENGTH} characters long.")
        if not NAME_PATTERN.match(name):
            raise ValueError(
                "Customer name can only contain letters, spaces, "
                "full stops, hyphens and apostrophes.")
        return name

    @staticmethod
    def validate_order_type(raw_type: str) -> str:
        if raw_type not in ORDER_TYPES:
            raise ValueError("Please select Regular, Premium or VIP.")
        return raw_type

    @staticmethod
    def validate_item_count(raw_count: str) -> int:
        text = raw_count.strip()
        if not text:
            raise ValueError("Number of items is required.")
        if not text.isdigit():
            raise ValueError("Number of items must be a whole number.")
        count = int(text)
        if not 1 <= count <= MAX_ITEMS_PER_ORDER:
            raise ValueError(
                f"Number of items must be between 1 and "
                f"{MAX_ITEMS_PER_ORDER}.")
        return count

    @staticmethod
    def _to_positive_number(raw_value: str, field_label: str) -> float:
        text = raw_value.strip()
        if not text:
            raise ValueError(f"{field_label} is required.")
        try:
            value = float(text)
        except ValueError:
            raise ValueError(f"{field_label} must be a number.") from None
        # float() accepts 'nan' and 'inf', so they are blocked here.
        if math.isnan(value) or math.isinf(value):
            raise ValueError(f"{field_label} must be a real number.")
        if value <= 0:
            raise ValueError(f"{field_label} must be greater than 0.")
        return value

    @classmethod
    def validate_price(cls, raw_price: str) -> float:
        price = cls._to_positive_number(raw_price, "Price per item")
        if price > MAX_PRICE_PER_ITEM:
            raise ValueError(
                f"Price per item cannot be more than "
                f"Rs. {MAX_PRICE_PER_ITEM:,.2f}.")
        return round(price, 2)

    @classmethod
    def validate_distance(cls, raw_distance: str) -> float:
        distance = cls._to_positive_number(raw_distance, "Delivery distance")
        if distance > MAX_DELIVERY_DISTANCE_KM:
            raise ValueError(
                f"Sorry, we only deliver up to "
                f"{MAX_DELIVERY_DISTANCE_KM:.0f} km.")
        return round(distance, 2)

    @classmethod
    def validate_form(cls, form: dict[str, object]) -> dict[str, object]:
        """Validate the whole form and collect every error at once.

        Showing all problems together is friendlier than making the user
        fix them one by one.
        """
        clean: dict[str, object] = {}
        errors: dict[str, str] = {}
        checks = {
            "customer_name": cls.validate_name,
            "order_type": cls.validate_order_type,
            "item_count": cls.validate_item_count,
            "price_per_item": cls.validate_price,
        }
        for field, check in checks.items():
            try:
                clean[field] = check(str(form.get(field, "")))
            except ValueError as error:
                errors[field] = str(error)

        option = str(form.get("delivery_option", ""))
        if option not in DELIVERY_OPTIONS:
            errors["delivery_option"] = "Please choose a delivery option."
        else:
            clean["delivery_option"] = option
            if option == "Home Delivery":
                try:
                    clean["distance_km"] = cls.validate_distance(
                        str(form.get("distance_km", "")))
                except ValueError as error:
                    errors["distance_km"] = str(error)
            else:
                clean["distance_km"] = 0.0

        clean["discount_eligible"] = bool(form.get("discount_eligible"))

        if errors:
            raise ValidationError(errors)
        return clean
