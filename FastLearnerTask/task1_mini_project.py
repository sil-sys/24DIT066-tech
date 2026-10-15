"""
Task 1: End-to-End Big Data Mini Project
Dataset: Indian Air Quality Index (Open Data from data.gov.in / Kaggle)
Author: Sil Shah (24DIT066)
Course: CSUE301 - Big Data Analytics

Workflow:
1. Ingest dataset into simulated HDFS path / distributed storage
2. Process with PySpark (Data cleaning, schema definition, aggregations, window functions)
3. Generate 3 core insights with publication-quality charts:
   - Insight 1: Spatial Pollution Disparity (Top Polluted Cities)
   - Insight 2: Seasonal Pollution Trajectory (Winter Peak vs Monsoon Washout)
   - Insight 3: Particulate Matter Composition & AQI Category Distribution
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, avg, max as spark_max, min as spark_min, count,
    round as spark_round, month, year, when, desc
)
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, DateType
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "india_air_quality.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_mini_project():
    print("=" * 70)
    print("Task 1: End-to-End Big Data Mini Project - India Air Quality Analysis")
    print("Author: Sil Shah (24DIT066) | BDA Fast Learners Assignment")
    print("=" * 70)
    
    # 1. Initialize Spark Session
    spark = SparkSession.builder \
        .appName("Task1_AirQuality_Analysis_24DIT066") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("WARN")
    print(f"\n[+] Apache Spark Session Initialized (Version: {spark.version})")
    
    # 2. Ingest Dataset
    print(f"[+] Ingesting data from storage: {DATA_PATH}")
    df = spark.read.csv(DATA_PATH, header=True, inferSchema=True)
    
    print("\n--- Raw Dataset Schema ---")
    df.printSchema()
    
    total_records = df.count()
    print(f"\n[+] Total Ingested Records: {total_records:,}")
    
    # 3. Data Cleaning & Transformation
    cleaned_df = df.filter(col("AQI").isNotNull() & col("City").isNotNull()) \
                   .withColumn("Date", col("Date").cast(DateType())) \
                   .withColumn("Year", year(col("Date"))) \
                   .withColumn("Month", month(col("Date")))
                   
    print(f"[+] Records after quality validation & cleaning: {cleaned_df.count():,}")
    
    print("\n--- Sample Cleaned Records ---")
    cleaned_df.select("Date", "City", "State", "PM2_5", "PM10", "AQI", "AQI_Bucket").show(5, truncate=False)
    
    # -------------------------------------------------------------
    # INSIGHT 1: Spatial Pollution Disparity (Top 10 Most Polluted Cities)
    # -------------------------------------------------------------
    print("\n[+] Computing Insight 1: Spatial Pollution Disparity (Top Cities)...")
    city_aqi_df = cleaned_df.groupBy("City", "State") \
        .agg(
            spark_round(avg("AQI"), 2).alias("Avg_AQI"),
            spark_round(avg("PM2_5"), 2).alias("Avg_PM2_5"),
            spark_round(avg("PM10"), 2).alias("Avg_PM10"),
            spark_round(spark_max("AQI"), 2).alias("Max_AQI")
        ) \
        .orderBy(desc("Avg_AQI"))
        
    print("\n--- Top 10 Most Polluted Cities by Average AQI ---")
    city_aqi_df.show(10, truncate=False)
    
    top_10_cities = city_aqi_df.limit(10).toPandas()
    
    # Chart 1: Top 10 Cities
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    bars = ax.barh(top_10_cities["City"][::-1], top_10_cities["Avg_AQI"][::-1], 
                   color='#D9534F', edgecolor='#A94442', alpha=0.9, height=0.65)
    
    # Threshold lines for CPCB / WHO National Ambient Air Quality standards
    ax.axvline(x=100, color='#5CB85C', linestyle='--', linewidth=1.5, label='Satisfactory Threshold (AQI 100)')
    ax.axvline(x=200, color='#F0AD4E', linestyle='--', linewidth=1.5, label='Moderate/Poor Threshold (AQI 200)')
    ax.axvline(x=300, color='#D9534F', linestyle='--', linewidth=1.5, label='Very Poor Threshold (AQI 300)')
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 3, bar.get_y() + bar.get_height()/2, f'{width:.1f}', 
                va='center', ha='left', fontsize=9.5, fontweight='bold', color='#333333')
                
    ax.set_title("Insight 1: Top 10 Most Polluted Indian Cities by Mean AQI\n(24DIT066 - Big Data Mini Project)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Average Air Quality Index (AQI)", fontsize=11, fontweight='bold')
    ax.set_ylabel("City", fontsize=11, fontweight='bold')
    ax.set_xlim(0, 420)
    ax.grid(axis='x', linestyle=':', alpha=0.6)
    ax.legend(loc='lower right', framealpha=0.9)
    plt.tight_layout()
    chart1_path = os.path.join(OUTPUT_DIR, "insight1_top_polluted_cities.png")
    plt.savefig(chart1_path)
    plt.close()
    print(f"[+] Saved Chart 1: {chart1_path}")
    
    # -------------------------------------------------------------
    # INSIGHT 2: Seasonal Pollution Trajectory (Winter Peak vs Monsoon)
    # -------------------------------------------------------------
    print("\n[+] Computing Insight 2: Seasonal Pollution Trajectory...")
    metro_cities = ["Delhi", "Kolkata", "Mumbai", "Bengaluru", "Ahmedabad"]
    monthly_trend_df = cleaned_df.filter(col("City").isin(metro_cities)) \
        .groupBy("Month", "City") \
        .agg(spark_round(avg("AQI"), 2).alias("Monthly_Avg_AQI")) \
        .orderBy("Month", "City")
        
    trend_pddf = monthly_trend_df.toPandas()
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    palette = {"Delhi": "#D9534F", "Kolkata": "#F0AD4E", "Ahmedabad": "#337AB7", "Mumbai": "#5CB85C", "Bengaluru": "#9C27B0"}
    
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    for city in metro_cities:
        city_data = trend_pddf[trend_pddf["City"] == city].sort_values("Month")
        ax.plot(city_data["Month"], city_data["Monthly_Avg_AQI"], marker='o', linewidth=2.2, 
                markersize=6, label=city, color=palette.get(city, "#333333"))
                
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(months, fontweight='bold')
    ax.set_title("Insight 2: Seasonal AQI Trajectory Across Major Metros (Winter Spike Phenomenon)\n(24DIT066 - Big Data Mini Project)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Month of Year", fontsize=11, fontweight='bold')
    ax.set_ylabel("Monthly Mean AQI", fontsize=11, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # Highlight Winter Season vs Monsoon Season
    ax.axvspan(10.5, 12.5, color='#FFCDD2', alpha=0.35, label='Winter Inversion Period (Nov-Feb)')
    ax.axvspan(0.5, 2.5, color='#FFCDD2', alpha=0.35)
    ax.axvspan(6.5, 9.5, color='#C8E6C9', alpha=0.35, label='Monsoon Washout Period (Jul-Sep)')
    
    ax.legend(loc='upper right', framealpha=0.92)
    plt.tight_layout()
    chart2_path = os.path.join(OUTPUT_DIR, "insight2_seasonal_trajectory.png")
    plt.savefig(chart2_path)
    plt.close()
    print(f"[+] Saved Chart 2: {chart2_path}")
    
    # -------------------------------------------------------------
    # INSIGHT 3: AQI Bucket Distribution & Particulate Composition
    # -------------------------------------------------------------
    print("\n[+] Computing Insight 3: AQI Category Breakdown & Particulate Ratios...")
    bucket_df = cleaned_df.groupBy("AQI_Bucket") \
        .agg(
            count("*").alias("Total_Days"),
            spark_round(avg("PM2_5"), 2).alias("Mean_PM25"),
            spark_round(avg("PM10"), 2).alias("Mean_PM10")
        ) \
        .withColumn("Percentage", spark_round((col("Total_Days") / total_records) * 100, 2)) \
        .orderBy(desc("Total_Days"))
        
    print("\n--- AQI Severity Category Distribution ---")
    bucket_df.show(truncate=False)
    
    bucket_pddf = bucket_df.toPandas()
    
    order = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
    bucket_pddf["sort_order"] = bucket_pddf["AQI_Bucket"].map(lambda x: order.index(x) if x in order else 99)
    bucket_pddf = bucket_pddf.sort_values("sort_order")
    
    colors = ['#5CB85C', '#8BC34A', '#FFEB3B', '#FF9800', '#F44336', '#9C27B0']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), dpi=300)
    
    # Donut chart of distribution
    wedges, texts, autotexts = ax1.pie(
        bucket_pddf["Total_Days"], 
        labels=bucket_pddf["AQI_Bucket"], 
        autopct='%1.1f%%',
        startangle=140, 
        colors=colors, 
        wedgeprops=dict(width=0.45, edgecolor='w')
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_fontweight('bold')
    ax1.set_title("AQI Category Proportion (% Days)", fontsize=11, fontweight='bold')
    
    # Stacked bar of PM2.5 vs PM10
    x = np.arange(len(bucket_pddf))
    w = 0.55
    ax2.bar(x, bucket_pddf["Mean_PM25"], width=w, label="PM2.5 (Fine Particulates)", color="#D9534F", alpha=0.9)
    ax2.bar(x, bucket_pddf["Mean_PM10"] - bucket_pddf["Mean_PM25"], bottom=bucket_pddf["Mean_PM25"], 
            width=w, label="Coarse PM (PM10 - PM2.5)", color="#337AB7", alpha=0.9)
            
    ax2.set_xticks(x)
    ax2.set_xticklabels(bucket_pddf["AQI_Bucket"], rotation=25, ha='right', fontsize=9.5)
    ax2.set_ylabel("Concentration (µg/m³)", fontsize=10, fontweight='bold')
    ax2.set_title("Mean Particulate Matter Load by Category", fontsize=11, fontweight='bold')
    ax2.grid(axis='y', linestyle=':', alpha=0.6)
    ax2.legend(loc='upper left', framealpha=0.9)
    
    plt.suptitle("Insight 3: AQI Distribution & Particulate Composition in India (24DIT066)", fontsize=13, fontweight='bold', y=0.98)
    plt.tight_layout()
    chart3_path = os.path.join(OUTPUT_DIR, "insight3_aqi_distribution.png")
    plt.savefig(chart3_path)
    plt.close()
    print(f"[+] Saved Chart 3: {chart3_path}")
    
    spark.stop()
    print("\n[+] Task 1 Completed Successfully!")

if __name__ == "__main__":
    run_mini_project()
