"""
Superstore Sales Dataset Generator for Practical 12: Customer Sales Dashboard
Generates an authentic, rich multi-year Superstore Sales dataset with
orders, customer segments, regional geographies, and financial metrics.
"""

import csv
import random
from datetime import datetime, timedelta
import os

CATEGORIES = {
    "Technology": {
        "Phones": (150, 1200, 0.15, 0.35),
        "Copiers": (400, 3000, 0.25, 0.45),
        "Accessories": (25, 250, 0.20, 0.40),
        "Machines": (300, 2500, -0.05, 0.20)
    },
    "Office Supplies": {
        "Storage": (30, 450, 0.10, 0.25),
        "Binders": (5, 120, 0.15, 0.38),
        "Paper": (10, 90, 0.25, 0.45),
        "Art": (8, 60, 0.18, 0.32),
        "Appliances": (50, 600, 0.12, 0.28),
        "Envelopes": (6, 50, 0.20, 0.35),
        "Labels": (4, 40, 0.25, 0.40),
        "Fasteners": (3, 25, 0.20, 0.35)
    },
    "Furniture": {
        "Chairs": (80, 700, 0.05, 0.20),
        "Furnishings": (15, 180, 0.12, 0.28),
        "Bookcases": (90, 800, -0.15, 0.12),
        "Tables": (120, 1100, -0.25, 0.05)   # Tables often loss-making in retail
    }
}

REGIONS_STATES = {
    "West": [("California", "Los Angeles", "90036"), ("California", "San Francisco", "94109"),
             ("Washington", "Seattle", "98105"), ("Oregon", "Portland", "97201"),
             ("Colorado", "Denver", "80219"), ("Arizona", "Phoenix", "85001")],
    "East": [("New York", "New York City", "10024"), ("Pennsylvania", "Philadelphia", "19140"),
             ("Massachusetts", "Boston", "02116"), ("Ohio", "Columbus", "43229"),
             ("New Jersey", "Newark", "07102")],
    "Central": [("Illinois", "Chicago", "60653"), ("Texas", "Houston", "77005"),
                ("Texas", "Dallas", "75220"), ("Michigan", "Detroit", "48227"),
                ("Minnesota", "Minneapolis", "55407"), ("Wisconsin", "Milwaukee", "53209")],
    "South": [("Florida", "Miami", "33125"), ("Florida", "Tampa", "33612"),
              ("Georgia", "Atlanta", "30318"), ("North Carolina", "Charlotte", "28205"),
              ("Virginia", "Richmond", "23219"), ("Tennessee", "Nashville", "37211")]
}

CUSTOMER_NAMES = [
    "Claire Gute", "Brosina Hoffman", "Darrin Van Huff", "Sean O'Donnell", "Zuschuss Donatelli",
    "Eric Hoffmann", "Ruben Dartt", "Ted Butterfield", "Hunter Lopez", "Jack Fabrikant",
    "David Kendrick", "Robert Marcy", "Sandra Flanagan", "Tamara Chand", "Raymond Buch",
    "Tom Boeckenhauer", "Sanjit Chand", "Bill Tyler", "Nora Pelletier", "Kelly Collister",
    "Harry Marie", "Arthur Prichep", "Lena Cacioppo", "Ken Brennan", "Patrick Jones",
    "Jane Waco", "Laura Armstrong", "Joe Elijah", "Seth Vernon", "Maria Etezadi"
]

SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SEGMENT_WEIGHTS = [0.52, 0.30, 0.18]
SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
SHIP_WEIGHTS = [0.60, 0.20, 0.15, 0.05]

def generate_dataset():
    random.seed(42)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_csv = os.path.join(base_dir, "superstore_sales.csv")
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 6, 30)
    total_days = (end_date - start_date).days
    
    total_records = 5000
    rows = []
    
    for i in range(1, total_records + 1):
        order_days = random.randint(0, total_days)
        order_date = start_date + timedelta(days=order_days)
        ship_days = random.randint(1, 6)
        ship_date = order_date + timedelta(days=ship_days)
        
        region = random.choice(list(REGIONS_STATES.keys()))
        state, city, postal = random.choice(REGIONS_STATES[region])
        
        segment = random.choices(SEGMENTS, weights=SEGMENT_WEIGHTS)[0]
        ship_mode = random.choices(SHIP_MODES, weights=SHIP_WEIGHTS)[0]
        customer_name = random.choice(CUSTOMER_NAMES)
        customer_id = f"{''.join([w[0] for w in customer_name.split()[:2]])}-{random.randint(10000, 99999)}"
        
        category = random.choice(list(CATEGORIES.keys()))
        sub_cat = random.choice(list(CATEGORIES[category].keys()))
        min_p, max_p, min_m, max_m = CATEGORIES[category][sub_cat]
        
        unit_price = round(random.uniform(min_p, max_p), 2)
        quantity = random.randint(1, 9)
        discount = round(random.choice([0.0, 0.0, 0.1, 0.15, 0.2, 0.3, 0.5, 0.7]), 2)
        
        sales = round(unit_price * quantity * (1.0 - discount), 2)
        margin = random.uniform(min_m, max_m)
        
        # Heavy discounts turn transactions negative
        if discount >= 0.3:
            profit = round(sales * (margin - discount * 0.8), 2)
        else:
            profit = round(sales * margin, 2)
            
        order_id = f"CA-{order_date.year}-{random.randint(100000, 999999)}"
        product_id = f"{category[:3].upper()}-{sub_cat[:2].upper()}-{random.randint(10000000, 99999999)}"
        product_name = f"{sub_cat} Pro Series model {random.randint(100, 999)}"
        
        rows.append([
            order_id,
            order_date.strftime("%Y-%m-%d"),
            ship_date.strftime("%Y-%m-%d"),
            ship_mode,
            customer_id,
            customer_name,
            segment,
            "United States",
            city,
            state,
            postal,
            region,
            product_id,
            category,
            sub_cat,
            product_name,
            sales,
            quantity,
            discount,
            profit
        ])
        
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Order ID", "Order Date", "Ship Date", "Ship Mode", "Customer ID",
            "Customer Name", "Segment", "Country", "City", "State", "Postal Code",
            "Region", "Product ID", "Category", "Sub-Category", "Product Name",
            "Sales", "Quantity", "Discount", "Profit"
        ])
        writer.writerows(rows)
        
    print(f"Generated {total_records} Superstore Sales records to {output_csv}")

if __name__ == "__main__":
    generate_dataset()
