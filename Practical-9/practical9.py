"""
========================================================================================
BDA Practical 9: Social Media Trend Detection Using PySpark
Scenario: TrendPulse Social Media Analytics - Multi-Platform Trend Engine
Student Practical Implementation (PySpark + Matplotlib)
========================================================================================
"""

import os
import matplotlib
matplotlib.use('Agg')  # Headless backend for terminal / automated execution
import matplotlib.pyplot as plt

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, desc, when, row_number
from pyspark.sql.window import Window

def print_separator(title=""):
    print("\n" + "=" * 65)
    if title:
        print(f" {title.upper()}")
        print("=" * 65)

def main():
    # -------------------------------------------------------------------------
    # TASK 1: CREATE SPARK SESSION
    # -------------------------------------------------------------------------
    print_separator("TASK 1: CREATING SPARK SESSION")
    
    spark = SparkSession.builder \
        .appName("Social-Media-Trend-Detection") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
        
    # Suppress verbose internal Spark logs for clean terminal output and screenshots
    spark.sparkContext.setLogLevel("ERROR")
    
    print(f"Spark Version   : {spark.version}")
    print(f"Spark App Name  : {spark.sparkContext.appName}")
    print(f"Master URL      : {spark.sparkContext.master}")

    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "social_media_hashtags.csv")
    chart_path = os.path.join(base_dir, "hashtag_trends.png")
    report_path = os.path.join(base_dir, "trend_analysis_report.txt")

    # -------------------------------------------------------------------------
    # TASK 2: LOAD DATASET
    # -------------------------------------------------------------------------
    print_separator("TASK 2: LOADING SOCIAL MEDIA HASHTAG DATASET")
    print(f"Dataset Path    : {dataset_path}")
    
    df = spark.read.csv(
        dataset_path,
        header=True,
        inferSchema=True
    )
    print("Dataset loaded successfully.")
    
    total_records = df.count()
    print(f"Total Number of Records: {total_records:,}")
    print("\nFirst 10 Records:")
    df.show(10, truncate=False)

    # -------------------------------------------------------------------------
    # TASK 3: DISPLAY HASHTAG RECORDS
    # -------------------------------------------------------------------------
    print_separator("TASK 3: DISPLAYING HASHTAG RECORDS")
    print("Sample Hashtag Records (First 10 rows):")
    df.select("Timestamp", "Platform", "Hashtag", "Region").show(10, truncate=False)

    # -------------------------------------------------------------------------
    # TASK 4: VALIDATE DATASET STRUCTURE
    # -------------------------------------------------------------------------
    print_separator("TASK 4: VALIDATING DATASET STRUCTURE")
    print("DataFrame Schema:")
    df.printSchema()
    
    print(f"Number of Columns : {len(df.columns)}")
    print(f"Number of Records : {total_records:,}")
    print(f"Column Names      : {', '.join(df.columns)}")

    # -------------------------------------------------------------------------
    # TASK 5: GROUP HASHTAGS
    # -------------------------------------------------------------------------
    print_separator("TASK 5: GROUPING HASHTAGS")
    hashtag_grouped = df.groupBy("Hashtag") \
        .count() \
        .orderBy(desc("count"))
    
    print("Hashtag Occurrences Grouped (Top 15):")
    hashtag_grouped.show(15, truncate=False)

    # -------------------------------------------------------------------------
    # TASK 6: COUNT HASHTAG OCCURRENCES (TOP 10 FREQUENT)
    # -------------------------------------------------------------------------
    print_separator("TASK 6: COUNTING HASHTAG OCCURRENCES")
    top_10_df = hashtag_grouped.limit(10)
    print("Top 10 Most Frequent Hashtags:")
    top_10_df.show(10, truncate=False)

    # -------------------------------------------------------------------------
    # TASK 7: SORT HASHTAGS BY POPULARITY WITH RANK
    # -------------------------------------------------------------------------
    print_separator("TASK 7: SORTING HASHTAGS BY POPULARITY")
    w_rank = Window.orderBy(desc("count"))
    ranked_hashtags = hashtag_grouped.withColumn("Rank", row_number().over(w_rank)) \
        .select("Rank", "Hashtag", col("count").alias("Occurrence_Count"))
        
    print("Hashtags Sorted by Popularity with Dynamic Rank:")
    ranked_hashtags.show(15, truncate=False)

    # -------------------------------------------------------------------------
    # TASK 8: IDENTIFY TOP TRENDING HASHTAGS (TOP 5)
    # -------------------------------------------------------------------------
    print_separator("TASK 8: IDENTIFYING TOP TRENDING HASHTAGS")
    top_5_df = ranked_hashtags.limit(5)
    print("Top 5 Trending Hashtags:")
    top_5_df.show(truncate=False)
    
    top_1_row = ranked_hashtags.first()
    top_hashtag = top_1_row["Hashtag"]
    top_count = top_1_row["Occurrence_Count"]
    print(f"[>>>] Top Trending Hashtag: {top_hashtag} with {top_count} posts")

    # -------------------------------------------------------------------------
    # SUPPLEMENTARY 1: TOP 3 TRENDING HASHTAGS
    # -------------------------------------------------------------------------
    print_separator("SUPPLEMENTARY 1: TOP 3 TRENDING HASHTAGS")
    top_3_df = ranked_hashtags.limit(3)
    top_3_df.show(truncate=False)
    
    print(f"Top Trending Hashtag:\n{top_hashtag} (Total Occurrences: {top_count})\n")

    # -------------------------------------------------------------------------
    # SUPPLEMENTARY 2: DAILY TREND COMPARISON
    # -------------------------------------------------------------------------
    print_separator("SUPPLEMENTARY 2: DAILY TREND COMPARISON")
    print("Comparing Hashtag Trends Across Multiple Days...")
    
    daily_hashtag = df.groupBy("Timestamp", "Hashtag") \
        .count() \
        .orderBy("Timestamp", desc("count"))
        
    print("\nDaily Hashtag Counts (Sample 12 records):")
    daily_hashtag.show(12, truncate=False)
    
    # Identify top trending hashtag for each distinct day using Window
    w_daily = Window.partitionBy("Timestamp").orderBy(desc("count"))
    daily_top = daily_hashtag.withColumn("rn", row_number().over(w_daily)) \
        .filter(col("rn") == 1) \
        .select("Timestamp", col("Hashtag").alias("Daily_Top_Hashtag"), col("count").alias("Daily_Count")) \
        .orderBy("Timestamp")
        
    print("\nMost Popular Hashtag Per Day:")
    daily_top.show(truncate=False)

    # -------------------------------------------------------------------------
    # SUPPLEMENTARY 3: REGIONAL HASHTAG ANALYSIS
    # -------------------------------------------------------------------------
    print_separator("SUPPLEMENTARY 3: REGIONAL HASHTAG ANALYSIS")
    
    # Total posts per region
    region_totals = df.groupBy("Region") \
        .agg(count("*").alias("Total_Posts")) \
        .orderBy(desc("Total_Posts"))
        
    print("Total Posts Per Region:")
    region_totals.show(truncate=False)
    
    # Top hashtag per region
    region_hashtag = df.groupBy("Region", "Hashtag") \
        .count()
        
    w_region = Window.partitionBy("Region").orderBy(desc("count"))
    top_by_region = region_hashtag.withColumn("rn", row_number().over(w_region)) \
        .filter(col("rn") == 1) \
        .select("Region", col("Hashtag").alias("Top_Hashtag"), col("count").alias("Post_Count")) \
        .orderBy(desc("Post_Count"))
        
    print("Top Trending Hashtag Per Region:")
    top_by_region.show(truncate=False)

    # -------------------------------------------------------------------------
    # TASK 10 & SUPPLEMENTARY 4: USER INTEREST & HASHTAG CATEGORIES
    # -------------------------------------------------------------------------
    print_separator("TASK 10 & SUPPLEMENTARY 4: USER INTEREST & HASHTAG CATEGORIES")
    
    tech_tags = ["#AI", "#MachineLearning", "#CloudComputing", "#CyberSecurity", "#DataScience", "#Tech"]
    sports_tags = ["#Cricket", "#Football", "#FIFA", "#IPL", "#Sports", "#Tennis"]
    ent_tags = ["#Movies", "#Music", "#Netflix", "#Bollywood", "#Hollywood", "#Gaming"]
    
    df_categorized = df.withColumn(
        "Category",
        when(col("Hashtag").isin(tech_tags), "Technology")
        .when(col("Hashtag").isin(sports_tags), "Sports")
        .when(col("Hashtag").isin(ent_tags), "Entertainment")
        .otherwise("General")
    )
    
    category_summary = df_categorized.groupBy("Category") \
        .agg(count("*").alias("Number_of_Posts")) \
        .orderBy(desc("Number_of_Posts"))
        
    print("User Interest Distribution by Category:")
    category_summary.show(truncate=False)
    
    top_category_row = category_summary.first()
    top_category = top_category_row["Category"]
    top_cat_posts = top_category_row["Number_of_Posts"]
    print(f"[>>>] Most Popular Category: {top_category} with {top_cat_posts} posts")

    # Platform distribution
    platform_summary = df.groupBy("Platform") \
        .agg(count("*").alias("Total_Posts")) \
        .orderBy(desc("Total_Posts"))
        
    print("\nPlatform Distribution:")
    platform_summary.show(truncate=False)

    # -------------------------------------------------------------------------
    # SUPPLEMENTARY 5: TREND VISUALIZATION (BAR CHART)
    # -------------------------------------------------------------------------
    print_separator("SUPPLEMENTARY 5: TREND VISUALIZATION")
    print("Creating Matplotlib Bar Chart for Top 10 Trending Hashtags...")
    
    top_10_pd = top_10_df.toPandas()
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(top_10_pd["Hashtag"], top_10_pd["count"], color="#2b5c8f", edgecolor="#1a365d")
    
    # Add numerical count label on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height + 1, f"{int(height)}", ha="center", va="bottom", fontsize=10, fontweight="bold")
        
    plt.title("Top 10 Trending Hashtags - TrendPulse Analytics", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Hashtag", fontsize=11, labelpad=10)
    plt.ylabel("Number of Occurrences", fontsize=11, labelpad=10)
    plt.xticks(rotation=40, ha="right", fontsize=10)
    plt.ylim(0, top_count + 12)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Chart successfully saved to: {chart_path}")

    # -------------------------------------------------------------------------
    # BUSINESS RECOMMENDATIONS
    # -------------------------------------------------------------------------
    print_separator("BUSINESS RECOMMENDATIONS")
    print("[DISCLAIMER]: Educational analysis based on generated/sample social media data.\n")
    print("1. Campaign Targeting   : Allocate top-tier marketing budgets toward Technology and Sports hashtags.")
    print("2. Platform Strategy    : Cross-post top tech trends on LinkedIn and fan-driven sports topics on Twitter/X.")
    print("3. Emerging Topics      : Monitor real-time daily trend shifts to detect breakout virality early.")
    print("4. Geo-Targeted Content : Tailor campaigns based on regional preferences (e.g. cricket in Asia-Pacific).")
    print("5. Community Engagement : Create branded interactive polls around #AI, #Cricket, and #Netflix.")

    # -------------------------------------------------------------------------
    # FINAL REPORT GENERATION (.txt)
    # -------------------------------------------------------------------------
    print_separator("FINAL SOCIAL MEDIA TREND ANALYSIS REPORT")
    
    unique_hashtags_count = hashtag_grouped.count()
    top_10_rows = top_10_df.collect()
    top_10_str = f"{'Rank':<6} | {'Hashtag':<20} | {'Occurrences':<12}\n" + "-" * 42 + "\n"
    for idx, r in enumerate(top_10_rows, 1):
        top_10_str += f"{idx:<6} | {r['Hashtag']:<20} | {r['count']:<12}\n"
        
    top_5_rows = top_5_df.collect()
    top_5_str = f"{'Rank':<6} | {'Hashtag':<20} | {'Occurrences':<12}\n" + "-" * 42 + "\n"
    for r in top_5_rows:
        top_5_str += f"{r['Rank']:<6} | {r['Hashtag']:<20} | {r['Occurrence_Count']:<12}\n"

    top_3_rows = top_3_df.collect()
    top_3_str = f"{'Rank':<6} | {'Hashtag':<20} | {'Occurrences':<12}\n" + "-" * 42 + "\n"
    for r in top_3_rows:
        top_3_str += f"{r['Rank']:<6} | {r['Hashtag']:<20} | {r['Occurrence_Count']:<12}\n"

    daily_rows = daily_top.collect()
    daily_str = f"{'Date':<12} | {'Daily Top Hashtag':<20} | {'Post Count':<12}\n" + "-" * 48 + "\n"
    for r in daily_rows:
        daily_str += f"{str(r['Timestamp']):<12} | {r['Daily_Top_Hashtag']:<20} | {r['Daily_Count']:<12}\n"

    reg_rows = top_by_region.collect()
    reg_str = f"{'Region':<16} | {'Top Hashtag':<20} | {'Post Count':<12}\n" + "-" * 52 + "\n"
    for r in reg_rows:
        reg_str += f"{r['Region']:<16} | {r['Top_Hashtag']:<20} | {r['Post_Count']:<12}\n"

    cat_rows = category_summary.collect()
    cat_str = f"{'Category':<16} | {'Number of Posts':<16}\n" + "-" * 34 + "\n"
    for r in cat_rows:
        cat_str += f"{r['Category']:<16} | {r['Number_of_Posts']:<16}\n"

    plat_rows = platform_summary.collect()
    plat_str = f"{'Platform':<16} | {'Total Posts':<16}\n" + "-" * 34 + "\n"
    for r in plat_rows:
        plat_str += f"{r['Platform']:<16} | {r['Total_Posts']:<16}\n"

    report_text = f"""========================================================================================
            TRENDPULSE SOCIAL MEDIA TREND DETECTION REPORT
========================================================================================
1. DATASET DETAILS:
   - Source File                : social_media_hashtags.csv
   - Total Records              : {total_records:,}
   - Schema                     : Timestamp (string), Platform (string), Hashtag (string), Region (string)
   - Data Nature                : Generated / Sample dataset for educational evaluation

2. TOTAL RECORDS:
   - Total Monitored Posts      : {total_records:,}

3. UNIQUE HASHTAGS:
   - Total Distinct Hashtags    : {unique_hashtags_count}

4. PLATFORM DISTRIBUTION:
{plat_str.strip()}

5. REGION DISTRIBUTION:
{reg_str.strip()}

6. HASHTAG FREQUENCY ANALYSIS:
   - Evaluated across all monitored interactions with dynamic grouping and frequency sorting.

7. TOP 10 HASHTAGS:
{top_10_str.strip()}

8. TOP 5 TRENDING HASHTAGS:
{top_5_str.strip()}

9. TOP 3 TRENDING HASHTAGS:
{top_3_str.strip()}
   * Top Trending Hashtag       : {top_hashtag} ({top_count} occurrences)

10. DAILY TREND ANALYSIS:
{daily_str.strip()}

11. REGIONAL ANALYSIS:
{reg_str.strip()}

12. CATEGORY ANALYSIS:
{cat_str.strip()}
   * Leading Category           : {top_category} ({top_cat_posts} posts)

13. USER INTEREST ANALYSIS:
   - User attention is primarily concentrated in cutting-edge Technology topics (#AI, #MachineLearning),
     followed by high-energy Sports discussions (#Cricket, #Football) and Entertainment streaming (#Netflix).

14. BUSINESS RECOMMENDATIONS:
   * DISCLAIMER: Educational analysis based on generated/sample social media data.
   - Allocate promotional spending to high-affinity topics (#AI, #Cricket, #MachineLearning).
   - Leverage multi-platform distribution based on user demographics (Tech -> LinkedIn, Sports -> Twitter/X).
   - Monitor daily breakout hashtags to optimize real-time digital marketing responses.

15. CONCLUSION:
   PySpark DataFrame transformations, grouping, and window functions offer massive scalability
   and low latency for parsing unstructured social interaction streams and extracting actionable trends.
========================================================================================
"""
    print(report_text)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text.strip() + "\n")
    print(f"[OK] Trend analysis report successfully saved to: {report_path}")

    # Stop Spark Session
    spark.stop()
    print("[*] Spark Session stopped successfully.")

if __name__ == "__main__":
    main()
