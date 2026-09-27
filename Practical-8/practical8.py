"""
========================================================================================
BDA Practical 8: Stock Market Analytics Using Window-Based Analysis
Company Scenario: FinEdge Securities Ltd. - Financial Analytics Engine
Student Practical Implementation (PySpark + Matplotlib)
========================================================================================
"""

import os
import matplotlib
matplotlib.use('Agg')  # Headless backend for terminal / automated execution
import matplotlib.pyplot as plt

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, avg, max as spark_max, min as spark_min, count, round as spark_round,
    lag, row_number, stddev, when
)
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
        .appName("Stock-Market-Analytics") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
        
    # Suppress internal Spark INFO logs for clean terminal output and screenshots
    spark.sparkContext.setLogLevel("ERROR")
    
    print(f"Spark Version   : {spark.version}")
    print(f"Spark App Name  : {spark.sparkContext.appName}")
    print(f"Master URL      : {spark.sparkContext.master}")

    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "stock_data.csv")
    chart_path = os.path.join(base_dir, "stock_price_trends.png")
    report_path = os.path.join(base_dir, "stock_summary_report.txt")

    # -------------------------------------------------------------------------
    # TASK 2: LOAD STOCK DATASET
    # -------------------------------------------------------------------------
    print_separator("TASK 2: LOADING STOCK DATASET")
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
    # TASK 3: DISPLAYING SCHEMA AND SAMPLE RECORDS
    # -------------------------------------------------------------------------
    print_separator("TASK 3: DISPLAYING SCHEMA AND SAMPLE RECORDS")
    print("DataFrame Schema:")
    df.printSchema()

    # -------------------------------------------------------------------------
    # TASK 4: GROUPING BY STOCK SYMBOL
    # -------------------------------------------------------------------------
    print_separator("TASK 4: GROUPING BY STOCK SYMBOL")
    stock_counts = df.groupBy("Stock") \
        .agg(count("*").alias("Number_of_Records")) \
        .orderBy("Stock")
    stock_counts.show(truncate=False)

    # -------------------------------------------------------------------------
    # TASK 5: AVERAGE STOCK PRICE
    # -------------------------------------------------------------------------
    print_separator("TASK 5: AVERAGE STOCK PRICE")
    avg_price_df = df.groupBy("Stock") \
        .agg(spark_round(avg("Price"), 2).alias("Average_Price")) \
        .orderBy(col("Average_Price").desc())
    avg_price_df.show(truncate=False)

    # -------------------------------------------------------------------------
    # TASK 6: MAXIMUM STOCK PRICE
    # -------------------------------------------------------------------------
    print_separator("TASK 6: MAXIMUM STOCK PRICE")
    max_price_df = df.groupBy("Stock") \
        .agg(spark_round(spark_max("Price"), 2).alias("Maximum_Price")) \
        .orderBy(col("Maximum_Price").desc())
    max_price_df.show(truncate=False)

    # -------------------------------------------------------------------------
    # TASK 7: MINIMUM STOCK PRICE
    # -------------------------------------------------------------------------
    print_separator("TASK 7: MINIMUM STOCK PRICE")
    min_price_df = df.groupBy("Stock") \
        .agg(spark_round(spark_min("Price"), 2).alias("Minimum_Price")) \
        .orderBy(col("Minimum_Price").asc())
    min_price_df.show(truncate=False)

    # -------------------------------------------------------------------------
    # TASK 8: STOCK SUMMARY REPORT
    # -------------------------------------------------------------------------
    print_separator("TASK 8: STOCK SUMMARY REPORT")
    stock_summary = df.groupBy("Stock") \
        .agg(
            count("*").alias("Total_Records"),
            spark_round(avg("Price"), 2).alias("Average_Price"),
            spark_round(spark_min("Price"), 2).alias("Minimum_Price"),
            spark_round(spark_max("Price"), 2).alias("Maximum_Price")
        ) \
        .orderBy("Stock")
    stock_summary.show(truncate=False)

    # -------------------------------------------------------------------------
    # TASK 9: BEST-PERFORMING STOCKS (WINDOW FUNCTIONS: FIRST & LAST PRICE)
    # -------------------------------------------------------------------------
    print_separator("TASK 9: BEST-PERFORMING STOCKS")
    
    # Define Windows to extract earliest and latest stock prices
    w_asc = Window.partitionBy("Stock").orderBy("Timestamp")
    w_desc = Window.partitionBy("Stock").orderBy(col("Timestamp").desc())
    
    first_prices = df.withColumn("rn", row_number().over(w_asc)) \
        .filter(col("rn") == 1) \
        .select(col("Stock"), spark_round(col("Price"), 2).alias("First_Price"))
        
    last_prices = df.withColumn("rn", row_number().over(w_desc)) \
        .filter(col("rn") == 1) \
        .select(col("Stock"), spark_round(col("Price"), 2).alias("Last_Price"))
        
    returns_df = first_prices.join(last_prices, "Stock") \
        .withColumn(
            "Return_Percentage",
            spark_round(((col("Last_Price") - col("First_Price")) / col("First_Price")) * 100, 2)
        ) \
        .orderBy(col("Return_Percentage").desc())
        
    returns_df.show(truncate=False)
    
    best_stock_row = returns_df.first()
    best_stock = best_stock_row["Stock"]
    best_return = best_stock_row["Return_Percentage"]
    print(f"[>>>] Best-Performing Stock: {best_stock} with Return of {best_return:.2f}%")

    # -------------------------------------------------------------------------
    # SUPPLEMENTARY 1: DAILY STOCK RETURNS USING lag()
    # -------------------------------------------------------------------------
    print_separator("SUPPLEMENTARY 1: DAILY STOCK RETURNS")
    print("Using Window: Window.partitionBy('Stock').orderBy('Timestamp') with lag('Price')")
    
    w_daily = Window.partitionBy("Stock").orderBy("Timestamp")
    
    df_daily = df.withColumn("Previous_Price", spark_round(lag("Price", 1).over(w_daily), 2)) \
        .withColumn(
            "Daily_Return_Percentage",
            when(col("Previous_Price").isNull(), 0.0)
            .otherwise(
                spark_round(((col("Price") - col("Previous_Price")) / col("Previous_Price")) * 100, 2)
            )
        ) \
        .orderBy("Stock", "Timestamp")
        
    print("\nSample Daily Returns (First 10 records):")
    df_daily.select("Timestamp", "Stock", "Price", "Previous_Price", "Daily_Return_Percentage") \
        .show(10, truncate=False)

    # -------------------------------------------------------------------------
    # SUPPLEMENTARY 2: TOP-PERFORMING STOCK RANKING
    # -------------------------------------------------------------------------
    print_separator("SUPPLEMENTARY 2: TOP-PERFORMING STOCK")
    print("Ranked Stocks by Cumulative Period Return:")
    returns_df.show(truncate=False)
    print(f"Top-Ranked Stock overall : {best_stock} ({best_return:.2f}%)")

    # -------------------------------------------------------------------------
    # SUPPLEMENTARY 3: MOVING AVERAGE (3-PERIOD WINDOW)
    # -------------------------------------------------------------------------
    print_separator("SUPPLEMENTARY 3: MOVING AVERAGE")
    print("Computing 3-Period Moving Average using rowsBetween(-2, 0)...")
    
    w_ma3 = Window.partitionBy("Stock").orderBy("Timestamp").rowsBetween(-2, 0)
    
    df_ma = df.withColumn(
        "3_Day_Moving_Avg",
        spark_round(avg("Price").over(w_ma3), 2)
    ).orderBy("Stock", "Timestamp")
    
    print("\nSample Moving Average Results (First 10 records):")
    df_ma.select("Timestamp", "Stock", "Price", "3_Day_Moving_Avg") \
        .show(10, truncate=False)

    # -------------------------------------------------------------------------
    # SUPPLEMENTARY 4: STOCK VOLATILITY (stddev OF RETURNS)
    # -------------------------------------------------------------------------
    print_separator("SUPPLEMENTARY 4: STOCK VOLATILITY")
    print("Calculating Volatility as Standard Deviation of Daily Returns...")
    
    volatility_df = df_daily.filter(col("Previous_Price").isNotNull()) \
        .groupBy("Stock") \
        .agg(spark_round(stddev("Daily_Return_Percentage"), 2).alias("Volatility_StdDev")) \
        .orderBy(col("Volatility_StdDev").desc())
        
    volatility_df.show(truncate=False)

    # -------------------------------------------------------------------------
    # TASK 10: MARKET TREND ANALYSIS
    # -------------------------------------------------------------------------
    print_separator("TASK 10: MARKET TREND ANALYSIS")
    
    returns_list = returns_df.collect()
    positive_stocks = [r["Stock"] for r in returns_list if r["Return_Percentage"] > 0]
    negative_stocks = [r["Stock"] for r in returns_list if r["Return_Percentage"] <= 0]
    
    highest_avg_row = avg_price_df.first()
    highest_max_row = max_price_df.first()
    lowest_min_row = min_price_df.first()
    
    print(f"1. Stocks with Positive Cumulative Return : {', '.join(positive_stocks)}")
    print(f"2. Stocks with Negative Cumulative Return : {', '.join(negative_stocks) if negative_stocks else 'None'}")
    print(f"3. Stock with Highest Average Price       : {highest_avg_row['Stock']} (${highest_avg_row['Average_Price']:.2f})")
    print(f"4. Highest Single Stock Price Peak        : {highest_max_row['Stock']} (${highest_max_row['Maximum_Price']:.2f})")
    print(f"5. Lowest Single Stock Price Trough       : {lowest_min_row['Stock']} (${lowest_min_row['Minimum_Price']:.2f})")

    # -------------------------------------------------------------------------
    # TASK 11: INVESTMENT RECOMMENDATIONS
    # -------------------------------------------------------------------------
    print_separator("TASK 11: INVESTMENT RECOMMENDATIONS")
    print("[DISCLAIMER]: Educational analysis only -- not financial advice.\n")
    
    vol_dict = {row["Stock"]: row["Volatility_StdDev"] for row in volatility_df.collect()}
    
    for r in returns_list:
        symbol = r["Stock"]
        ret = r["Return_Percentage"]
        vol = vol_dict.get(symbol, 0.0)
        
        if ret > 10.0 and vol > 2.0:
            profile = "Aggressive Growth (High Return, Elevated Volatility)"
        elif ret > 0.0 and vol <= 2.0:
            profile = "Balanced / Moderate (Steady Positive Return, Low Volatility)"
        else:
            profile = "Defensive / Review (Subdued Return or Higher Fluctuations)"
            
        print(f"[*] {symbol:<5}: Return = {ret:>6.2f}% | Volatility = {vol:>4.2f}% -> Profile: {profile}")

    # -------------------------------------------------------------------------
    # SUPPLEMENTARY 5: VISUALIZATION (MATPLOTLIB)
    # -------------------------------------------------------------------------
    print_separator("SUPPLEMENTARY 5: STOCK PRICE VISUALIZATION")
    print("Generating stock price trends chart using Matplotlib...")
    
    # Collect records sorted by Timestamp for plotting
    plot_df = df.toPandas()
    
    plt.figure(figsize=(11, 6))
    for stock_sym in sorted(plot_df["Stock"].unique()):
        stock_sub = plot_df[plot_df["Stock"] == stock_sym].sort_values("Timestamp")
        plt.plot(stock_sub["Timestamp"], stock_sub["Price"], label=stock_sym, linewidth=2)
        
    plt.title("FinEdge Securities - Stock Market Price Trends", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Date / Timestamp", fontsize=11, labelpad=8)
    plt.ylabel("Stock Price ($)", fontsize=11, labelpad=8)
    plt.xticks(rotation=45, ha='right')
    
    # Format x-ticks: select around 8-10 tick markers so dates don't overlap
    all_dates = sorted(plot_df["Timestamp"].unique())
    step = max(1, len(all_dates) // 8)
    plt.xticks(all_dates[::step])
    
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(title="Stock Symbols", loc="upper left")
    plt.tight_layout()
    
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Chart successfully saved to: {chart_path}")

    # -------------------------------------------------------------------------
    # FINAL STOCK SUMMARY REPORT (.txt)
    # -------------------------------------------------------------------------
    print_separator("FINAL STOCK MARKET ANALYSIS REPORT")
    
    summary_rows = stock_summary.collect()
    summary_table_str = f"{'Stock':<8} | {'Records':<8} | {'Avg Price ($)':<14} | {'Min Price ($)':<14} | {'Max Price ($)':<14}\n"
    summary_table_str += "-" * 70 + "\n"
    for sr in summary_rows:
        summary_table_str += f"{sr['Stock']:<8} | {sr['Total_Records']:<8} | {sr['Average_Price']:<14.2f} | {sr['Minimum_Price']:<14.2f} | {sr['Maximum_Price']:<14.2f}\n"

    returns_table_str = f"{'Stock':<8} | {'First Price ($)':<16} | {'Last Price ($)':<15} | {'Return (%)':<12}\n"
    returns_table_str += "-" * 60 + "\n"
    for rr in returns_list:
        returns_table_str += f"{rr['Stock']:<8} | {rr['First_Price']:<16.2f} | {rr['Last_Price']:<15.2f} | {rr['Return_Percentage']:<12.2f}\n"

    vol_rows = volatility_df.collect()
    vol_table_str = f"{'Stock':<8} | {'Volatility (StdDev %)':<22}\n"
    vol_table_str += "-" * 34 + "\n"
    for vr in vol_rows:
        vol_table_str += f"{vr['Stock']:<8} | {vr['Volatility_StdDev']:<22.2f}\n"

    report_content = f"""========================================================================================
             FINEDGE SECURITIES LTD. - STOCK MARKET ANALYTICS REPORT
========================================================================================
1. DATASET DETAILS:
   - Source File                : stock_data.csv
   - Total Records              : {total_records:,}
   - Schema                     : Timestamp (string), Stock (string), Price (double)
   - Date Range Covered         : {all_dates[0]} to {all_dates[-1]} ({len(all_dates)} trading periods)

2. STOCKS ANALYSED:
   - Evaluated Tickers          : {', '.join(sorted(plot_df['Stock'].unique()))}

3. STOCK PRICE SUMMARY (AVERAGE, MINIMUM, MAXIMUM):
{summary_table_str.strip()}

4. CUMULATIVE STOCK RETURNS (FIRST vs LAST PRICE VIA WINDOW FUNCTIONS):
{returns_table_str.strip()}

5. BEST-PERFORMING STOCK:
   - Symbol                     : {best_stock}
   - Period Return              : {best_return:.2f}%
   - Evaluation Method          : Spark Window partitionBy("Stock") first/last price comparison

6. MOVING AVERAGE ANALYSIS:
   - Method                     : 3-period rolling window rowsBetween(-2, 0)
   - Purpose                    : Smooths out short-term price fluctuations and highlights baseline trend

7. VOLATILITY RESULTS (RISK MEASURE):
{vol_table_str.strip()}

8. MARKET TREND OBSERVATIONS:
   - Dominant Market Momentum   : Positive growth observed across analysed securities
   - Highest Value Security     : {highest_avg_row['Stock']} with Average Price ${highest_avg_row['Average_Price']:.2f}
   - Highest Price Peak         : {highest_max_row['Stock']} peaking at ${highest_max_row['Maximum_Price']:.2f}
   - Lowest Price Floor         : {lowest_min_row['Stock']} at ${lowest_min_row['Minimum_Price']:.2f}

9. EDUCATIONAL INVESTMENT RECOMMENDATIONS:
   * DISCLAIMER: Educational analysis only -- not financial advice.
   - For Growth Investors       : Focus on {best_stock} which exhibited the strongest upward momentum.
   - For Risk-Averse Investors  : Choose stocks with the lowest volatility stddev to minimize drawdown risk.
   - For Value Investors        : Consider securities trading close to their historical moving average baselines.

10. CONCLUSION:
   Window-based analysis in PySpark enables efficient time-series computations (lag, rolling averages,
   cumulative returns) at massive scale without requiring memory-intensive shuffles or external libraries.
========================================================================================
"""
    print(report_content)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content.strip() + "\n")
    print(f"[OK] Stock summary report successfully saved to: {report_path}")

    # Stop Spark Session
    spark.stop()
    print("[*] Spark Session stopped successfully.")

if __name__ == "__main__":
    main()
