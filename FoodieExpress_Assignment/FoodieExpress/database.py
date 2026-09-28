"""SQLite database layer for FoodieExpress.

Three related tables are used:
    Customer 1 --- * Orders 1 --- 1 Delivery
All queries use ? placeholders (parameterised queries) so that text typed
by a user can never be run as SQL (protection against SQL injection).
"""

from __future__ import annotations

import os
import sqlite3

from config import DATABASE_FILE, DELIVERY_CHARGE_PER_KM
from models import Bill, Order

# Keep the .db file next to this script, whatever folder the app is run from.
DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), DATABASE_FILE)

CREATE_CUSTOMER_TABLE = """
CREATE TABLE IF NOT EXISTS Customer (
    customer_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name   TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    created_at      TEXT    NOT NULL
);
"""

CREATE_ORDERS_TABLE = """
CREATE TABLE IF NOT EXISTS Orders (
    order_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id        INTEGER NOT NULL,
    order_type         TEXT    NOT NULL
                       CHECK (order_type IN ('Regular', 'Premium', 'VIP')),
    item_count         INTEGER NOT NULL CHECK (item_count > 0),
    price_per_item     REAL    NOT NULL CHECK (price_per_item > 0),
    food_cost          REAL    NOT NULL,
    discount_eligible  INTEGER NOT NULL CHECK (discount_eligible IN (0, 1)),
    discount_rate      REAL    NOT NULL,
    discount_amount    REAL    NOT NULL,
    total_payable      REAL    NOT NULL,
    order_date         TEXT    NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer (customer_id)
);
"""

CREATE_DELIVERY_TABLE = """
CREATE TABLE IF NOT EXISTS Delivery (
    delivery_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id           INTEGER NOT NULL UNIQUE,
    delivery_option    TEXT    NOT NULL,
    distance_km        REAL    NOT NULL
                       CHECK (distance_km >= 0 AND distance_km <= 20),
    charge_per_km      REAL    NOT NULL,
    delivery_fee       REAL    NOT NULL,
    free_delivery      INTEGER NOT NULL CHECK (free_delivery IN (0, 1)),
    delivery_category  TEXT    NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders (order_id) ON DELETE CASCADE
);
"""


class DatabaseManager:
    """Opens the database, creates the tables and runs every query."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        # SQLite ignores foreign keys unless this is switched on.
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.create_tables()

    def create_tables(self) -> None:
        with self.connection:
            self.connection.execute(CREATE_CUSTOMER_TABLE)
            self.connection.execute(CREATE_ORDERS_TABLE)
            self.connection.execute(CREATE_DELIVERY_TABLE)

    def get_or_create_customer(self, name: str, created_at: str) -> int:
        """Return the customer's ID, adding the customer if they are new."""
        row = self.connection.execute(
            "SELECT customer_id FROM Customer WHERE customer_name = ?;",
            (name,),
        ).fetchone()
        if row:
            return row["customer_id"]
        cursor = self.connection.execute(
            "INSERT INTO Customer (customer_name, created_at) VALUES (?, ?);",
            (name, created_at),
        )
        return cursor.lastrowid

    def save_order(self, order: Order, bill: Bill) -> int:
        """Save the customer, order and delivery in ONE transaction.

        If any insert fails, everything is rolled back, so the database
        never holds an order without its delivery record.
        """
        with self.connection:
            customer_id = self.get_or_create_customer(
                order.customer.name, order.order_date)
            order.customer.customer_id = customer_id
            cursor = self.connection.execute(
                """INSERT INTO Orders (customer_id, order_type, item_count,
                       price_per_item, food_cost, discount_eligible,
                       discount_rate, discount_amount, total_payable,
                       order_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                (customer_id, order.order_type, order.item_count,
                 order.price_per_item, bill.food_cost,
                 int(order.discount_eligible), bill.discount_rate,
                 bill.discount_amount, bill.total_payable, order.order_date),
            )
            order_id = cursor.lastrowid
            self.connection.execute(
                """INSERT INTO Delivery (order_id, delivery_option,
                       distance_km, charge_per_km, delivery_fee,
                       free_delivery, delivery_category)
                   VALUES (?, ?, ?, ?, ?, ?, ?);""",
                (order_id, order.delivery_option, order.distance_km,
                 DELIVERY_CHARGE_PER_KM, bill.delivery_fee,
                 int(bill.free_delivery), bill.delivery_category),
            )
        return order_id

    def fetch_order_history(self) -> list[sqlite3.Row]:
        """Join the three tables to show every saved order, newest first."""
        return self.connection.execute(
            """SELECT o.order_id, c.customer_name, o.order_type,
                      o.item_count, o.food_cost, o.discount_amount,
                      d.delivery_fee, o.total_payable, o.order_date
               FROM Orders AS o
               JOIN Customer AS c ON c.customer_id = o.customer_id
               JOIN Delivery AS d ON d.order_id = o.order_id
               ORDER BY o.order_id DESC;"""
        ).fetchall()

    def get_customer_total_spending(self, customer_id: int) -> float:
        """Total amount a customer has spent across all saved orders."""
        row = self.connection.execute(
            """SELECT COALESCE(SUM(total_payable), 0) AS total
               FROM Orders WHERE customer_id = ?;""",
            (customer_id,),
        ).fetchone()
        return round(row["total"], 2)

    def close(self) -> None:
        self.connection.close()
