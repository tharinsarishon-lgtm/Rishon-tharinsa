"""Activity 1 - the two algorithms, their dry runs and a timing test.

Algorithm 1: order growth sequence, O(n) = O(n-1) + O(n-2)
Algorithm 2: bulk order cost with decreasing discount factors
             total = base x 0.9 x 0.8 x 0.7 ...
"""

from __future__ import annotations

import time


def generate_order_growth(first: int, second: int, days: int,
                          show_steps: bool = False) -> list[int]:
    """Return the order counts for the given number of days (iterative).

    Time complexity: O(n) - the loop runs once per extra day.
    Space complexity: O(n) - every value is kept in the list.
    """
    if days < 1:
        raise ValueError("Number of days must be at least 1.")
    if days == 1:
        return [first]

    sequence = [first, second]
    for day in range(3, days + 1):
        next_value = sequence[-1] + sequence[-2]
        sequence.append(next_value)
        if show_steps:
            print(f"Iteration {day - 2}: Day {day} = {sequence[-3]} + "
                  f"{sequence[-2]} = {next_value}  ->  {sequence}")
    return sequence


def order_growth_recursive(day: int, first: int = 5, second: int = 8) -> int:
    """Naive recursive version, used only to compare efficiency.

    Time complexity: O(2^n) - every call makes two more calls.
    """
    if day == 1:
        return first
    if day == 2:
        return second
    return (order_growth_recursive(day - 1, first, second)
            + order_growth_recursive(day - 2, first, second))


def calculate_bulk_cost(base_price: float, item_count: int,
                        start_factor: float = 0.9, step: float = 0.1,
                        show_steps: bool = False) -> float:
    """Apply a smaller discount factor for every additional item.

    item 1 -> base price, item 2 -> x0.9, item 3 -> x0.8, and so on.
    Time complexity: O(n)   Space complexity: O(1)
    """
    if base_price <= 0:
        raise ValueError("Base price must be greater than 0.")
    if item_count < 1:
        raise ValueError("Item count must be at least 1.")
    # The factor must stay above 0, otherwise the total becomes 0.
    last_factor = start_factor - (item_count - 2) * step
    if item_count > 1 and last_factor <= 1e-9:
        raise ValueError("Too many items - the discount factor would "
                         "reach 0.")

    total = base_price
    factor = start_factor
    for item in range(2, item_count + 1):
        total = total * factor
        if show_steps:
            print(f"Iteration {item - 1}: item {item}, factor "
                  f"{factor:.1f} -> total = {total:.2f}")
        factor = round(factor - step, 10)   # avoids 0.7000000000000001
    return round(total, 2)


def time_function(function, *args, repeats: int = 5) -> float:
    """Return the average run time of a function in milliseconds."""
    start = time.perf_counter()
    for _ in range(repeats):
        function(*args)
    return (time.perf_counter() - start) / repeats * 1000


def run_benchmarks() -> None:
    print("\n--- Efficiency test: order growth sequence ---")
    print(f"{'n':>4} | {'Iterative O(n) ms':>18} | "
          f"{'Recursive O(2^n) ms':>20}")
    for n in (10, 15, 20, 25, 30):
        iterative_ms = time_function(generate_order_growth, 5, 8, n)
        recursive_ms = time_function(order_growth_recursive, n, repeats=1)
        print(f"{n:>4} | {iterative_ms:>18.4f} | {recursive_ms:>20.4f}")

    print("\n--- Efficiency test: bulk discount cost O(n) ---")
    print(f"{'items':>8} | {'time ms':>10}")
    for n in (1_000, 10_000, 100_000, 1_000_000):
        # A tiny step lets us test very large n without the factor hitting 0.
        step = 0.9 / n
        elapsed = time_function(calculate_bulk_cost, 100, n, 0.9, step)
        print(f"{n:>8} | {elapsed:>10.3f}")


def main() -> None:
    print("=== Dry run 1: order growth sequence (5, 8, 8 days) ===")
    result = generate_order_growth(5, 8, 8, show_steps=True)
    print(f"Final sequence: {result}")
    print(f"Orders on day 8: {result[-1]}")

    print("\n=== Dry run 2: bulk order cost (base Rs. 100, 5 items) ===")
    total = calculate_bulk_cost(100, 5, show_steps=True)
    print(f"Final total cost: Rs. {total:.2f}")

    run_benchmarks()


if __name__ == "__main__":
    main()
