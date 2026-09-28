"""Tkinter GUI for the FoodieExpress Order Management System.

The GUI is event-driven: nothing happens until the user clicks a button
or presses a key, and each event is handled by one small method.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from config import (
    APP_TITLE,
    DELIVERY_OPTIONS,
    FREE_DELIVERY_THRESHOLD,
    MAX_DELIVERY_DISTANCE_KM,
    ORDER_TYPES,
)
from database import DatabaseManager
from models import Bill, Customer, Order
from validation import OrderValidator, ValidationError

FIELD_LABELS = {
    "customer_name": "Customer Name",
    "order_type": "Order Type",
    "item_count": "Number of Items",
    "price_per_item": "Price per Item",
    "delivery_option": "Delivery Option",
    "distance_km": "Delivery Distance",
}


class FoodieExpressApp(tk.Tk):
    """Main window: order form, bill breakdown and order history."""

    def __init__(self, database: DatabaseManager) -> None:
        super().__init__()
        self.database = database
        self.title(APP_TITLE)
        self.geometry("1000x660")
        self.minsize(900, 600)

        self._create_variables()
        self._build_header()
        self._build_order_form()
        self._build_bill_panel()
        self._build_status_bar()
        self._build_history_table()
        self._bind_events()
        self.refresh_order_history()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ------------------------------------------------------------ layout
    def _create_variables(self) -> None:
        self.name_var = tk.StringVar()
        self.order_type_var = tk.StringVar(value=ORDER_TYPES[0])
        self.items_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.delivery_option_var = tk.StringVar(value=DELIVERY_OPTIONS[0])
        self.distance_var = tk.StringVar()
        self.discount_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready. Enter the order details.")
        self.bill_vars = {key: tk.StringVar(value="-") for key in (
            "customer_name", "order_type", "food_cost", "discount",
            "delivery_fee", "delivery_category", "total_payable")}

    def _build_header(self) -> None:
        header = tk.Frame(self, bg="#c0392b", height=56)
        header.pack(fill="x")
        tk.Label(header, text="FoodieExpress", bg="#c0392b", fg="white",
                 font=("Segoe UI", 20, "bold")).pack(side="left", padx=16,
                                                     pady=8)
        tk.Label(header, text="Order Management System", bg="#c0392b",
                 fg="white", font=("Segoe UI", 12)).pack(side="left")

    def _build_order_form(self) -> None:
        body = ttk.Frame(self, padding=10)
        body.pack(fill="x")
        self.body = body

        form = ttk.LabelFrame(body, text=" Order Details ", padding=12)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Label(form, text="Customer Name:").grid(row=0, column=0,
                                                    sticky="w", pady=4)
        self.name_entry = ttk.Entry(form, textvariable=self.name_var,
                                    width=30)
        self.name_entry.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Order Type:").grid(row=1, column=0,
                                                 sticky="w", pady=4)
        ttk.Combobox(form, textvariable=self.order_type_var,
                     values=ORDER_TYPES, state="readonly",
                     width=27).grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Number of Items:").grid(row=2, column=0,
                                                      sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.items_var,
                  width=30).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Price per Item (Rs.):").grid(row=3, column=0,
                                                           sticky="w",
                                                           pady=4)
        ttk.Entry(form, textvariable=self.price_var,
                  width=30).grid(row=3, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Delivery Option:").grid(row=4, column=0,
                                                      sticky="w", pady=4)
        options = ttk.Frame(form)
        options.grid(row=4, column=1, sticky="w")
        for option in DELIVERY_OPTIONS:
            ttk.Radiobutton(options, text=option, value=option,
                            variable=self.delivery_option_var,
                            command=self.on_delivery_option_change
                            ).pack(side="left", padx=(0, 8))

        ttk.Label(form, text="Delivery Distance (km):").grid(
            row=5, column=0, sticky="w", pady=4)
        self.distance_entry = ttk.Entry(form, textvariable=self.distance_var,
                                        width=30)
        self.distance_entry.grid(row=5, column=1, sticky="w", pady=4)
        ttk.Label(form, text=f"Max {MAX_DELIVERY_DISTANCE_KM:.0f} km",
                  foreground="grey").grid(row=5, column=2, sticky="w",
                                          padx=4)

        ttk.Checkbutton(form, text="Eligible for discount "
                        "(Premium 10% / VIP 20%)",
                        variable=self.discount_var).grid(
            row=6, column=0, columnspan=3, sticky="w", pady=6)

        buttons = ttk.Frame(form)
        buttons.grid(row=7, column=0, columnspan=3, pady=(10, 0),
                     sticky="w")
        ttk.Button(buttons, text="Calculate Bill",
                   command=self.on_calculate_click).pack(side="left",
                                                         padx=(0, 6))
        ttk.Button(buttons, text="Save Order",
                   command=self.on_save_click).pack(side="left", padx=6)
        ttk.Button(buttons, text="Clear",
                   command=self.on_clear_click).pack(side="left", padx=6)

    def _build_bill_panel(self) -> None:
        panel = ttk.LabelFrame(self.body, text=" Bill Breakdown ",
                               padding=12)
        panel.grid(row=0, column=1, sticky="nsew")
        self.body.columnconfigure(1, weight=1)

        rows = (
            ("Customer Name:", "customer_name"),
            ("Order Type:", "order_type"),
            ("Food Cost:", "food_cost"),
            ("Discount:", "discount"),
            ("Delivery Fee:", "delivery_fee"),
            ("Delivery Category:", "delivery_category"),
        )
        for row, (label, key) in enumerate(rows):
            ttk.Label(panel, text=label).grid(row=row, column=0,
                                              sticky="w", pady=3)
            ttk.Label(panel, textvariable=self.bill_vars[key],
                      wraplength=260).grid(row=row, column=1, sticky="w",
                                           pady=3, padx=8)
        ttk.Separator(panel).grid(row=6, column=0, columnspan=2,
                                  sticky="ew", pady=8)
        ttk.Label(panel, text="TOTAL PAYABLE:",
                  font=("Segoe UI", 12, "bold")).grid(row=7, column=0,
                                                      sticky="w")
        ttk.Label(panel, textvariable=self.bill_vars["total_payable"],
                  font=("Segoe UI", 12, "bold"),
                  foreground="#c0392b").grid(row=7, column=1, sticky="w",
                                             padx=8)
        ttk.Label(panel, text=f"Free delivery on food orders above "
                  f"Rs. {FREE_DELIVERY_THRESHOLD:,.2f}",
                  foreground="grey").grid(row=8, column=0, columnspan=2,
                                          sticky="w", pady=(10, 0))

    def _build_history_table(self) -> None:
        frame = ttk.LabelFrame(self, text=" Saved Orders (from database) ",
                               padding=8)
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        columns = ("order_id", "customer", "type", "items", "food_cost",
                   "discount", "delivery_fee", "total", "date")
        headings = ("Order ID", "Customer", "Type", "Items", "Food Cost",
                    "Discount", "Delivery Fee", "Total", "Date")
        widths = (70, 150, 80, 55, 100, 90, 95, 100, 150)
        self.history_table = ttk.Treeview(frame, columns=columns,
                                          show="headings", height=8)
        for column, heading, width in zip(columns, headings, widths):
            self.history_table.heading(column, text=heading)
            self.history_table.column(column, width=width, anchor="center")
        scrollbar = ttk.Scrollbar(frame, orient="vertical",
                                  command=self.history_table.yview)
        self.history_table.configure(yscrollcommand=scrollbar.set)
        self.history_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_status_bar(self) -> None:
        ttk.Label(self, textvariable=self.status_var, relief="sunken",
                  anchor="w", padding=4).pack(fill="x", side="bottom")

    def _bind_events(self) -> None:
        self.bind("<Return>", lambda event: self.on_calculate_click())
        self.bind("<Escape>", lambda event: self.on_clear_click())

    # ------------------------------------------------------------ logic
    def _read_form(self) -> dict[str, object]:
        return {
            "customer_name": self.name_var.get(),
            "order_type": self.order_type_var.get(),
            "item_count": self.items_var.get(),
            "price_per_item": self.price_var.get(),
            "delivery_option": self.delivery_option_var.get(),
            "distance_km": self.distance_var.get(),
            "discount_eligible": self.discount_var.get(),
        }

    def _build_order(self) -> Order | None:
        """Validate the form. Return an Order, or None if data is invalid."""
        try:
            data = OrderValidator.validate_form(self._read_form())
        except ValidationError as error:
            message = "\n".join(
                f"- {FIELD_LABELS.get(field, field)}: {text}"
                for field, text in error.errors.items())
            messagebox.showerror("Invalid input",
                                 "Please correct the following:\n\n"
                                 + message)
            self.status_var.set("Invalid input - nothing was calculated.")
            return None
        return Order(
            customer=Customer(name=data["customer_name"]),
            order_type=data["order_type"],
            item_count=data["item_count"],
            price_per_item=data["price_per_item"],
            delivery_option=data["delivery_option"],
            distance_km=data["distance_km"],
            discount_eligible=data["discount_eligible"],
        )

    def _show_bill(self, bill: Bill) -> None:
        self.bill_vars["customer_name"].set(bill.customer_name)
        self.bill_vars["order_type"].set(bill.order_type)
        self.bill_vars["food_cost"].set(f"Rs. {bill.food_cost:,.2f}")
        self.bill_vars["discount"].set(
            f"- Rs. {bill.discount_amount:,.2f} "
            f"({bill.discount_rate * 100:.0f}%)")
        fee_text = f"Rs. {bill.delivery_fee:,.2f}"
        if bill.free_delivery:
            fee_text += "  (FREE DELIVERY)"
        self.bill_vars["delivery_fee"].set(fee_text)
        self.bill_vars["delivery_category"].set(bill.delivery_category)
        self.bill_vars["total_payable"].set(f"Rs. {bill.total_payable:,.2f}")

    # ------------------------------------------------------------ events
    def on_delivery_option_change(self) -> None:
        """Disable the distance box when the customer will pick up."""
        if self.delivery_option_var.get() == "Self Pick-up":
            self.distance_var.set("")
            self.distance_entry.state(["disabled"])
        else:
            self.distance_entry.state(["!disabled"])

    def on_calculate_click(self) -> None:
        order = self._build_order()
        if order is None:
            return
        self._show_bill(order.generate_bill())
        self.status_var.set("Bill calculated. Click 'Save Order' to store it.")

    def on_save_click(self) -> None:
        order = self._build_order()
        if order is None:
            return
        bill = order.generate_bill()
        self._show_bill(bill)
        try:
            order_id = self.database.save_order(order, bill)
        except Exception as error:  # keep the app running on DB errors
            messagebox.showerror("Database error",
                                 f"The order could not be saved.\n{error}")
            return
        spent = self.database.get_customer_total_spending(
            order.customer.customer_id)
        self.refresh_order_history()
        self.status_var.set(
            f"Order #{order_id} saved for {bill.customer_name}. "
            f"Total spent by this customer so far: Rs. {spent:,.2f}")
        messagebox.showinfo("Order saved",
                            f"Order #{order_id} was saved successfully.")

    def on_clear_click(self) -> None:
        for variable in (self.name_var, self.items_var, self.price_var,
                         self.distance_var):
            variable.set("")
        self.order_type_var.set(ORDER_TYPES[0])
        self.delivery_option_var.set(DELIVERY_OPTIONS[0])
        self.on_delivery_option_change()
        self.discount_var.set(False)
        for variable in self.bill_vars.values():
            variable.set("-")
        self.status_var.set("Form cleared.")
        self.name_entry.focus_set()

    def refresh_order_history(self) -> None:
        self.history_table.delete(*self.history_table.get_children())
        for row in self.database.fetch_order_history():
            self.history_table.insert("", "end", values=(
                row["order_id"], row["customer_name"], row["order_type"],
                row["item_count"], f"{row['food_cost']:,.2f}",
                f"{row['discount_amount']:,.2f}",
                f"{row['delivery_fee']:,.2f}",
                f"{row['total_payable']:,.2f}", row["order_date"]))

    def on_close(self) -> None:
        self.database.close()
        self.destroy()
