"""
Generate synthetic e-commerce data with realistic distributions.
Produces five CSV files:
  - customers.csv
  - products.csv
  - orders.csv
  - order_details.csv
  - payments.csv

Usage:
  python synthetic_data_generator.py
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

random.seed(42)

OUTPUT_DIR = Path("data_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Basic vocab to keep names realistic without external deps
FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Elijah", "Sophia", "Lucas",
    "Isabella", "Mason", "Mia", "Ethan", "Charlotte", "Logan", "Amelia", "James",
    "Harper", "Benjamin", "Evelyn", "Henry"
]
LAST_NAMES = [
    "Smith", "Johnson", "Brown", "Taylor", "Anderson", "Thomas", "Jackson",
    "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
    "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall"
]

PRODUCT_CATEGORIES = {
    "Electronics": [
        ("Wireless Earbuds", 59, 199),
        ("Smartphone Case", 9, 39),
        ("USB-C Charger", 12, 45),
        ("Laptop Sleeve", 18, 69),
        ("Smartwatch", 99, 349),
    ],
    "Home": [
        ("Ceramic Mug", 6, 20),
        ("Throw Pillow", 14, 55),
        ("Desk Lamp", 22, 110),
        ("Bath Towel Set", 25, 90),
        ("Knife Set", 35, 160),
    ],
    "Beauty": [
        ("Facial Cleanser", 10, 35),
        ("Sunscreen SPF 50", 12, 42),
        ("Shampoo", 8, 28),
        ("Serum", 22, 90),
        ("Moisturizer", 15, 60),
    ],
    "Sports": [
        ("Yoga Mat", 18, 60),
        ("Running Shoes", 55, 180),
        ("Water Bottle", 12, 40),
        ("Fitness Tracker", 59, 220),
        ("Bike Helmet", 35, 140),
    ],
}

PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "gift_card", "apple_pay"]
STATES = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "WA"]


def random_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_email(name: str) -> str:
    base = name.lower().replace(" ", ".")
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "example.com"])
    suffix = "" if random.random() < 0.7 else str(random.randint(1, 99))
    return f"{base}{suffix}@{domain}"


def random_phone() -> str:
    return f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"


def generate_customers(count: int) -> List[Dict]:
    customers = []
    for cid in range(1, count + 1):
        name = random_name()
        customers.append(
            {
                "customer_id": cid,
                "name": name,
                "email": random_email(name),
                "phone": random_phone(),
                "state": random.choice(STATES),
                "signup_date": (datetime.now() - timedelta(days=random.randint(30, 900))).date(),
            }
        )
    return customers


def generate_products() -> List[Dict]:
    products = []
    pid = 1
    for category, items in PRODUCT_CATEGORIES.items():
        for name, min_price, max_price in items:
            price = round(random.normalvariate((min_price + max_price) / 2, (max_price - min_price) / 6), 2)
            price = max(min_price, min(max_price, price))
            products.append(
                {
                    "product_id": pid,
                    "name": name,
                    "category": category,
                    "unit_price": price,
                    "stock": random.randint(50, 500),
                }
            )
            pid += 1
    return products


def random_order_date(signup_date: datetime.date) -> datetime:
    days_since_signup = (datetime.now().date() - signup_date).days
    if days_since_signup <= 0:
        days_since_signup = 1
    delta_days = int(abs(random.gauss(days_since_signup / 2, days_since_signup / 3)))
    delta_days = max(1, min(days_since_signup, delta_days))
    order_date = signup_date + timedelta(days=delta_days)
    order_time = datetime.combine(order_date, datetime.min.time()) + timedelta(
        hours=random.randint(8, 21), minutes=random.randint(0, 59)
    )
    return order_time


def generate_orders(customers: List[Dict], avg_orders_per_customer: float = 2.5) -> List[Dict]:
    orders = []
    oid = 1
    for c in customers:
        orders_count = max(1, int(random.poisson(lam=avg_orders_per_customer))) if hasattr(random, "poisson") else max(
            1, int(random.gauss(avg_orders_per_customer, 1))
        )
        for _ in range(orders_count):
            order_dt = random_order_date(c["signup_date"])
            orders.append(
                {
                    "order_id": oid,
                    "customer_id": c["customer_id"],
                    "order_datetime": order_dt,
                    "shipping_state": c["state"],
                }
            )
            oid += 1
    orders.sort(key=lambda o: o["order_datetime"])
    return orders


def generate_order_details(orders: List[Dict], products: List[Dict]) -> List[Dict]:
    details = []
    detail_id = 1
    for order in orders:
        item_count = max(1, int(random.gauss(2, 1)))
        chosen_products = random.sample(products, k=min(item_count, len(products)))
        for product in chosen_products:
            quantity = max(1, int(random.gauss(2, 1)))
            discount = 0 if random.random() < 0.7 else round(random.uniform(0.05, 0.25), 2)
            line_total = round(product["unit_price"] * quantity * (1 - discount), 2)
            details.append(
                {
                    "order_detail_id": detail_id,
                    "order_id": order["order_id"],
                    "product_id": product["product_id"],
                    "quantity": quantity,
                    "unit_price": product["unit_price"],
                    "discount": discount,
                    "line_total": line_total,
                }
            )
            detail_id += 1
    return details


def generate_payments(orders: List[Dict], order_details: List[Dict]) -> List[Dict]:
    detail_totals = {}
    for d in order_details:
        detail_totals.setdefault(d["order_id"], 0)
        detail_totals[d["order_id"]] += d["line_total"]

    payments = []
    pid = 1
    for order in orders:
        gross = detail_totals[order["order_id"]]
        tax = round(gross * random.uniform(0.05, 0.095), 2)
        shipping = 0 if gross >= 75 else round(random.uniform(4.99, 14.99), 2)
        total = round(gross + tax + shipping, 2)
        payments.append(
            {
                "payment_id": pid,
                "order_id": order["order_id"],
                "payment_method": random.choices(PAYMENT_METHODS, weights=[40, 25, 20, 10, 5])[0],
                "payment_datetime": order["order_datetime"] + timedelta(minutes=random.randint(5, 90)),
                "subtotal": round(gross, 2),
                "tax": tax,
                "shipping": shipping,
                "total": total,
                "currency": "USD",
            }
        )
        pid += 1
    return payments


def write_csv(filename: Path, rows: List[Dict], fieldnames: List[str]) -> None:
    with filename.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    customer_count = 200
    customers = generate_customers(customer_count)
    products = generate_products()
    orders = generate_orders(customers)
    order_details = generate_order_details(orders, products)
    payments = generate_payments(orders, order_details)

    write_csv(
        OUTPUT_DIR / "customers.csv",
        customers,
        ["customer_id", "name", "email", "phone", "state", "signup_date"],
    )
    write_csv(
        OUTPUT_DIR / "products.csv",
        products,
        ["product_id", "name", "category", "unit_price", "stock"],
    )
    write_csv(
        OUTPUT_DIR / "orders.csv",
        orders,
        ["order_id", "customer_id", "order_datetime", "shipping_state"],
    )
    write_csv(
        OUTPUT_DIR / "order_details.csv",
        order_details,
        ["order_detail_id", "order_id", "product_id", "quantity", "unit_price", "discount", "line_total"],
    )
    write_csv(
        OUTPUT_DIR / "payments.csv",
        payments,
        ["payment_id", "order_id", "payment_method", "payment_datetime", "subtotal", "tax", "shipping", "total", "currency"],
    )

    print(f"Generated data in {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()

