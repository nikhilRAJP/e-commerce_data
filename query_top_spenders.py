"""
Query top customer spenders from ecommerce.db using pandas.

Run:
  python query_top_spenders.py
"""

import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("ecommerce.db")

SQL = """
SELECT
    c.name AS customer_name,
    SUM(od.quantity * od.unit_price) AS total_spend
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_details od ON od.order_id = o.order_id
JOIN products p ON p.product_id = od.product_id
GROUP BY c.name
ORDER BY total_spend DESC
LIMIT 5;
"""


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(SQL, conn)

    print(df.to_string(index=False))


if __name__ == "__main__":
    main()

