# E-Commerce Data Pipeline Assignment

A Python project that generates synthetic e-commerce data, loads it into a SQLite database, and performs analytical queries. The data mimics realistic retail patterns with proper relationships between customers, orders, products, and payments.

## Project Overview

This assignment consists of three main components:

1. **Data Generation** - Creates realistic synthetic e-commerce data in CSV format
2. **Data Ingestion** - Loads CSV files into a SQLite database with proper schema
3. **Data Analysis** - Queries the database to identify top customer spenders

## Project Structure

```
.
├── synthetic_data_generator.py  # Generates synthetic CSV data
├── ingest_to_sqlite.py          # Loads CSVs into SQLite database
├── query_top_spenders.py         # Queries top 5 customer spenders
├── data_output/                  # Generated CSV files
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── order_details.csv
│   └── payments.csv
├── ecommerce.db                  # SQLite database (generated)
└── README.md                     # This file
```

## Requirements

- Python 3.7+
- pandas
- sqlite3 (included with Python)

Install dependencies:
```bash
pip install pandas
```

## Database Schema

The SQLite database contains five related tables:

- **customers** - Customer information (ID, name, email, phone, state, signup_date)
- **products** - Product catalog (ID, name, category, unit_price, stock)
- **orders** - Order headers (ID, customer_id, order_datetime, shipping_state)
- **order_details** - Order line items (ID, order_id, product_id, quantity, unit_price, discount, line_total)
- **payments** - Payment transactions (ID, order_id, payment_method, payment_datetime, subtotal, tax, shipping, total, currency)

All tables are linked via foreign key relationships to ensure referential integrity.

## Usage

### Step 1: Generate Synthetic Data

Generate realistic e-commerce data and save it as CSV files:

```bash
python synthetic_data_generator.py
```

This creates five CSV files in the `data_output/` directory:
- `customers.csv` - 200 customers with realistic names, emails, and locations
- `products.csv` - 20 products across 4 categories (Electronics, Home, Beauty, Sports)
- `orders.csv` - Orders linked to customers with realistic timestamps
- `order_details.csv` - Order line items with quantities and pricing
- `payments.csv` - Payment records with taxes, shipping, and totals

**Features:**
- Realistic name distributions using common first/last names
- Normal price distributions within category ranges
- Temporal relationships (orders occur after customer signup)
- Proper ID linking across all tables
- Realistic discounts, taxes, and shipping costs

### Step 2: Ingest Data into SQLite Database

Load the CSV files into a SQLite database:

```bash
python ingest_to_sqlite.py
```

This script:
- Creates the `ecommerce.db` database (or replaces existing)
- Defines table schemas with foreign key constraints
- Loads all CSV data with proper type conversions
- Normalizes datetime formats to ISO 8601

### Step 3: Query Top Spenders

Query the database to find the top 5 customers by total spend:

```bash
python query_top_spenders.py
```

This executes a SQL query that:
- Joins customers, orders, order_details, and products tables
- Calculates total spend per customer using `SUM(quantity * unit_price)`
- Groups by customer name
- Orders by total spend descending
- Displays the top 5 results using pandas

## Example Output

Running `query_top_spenders.py` produces output like:

```
customer_name    total_spend
   customer_name  total_spend
Benjamin Jackson      2134.63
    Sophia White      1716.07
     Emma Harris      1593.36
 Sophia Anderson      1372.63
     Henry Smith      1362.14
     
```

## Data Characteristics

The synthetic data is designed to mimic real e-commerce patterns:

- **Customer Distribution**: 200 customers across 10 US states
- **Product Catalog**: 20 products in 4 categories with realistic price ranges
- **Order Patterns**: Average of 2.5 orders per customer with Poisson distribution
- **Pricing**: Normal distribution within category-specific ranges
- **Temporal Logic**: Orders occur after customer signup dates
- **Discounts**: 30% of items have discounts between 5-25%
- **Shipping**: Free shipping for orders over $75, otherwise $4.99-$14.99
- **Taxes**: 5-9.5% tax rate applied to subtotals

## Notes

- The data generator uses a fixed random seed (42) for reproducibility
- All foreign key relationships are enforced in the database schema
- Datetime values are normalized to ISO 8601 format during ingestion
- The database uses SQLite's foreign key constraints (PRAGMA foreign_keys = ON)

## License

This project is for educational/assignment purposes.

