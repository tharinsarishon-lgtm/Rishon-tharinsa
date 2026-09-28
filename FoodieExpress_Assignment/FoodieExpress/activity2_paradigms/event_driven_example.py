"""Activity 2 - EVENT-DRIVEN example: a GUI button click.

After the window is built, mainloop() waits for events. The program
does nothing until the user clicks the button (or presses Enter); the
event then calls its handler function.
"""

import tkinter as tk
from tkinter import messagebox


def on_calculate_click(event=None):
    """Event handler - runs only when the Calculate event happens."""
    try:
        items = int(items_entry.get())
        price = float(price_entry.get())
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter numbers only.")
        return
    result_label.config(text=f"Food cost: Rs. {items * price:.2f}")


window = tk.Tk()
window.title("FoodieExpress - Event Demo")

tk.Label(window, text="Number of items:").grid(
    row=0, column=0, padx=8, pady=4, sticky="w")
items_entry = tk.Entry(window)
items_entry.grid(row=0, column=1, padx=8, pady=4)

tk.Label(window, text="Price per item:").grid(
    row=1, column=0, padx=8, pady=4, sticky="w")
price_entry = tk.Entry(window)
price_entry.grid(row=1, column=1, padx=8, pady=4)

calculate_button = tk.Button(window, text="Calculate",
                             command=on_calculate_click)   # click event
calculate_button.grid(row=2, column=0, columnspan=2, pady=6)
window.bind("<Return>", on_calculate_click)                # key event

result_label = tk.Label(window, text="Food cost: Rs. 0.00")
result_label.grid(row=3, column=0, columnspan=2, pady=(0, 8))

window.mainloop()   # the event loop - waits here for user events
