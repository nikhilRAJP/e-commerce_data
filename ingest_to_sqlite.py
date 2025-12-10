"""
Ingest the synthetic e-commerce CSVs from data_output/ into a SQLite database.

Creates (or replaces) tables:
  customers, products, orders, order_details, payments

Run:
  python ingest_to_sqlite.py
"""

import csv
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple

DATA_DIR = Path("data_output")
DB_PATH = Path("ecommerce.db")


def read_csv(path: Path) -> Iterable[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def parse_datetime(value: str) -> str:
    # Normalize to ISO 8601; input was produced by datetime.__str__
    dt = datetime.fromisoformat(value)
    return dt.isoformat(sep=" ")


def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
        PRAGMA foreign_keys = ON;

        DROP TABLE IF EXISTS order_details;
        DROP TABLE IF EXISTS payments;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            customer_id    INTEGER PRIMARY KEY,
            name           TEXT NOT NULL,
            email          TEXT NOT NULL,
            phone          TEXT,
            state          TEXT,
            signup_date    TEXT
        );

        CREATE TABLE products (
            product_id   INTEGER PRIMARY KEY,
            name         TEXT NOT NULL,
            category     TEXT,
            unit_price   REAL,
            stock        INTEGER
        );

        CREATE TABLE orders (
            order_id        INTEGER PRIMARY KEY,
            customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
            order_datetime  TEXT NOT NULL,
            shipping_state  TEXT
        );

        CREATE TABLE order_details (
            order_detail_id INTEGER PRIMARY KEY,
            order_id        INTEGER NOT NULL REFERENCES orders(order_id),
            product_id      INTEGER NOT NULL REFERENCES products(product_id),
            quantity        INTEGER NOT NULL,
            unit_price      REAL NOT NULL,
            discount        REAL NOT NULL,
            line_total      REAL NOT NULL
        );

        CREATE TABLE payments (
            payment_id       INTEGER PRIMARY KEY,
            order_id         INTEGER NOT NULL REFERENCES orders(order_id),
            payment_method   TEXT,
            payment_datetime TEXT NOT NULL,
            subtotal         REAL NOT NULL,
            tax              REAL NOT NULL,
            shipping         REAL NOT NULL,
            total            REAL NOT NULL,
            currency         TEXT NOT NULL
        );
        """
    )
    conn.commit()


def insert_customers(conn: sqlite3.Connection) -> None:
    rows = (
        (
            int(r["customer_id"]),
            r["name"],
            r["email"],
            r.get("phone"),
            r.get("state"),
            r.get("signup_date"),
        )
        for r in read_csv(DATA_DIR / "customers.csv")
    )
    conn.executemany(
        "INSERT INTO customers VALUES (?,?,?,?,?,?)",
        rows,
    )
    conn.commit()


def insert_products(conn: sqlite3.Connection) -> None:
    rows = (
        (
            int(r["product_id"]),
            r["name"],
            r.get("category"),
            float(r["unit_price"]),
            int(r["stock"]),
        )
        for r in read_csv(DATA_DIR / "products.csv")
    )
    conn.executemany(
        "INSERT INTO products VALUES (?,?,?,?,?)",
        rows,
    )
    conn.commit()


def insert_orders(conn: sqlite3.Connection) -> None:
    rows = (
        (
            int(r["order_id"]),
            int(r["customer_id"]),
            parse_datetime(r["order_datetime"]),
            r.get("shipping_state"),
        )
        for r in read_csv(DATA_DIR / "orders.csv")
    )
    conn.executemany(
        "INSERT INTO orders VALUES (?,?,?,?)",
        rows,
    )
    conn.commit()


def insert_order_details(conn: sqlite3.Connection) -> None:
    rows = (
        (
            int(r["order_detail_id"]),
            int(r["order_id"]),
            int(r["product_id"]),
            int(r["quantity"]),
            float(r["unit_price"]),
            float(r["discount"]),
            float(r["line_total"]),
        )
        for r in read_csv(DATA_DIR / "order_details.csv")
    )
    conn.executemany(
        "INSERT INTO order_details VALUES (?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()


def insert_payments(conn: sqlite3.Connection) -> None:
    rows = (
        (
            int(r["payment_id"]),
            int(r["order_id"]),
            r.get("payment_method"),
            parse_datetime(r["payment_datetime"]),
            float(r["subtotal"]),
            float(r["tax"]),
            float(r["shipping"]),
            float(r["total"]),
            r.get("currency"),
        )
        for r in read_csv(DATA_DIR / "payments.csv")
    )
    conn.executemany(
        "INSERT INTO payments VALUES (?,?,?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()


def main() -> None:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)
        insert_customers(conn)
        insert_products(conn)
        insert_orders(conn)
        insert_order_details(conn)
        insert_payments(conn)

    print(f"Ingest complete. SQLite database at {DB_PATH.resolve()}")


if __name__ == "__main__":
    main()

