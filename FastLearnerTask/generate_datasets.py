"""
Dataset Generator for BDA Fast Learner Tasks
Author: Sil Shah (24DIT066)
Generates authentic datasets:
1. india_air_quality.csv (For Task 1: End-to-end Mini Project)
2. server_access_logs.txt (For Task 2: MapReduce vs Spark Benchmark)
3. customer_churn.csv (For Task 4: Spark MLlib Machine Learning)
"""

import os
import random
import csv
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

random.seed(42)

def generate_air_quality_dataset():
    filepath = os.path.join(DATA_DIR, "india_air_quality.csv")
    print("Generating India Air Quality Dataset...")
    
    cities = [
        ("Delhi", "Delhi", (150, 420)),
        ("Gurugram", "Haryana", (140, 390)),
        ("Noida", "Uttar Pradesh", (135, 380)),
        ("Lucknow", "Uttar Pradesh", (110, 310)),
        ("Patna", "Bihar", (130, 360)),
        ("Kolkata", "West Bengal", (85, 230)),
        ("Ahmedabad", "Gujarat", (90, 240)),
        ("Surat", "Gujarat", (75, 190)),
        ("Vadodara", "Gujarat", (70, 180)),
        ("Mumbai", "Maharashtra", (65, 175)),
        ("Pune", "Maharashtra", (60, 160)),
        ("Bengaluru", "Karnataka", (45, 120)),
        ("Hyderabad", "Telangana", (60, 150)),
        ("Chennai", "Tamil Nadu", (50, 130)),
        ("Jaipur", "Rajasthan", (95, 260)),
        ("Varanasi", "Uttar Pradesh", (100, 290)),
        ("Bhopal", "Madhya Pradesh", (70, 180)),
        ("Indore", "Madhya Pradesh", (65, 170)),
        ("Visakhapatnam", "Andhra Pradesh", (55, 135)),
        ("Kochi", "Kerala", (35, 95))
    ]
    
    start_date = datetime(2024, 1, 1)
    rows = []
    
    for day in range(730):  # 2 years (2024 - 2025)
        cur_date = start_date + timedelta(days=day)
        month = cur_date.month
        # Winter season modifier (Nov, Dec, Jan, Feb have high pollution)
        season_mod = 1.45 if month in [11, 12, 1, 2] else (0.75 if month in [7, 8, 9] else 1.0)
        
        for city, state, (min_aqi, max_aqi) in cities:
            base_aqi = random.uniform(min_aqi, max_aqi) * season_mod
            aqi = round(min(500, max(25, base_aqi + random.gauss(0, 15))), 1)
            
            pm25 = round(aqi * random.uniform(0.40, 0.55), 1)
            pm10 = round(pm25 * random.uniform(1.6, 2.2), 1)
            no2 = round(random.uniform(15, 85) * (aqi / 200.0), 1)
            so2 = round(random.uniform(8, 45) * (aqi / 250.0), 1)
            co = round(random.uniform(0.4, 2.8) * (aqi / 180.0), 2)
            o3 = round(random.uniform(10, 65), 1)
            
            if aqi <= 50:
                bucket = "Good"
            elif aqi <= 100:
                bucket = "Satisfactory"
            elif aqi <= 200:
                bucket = "Moderate"
            elif aqi <= 300:
                bucket = "Poor"
            elif aqi <= 400:
                bucket = "Very Poor"
            else:
                bucket = "Severe"
                
            rows.append([
                cur_date.strftime("%Y-%m-%d"),
                city,
                state,
                pm25,
                pm10,
                no2,
                so2,
                co,
                o3,
                aqi,
                bucket
            ])
            
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "City", "State", "PM2_5", "PM10", "NO2", "SO2", "CO", "Ozone", "AQI", "AQI_Bucket"])
        writer.writerows(rows)
        
    print(f"Saved {len(rows)} records to {filepath}")

def generate_server_logs_dataset():
    filepath = os.path.join(DATA_DIR, "server_access_logs.txt")
    print("Generating Large Server Access Logs Dataset for Benchmark...")
    
    endpoints = [
        "/api/v1/auth/login",
        "/api/v1/products/list",
        "/api/v1/cart/checkout",
        "/api/v1/user/profile",
        "/api/v1/orders/history",
        "/api/v1/payment/process",
        "/static/css/main.css",
        "/static/js/bundle.js",
        "/api/v1/search/query",
        "/healthcheck"
    ]
    endpoint_weights = [15, 30, 8, 12, 10, 5, 20, 25, 18, 7]
    
    methods = ["GET", "POST", "PUT", "DELETE"]
    status_codes = [200, 201, 304, 400, 401, 403, 404, 500, 502]
    status_weights = [70, 8, 10, 3, 2, 1, 4, 1.5, 0.5]
    
    num_records = 300000  # 300,000 records for benchmark
    start_time = datetime(2026, 10, 1, 0, 0, 0)
    
    with open(filepath, "w", encoding="utf-8") as f:
        for i in range(num_records):
            ip = f"192.168.{random.randint(1, 45)}.{random.randint(1, 254)}"
            t = start_time + timedelta(seconds=i * 0.25)
            t_str = t.strftime("%d/%b/%Y:%H:%M:%S +0530")
            method = random.choices(methods, weights=[65, 25, 7, 3])[0]
            endpoint = random.choices(endpoints, weights=endpoint_weights)[0]
            status = random.choices(status_codes, weights=status_weights)[0]
            bytes_sent = random.randint(120, 45000) if status == 200 else random.randint(40, 500)
            
            line = f'{ip} - - [{t_str}] "{method} {endpoint} HTTP/1.1" {status} {bytes_sent}\n'
            f.write(line)
            
    print(f"Saved {num_records} log lines to {filepath} (Size: {os.path.getsize(filepath) / (1024*1024):.2f} MB)")

def generate_customer_churn_dataset():
    filepath = os.path.join(DATA_DIR, "customer_churn.csv")
    print("Generating Customer Churn Dataset for MLlib...")
    
    contracts = ["Month-to-month", "One year", "Two year"]
    internets = ["DSL", "Fiber optic", "No"]
    tech_supports = ["Yes", "No", "No internet service"]
    num_records = 12000
    
    rows = []
    for i in range(1, num_records + 1):
        cid = f"CUST-{10000 + i}"
        age = random.randint(18, 75)
        tenure = random.randint(1, 72)
        contract = random.choices(contracts, weights=[55, 25, 20])[0]
        internet = random.choices(internets, weights=[35, 45, 20])[0]
        tech_support = random.choices(tech_supports, weights=[30, 50, 20])[0]
        
        # Monthly charges depend on internet service
        base_monthly = 25.0 if internet == "No" else (55.0 if internet == "DSL" else 85.0)
        monthly_charges = round(base_monthly + random.uniform(-10, 25), 2)
        total_charges = round(monthly_charges * tenure + random.uniform(0, 100), 2)
        service_calls = random.randint(0, 6)
        
        # Calculate realistic churn probability
        churn_score = 0.0
        if contract == "Month-to-month":
            churn_score += 0.35
        if tenure < 12:
            churn_score += 0.25
        if internet == "Fiber optic":
            churn_score += 0.15
        if service_calls >= 3:
            churn_score += 0.30
        if tech_support == "No":
            churn_score += 0.15
        if monthly_charges > 80:
            churn_score += 0.10
            
        prob = min(0.92, max(0.04, churn_score + random.gauss(0, 0.12)))
        churn = 1 if random.random() < prob else 0
        
        rows.append([
            cid, age, tenure, contract, internet, tech_support, monthly_charges, total_charges, service_calls, churn
        ])
        
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["CustomerID", "Age", "TenureMonths", "ContractType", "InternetService", "TechSupport", "MonthlyCharges", "TotalCharges", "CustomerServiceCalls", "Churn"])
        writer.writerows(rows)
        
    print(f"Saved {num_records} records to {filepath}")

if __name__ == "__main__":
    generate_air_quality_dataset()
    generate_server_logs_dataset()
    generate_customer_churn_dataset()
    print("All datasets generated successfully!")
