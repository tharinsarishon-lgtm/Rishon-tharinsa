"""Start the FoodieExpress Order Management System."""

from database import DatabaseManager
from gui import FoodieExpressApp


def main() -> None:
    database = DatabaseManager()
    app = FoodieExpressApp(database)
    app.mainloop()


if __name__ == "__main__":
    main()
