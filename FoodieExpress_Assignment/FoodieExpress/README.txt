FoodieExpress Order Management System
Unit 1: Programming - Pearson BTEC HND in Computing
=====================================================

1. REQUIREMENTS
   - Python 3.10 or newer (tested on Python 3.12) from https://www.python.org
     (tkinter and sqlite3 come with the standard Windows installer)
   - No extra packages need to be installed.

2. HOW TO RUN THE MAIN APPLICATION
   a) Open a terminal / Command Prompt inside the "FoodieExpress" folder.
   b) Type:   python main.py
   c) The FoodieExpress window opens. The database file
      "foodieexpress.db" is created automatically in this folder the
      first time the program runs.

   In Visual Studio Code: File > Open Folder > select "FoodieExpress",
   open main.py and press F5 (or click the Run button).

3. HOW TO USE THE APPLICATION
   - Enter the customer name, order type, number of items, price per
     item, delivery option and delivery distance (maximum 20 km).
   - Tick "Eligible for discount" for Premium (10%) or VIP (20%) discounts.
   - Click "Calculate Bill" (or press Enter) to see the itemised bill.
   - Click "Save Order" to store the order in the database. Saved orders
     appear in the table at the bottom of the window.
   - Click "Clear" (or press Esc) to start a new order.

4. BUSINESS RULES
   - Food cost      = number of items x price per item
   - Discount       = Premium 10%, VIP 20% of food cost (only if eligible)
   - Delivery fee   = Rs. 50 per km (maximum distance 20 km)
   - Free delivery  = when the food cost is above Rs. 5,000.00
   - Self Pick-up   = no delivery fee
   - Total payable  = food cost - discount + delivery fee
   - All money values are shown with 2 decimal places.

5. OTHER FILES
   activity1_algorithms.py            Activity 1 algorithms, dry runs, timings
   activity2_paradigms/                Activity 2 paradigm examples
   debug_demo/buggy_calculator.py      Early buggy version used in Activity 4.2
   debug_demo/fixed_calculator.py      Same code after the bugs were fixed
   tests/test_order.py                 Unit tests

   Run the unit tests with:   python -m unittest discover tests

6. PROJECT FILES
   main.py        - starts the program
   gui.py         - Tkinter window and event handlers
   models.py      - Customer, Order and Bill classes (calculations)
   validation.py  - input validation
   database.py    - SQLite database (Customer, Orders, Delivery tables)
   config.py      - business rules and constants
