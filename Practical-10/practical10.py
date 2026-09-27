"""
========================================================================================
BDA Practical 10: Scalable K-Means Clustering on Customer Segmentation Data
                  using Apache Spark MLlib (Parallel K-Means)
Scenario: RetailEdge Analytics - Large-Scale Customer Segmentation Engine
Student Practical Implementation (PySpark MLlib + scikit-learn + Matplotlib)
========================================================================================
"""

import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Headless backend for automated/terminal environments
import matplotlib.pyplot as plt

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, sum as spark_sum, count as spark_count, avg as spark_avg,
    max as spark_max, min as spark_min, round as spark_round,
    datediff, to_date, lit
)
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans, BisectingKMeans
from sklearn.cluster import KMeans as SklearnKMeans

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
        .appName("Customer-Segmentation-KMeans") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
        
    # Suppress verbose internal Spark INFO logs for clean terminal screenshots
    spark.sparkContext.setLogLevel("ERROR")
    
    print(f"Spark Version          : {spark.version}")
    print(f"Spark Application Name : {spark.sparkContext.appName}")
    print(f"Master URL             : {spark.sparkContext.master}")

    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "customer_transactions.csv")
    elbow_chart_path = os.path.join(base_dir, "elbow_curve.png")
    cluster_chart_path = os.path.join(base_dir, "cluster_visualization.png")
    report_path = os.path.join(base_dir, "kmeans_report.txt")

    # -------------------------------------------------------------------------
    # TASK 2: LOAD CUSTOMER TRANSACTION DATASET
    # -------------------------------------------------------------------------
    print_separator("TASK 2: LOADING CUSTOMER TRANSACTION DATASET")
    print(f"Dataset Path : {dataset_path}")
    
    df_raw = spark.read.csv(
        dataset_path,
        header=True,
        inferSchema=True
    )
    print("Dataset loaded successfully.")
    
    total_txns = df_raw.count()
    print(f"Total number of transaction records: {total_txns:,}")
    print("\nFirst 10 Transaction Records:")
    df_raw.show(10, truncate=False)

    # -------------------------------------------------------------------------
    # TASK 3: DISPLAY DATASET SCHEMA
    # -------------------------------------------------------------------------
    print_separator("TASK 3: DATASET SCHEMA AND STRUCTURE")
    print("DataFrame Schema:")
    df_raw.printSchema()
    
    print(f"Number of Records : {total_txns:,}")
    print(f"Number of Columns : {len(df_raw.columns)}")
    print(f"Column Names      : {', '.join(df_raw.columns)}")

    # -------------------------------------------------------------------------
    # TASK 4: DATA PREPROCESSING
    # -------------------------------------------------------------------------
    print_separator("TASK 4: DATA PREPROCESSING")
    
    # Cast transaction_date to DateType
    df_clean = df_raw.withColumn("transaction_date", to_date(col("transaction_date"), "yyyy-MM-dd"))
    
    # Filter nulls or invalid negative values if any
    df_clean = df_clean.filter(
        col("customer_id").isNotNull() &
        col("transaction_id").isNotNull() &
        (col("amount") > 0) &
        (col("quantity") > 0)
    ).dropDuplicates(["transaction_id"])
    
    valid_txns = df_clean.count()
    dropped_txns = total_txns - valid_txns
    
    print(f"1. Valid Transactions After Cleaning : {valid_txns:,}")
    print(f"2. Dropped / Invalid Records          : {dropped_txns}")
    print(f"3. Null Check Status                  : All critical columns verified NOT NULL")
    print(f"4. Duplicate Check Status             : Unique transaction IDs ensured")

    # -------------------------------------------------------------------------
    # TASK 5: CUSTOMER FEATURE EXTRACTION
    # -------------------------------------------------------------------------
    print_separator("TASK 5: CUSTOMER FEATURE EXTRACTION")
    
    # Identify latest transaction date in dataset as reference date for Recency
    max_date_row = df_clean.agg(spark_max("transaction_date").alias("max_date")).first()
    reference_date = max_date_row["max_date"]
    print(f"Reference Dataset Date for Recency: {reference_date}")
    
    customer_features = df_clean.groupBy("customer_id").agg(
        spark_round(spark_sum("amount"), 2).alias("total_spend"),
        spark_count("transaction_id").alias("purchase_frequency"),
        spark_round(spark_avg("amount"), 2).alias("average_basket_size"),
        datediff(lit(reference_date), spark_max("transaction_date")).alias("recency")
    ).orderBy("customer_id")
    
    total_customers = customer_features.count()
    print(f"Total Unique Customers Extracted: {total_customers:,}")
    print("\nFirst 10 Customer Feature Records:")
    customer_features.show(10, truncate=False)

    # -------------------------------------------------------------------------
    # TASK 6: FEATURE VECTOR ASSEMBLY
    # -------------------------------------------------------------------------
    print_separator("TASK 6: FEATURE VECTOR ASSEMBLY")
    
    feature_cols = ["total_spend", "purchase_frequency", "average_basket_size", "recency"]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    assembled_df = assembler.transform(customer_features)
    
    print("Features assembled into Vector format [total_spend, purchase_frequency, average_basket_size, recency]:")
    assembled_df.select("customer_id", "features").show(10, truncate=False)

    # -------------------------------------------------------------------------
    # TASK 7: FEATURE SCALING USING STANDARDSCALER
    # -------------------------------------------------------------------------
    print_separator("TASK 7: FEATURE SCALING USING STANDARDSCALER")
    print("Explanation: Features like total_spend have much larger numerical scales than purchase_frequency.")
    print("StandardScaler normalizes each feature to mean = 0, std = 1 to prevent distance domination.\n")
    
    scaler = StandardScaler(inputCol="features", outputCol="scaledFeatures", withStd=True, withMean=True)
    scaler_model = scaler.fit(assembled_df)
    scaled_df = scaler_model.transform(assembled_df).cache()
    
    print("Sample Normalized (Scaled) Features:")
    scaled_df.select("customer_id", "scaledFeatures").show(10, truncate=False)

    # -------------------------------------------------------------------------
    # TASK 8: SPARK MLlib PARALLEL K-MEANS CLUSTERING (k=5)
    # -------------------------------------------------------------------------
    print_separator("TASK 8: SPARK MLlib PARALLEL K-MEANS CLUSTERING")
    
    start_time_spark = time.time()
    kmeans = KMeans(featuresCol="scaledFeatures", predictionCol="prediction", k=5, seed=42)
    kmeans_model = kmeans.fit(scaled_df)
    spark_kmeans_time = time.time() - start_time_spark
    
    cluster_centers = kmeans_model.clusterCenters()
    print(f"Number of Clusters (k)  : {len(cluster_centers)}")
    print(f"Model Training Time     : {spark_kmeans_time:.4f} seconds")
    print("\nStandardized Cluster Centers:")
    for idx, center in enumerate(cluster_centers):
        formatted_center = [round(float(c), 4) for c in center]
        print(f"Cluster {idx} Center: {formatted_center}")

    # -------------------------------------------------------------------------
    # TASK 9: CLUSTERING QUALITY USING WSSSE
    # -------------------------------------------------------------------------
    print_separator("TASK 9: CLUSTERING QUALITY USING WSSSE")
    
    wssse_k5 = kmeans_model.summary.trainingCost
    print(f"Within Set Sum of Squared Errors (WSSSE) for k=5: {wssse_k5:.4f}")
    print("\nExplanation:")
    print("WSSSE measures internal cluster cohesion. Lower values signify tighter, more cohesive clusters.")
    print("However, increasing k naturally decreases WSSSE, so it must be evaluated alongside the Elbow Method.")

    # -------------------------------------------------------------------------
    # TASK 10: CUSTOMER CLUSTER ASSIGNMENT
    # -------------------------------------------------------------------------
    print_separator("TASK 10: CUSTOMER CLUSTER ASSIGNMENT")
    
    predictions = kmeans_model.transform(scaled_df)
    
    print("First 10 Customer Records with Cluster Predictions:")
    predictions.select("customer_id", "total_spend", "purchase_frequency", "average_basket_size", "recency", "prediction") \
        .show(10, truncate=False)
        
    cluster_counts = predictions.groupBy("prediction") \
        .count() \
        .orderBy("prediction")
        
    print("Customer Distribution Across Clusters:")
    cluster_counts.show(truncate=False)

    # -------------------------------------------------------------------------
    # TASK 11: CLUSTER CENTERS AND SEGMENT SUMMARY
    # -------------------------------------------------------------------------
    print_separator("TASK 11: CLUSTER CENTERS AND SEGMENT SUMMARY")
    print("Note: Cluster centers in Task 8 were in standardized Z-score space.")
    print("Below is the practical summary computed on ORIGINAL feature values ($ and days):\n")
    
    segment_summary = predictions.groupBy("prediction").agg(
        spark_round(spark_avg("total_spend"), 2).alias("Avg_Total_Spend"),
        spark_round(spark_avg("purchase_frequency"), 2).alias("Avg_Frequency"),
        spark_round(spark_avg("average_basket_size"), 2).alias("Avg_Basket_Size"),
        spark_round(spark_avg("recency"), 2).alias("Avg_Recency_Days"),
        spark_count("customer_id").alias("Customer_Count")
    ).orderBy("prediction")
    
    segment_summary.show(truncate=False)

    # -------------------------------------------------------------------------
    # TASK 12: CUSTOMER SEGMENT INTERPRETATION
    # -------------------------------------------------------------------------
    print_separator("TASK 12: CUSTOMER SEGMENT INTERPRETATION")
    
    summary_data = segment_summary.collect()
    segment_profiles = {}
    
    for row in summary_data:
        c_id = row["prediction"]
        spend = row["Avg_Total_Spend"]
        freq = row["Avg_Frequency"]
        rec = row["Avg_Recency_Days"]
        count_c = row["Customer_Count"]
        
        # Data-driven segment characterization
        if spend > 250 and freq >= 18:
            profile = "VIP / High-Value Frequent Shoppers (Top Revenue Driver)"
            strategy = "Exclusive VIP perks, early access, personalized concierge service."
        elif freq >= 14 and rec <= 25:
            profile = "Loyal / Regular Customers (Active & Consistent)"
            strategy = "Product recommendations, points-based loyalty rewards."
        elif rec > 50 and freq <= 8:
            profile = "At-Risk / Lapsed Customers (High Recency, Low Activity)"
            strategy = "Win-back discounts, re-engagement emails, churn prevention."
        elif spend < 60 and freq <= 5:
            profile = "Budget / Occasional Shoppers (Low Basket, Low Frequency)"
            strategy = "Bundle promotions, free shipping thresholds, discount coupons."
        else:
            profile = "Moderate Value / Selective Buyers"
            strategy = "Cross-sell campaigns, seasonal notifications, targeted newsletters."
            
        segment_profiles[c_id] = (profile, strategy)
        print(f"Cluster {c_id} ({count_c} customers):")
        print(f"   Averages : Spend: ${spend:.2f} | Frequency: {freq:.1f} orders | Recency: {rec:.1f} days")
        print(f"   Profile  : {profile}")
        print(f"   Strategy : {strategy}\n")

    # -------------------------------------------------------------------------
    # TASK 13: ELBOW METHOD (k = 3, 4, 5, 6, 7)
    # -------------------------------------------------------------------------
    print_separator("TASK 13: ELBOW METHOD")
    print("Evaluating WSSSE across k = 3, 4, 5, 6, 7 to detect the optimal cluster elbow...")
    
    k_values = [3, 4, 5, 6, 7]
    wssse_values = []
    
    for k_val in k_values:
        km_test = KMeans(featuresCol="scaledFeatures", k=k_val, seed=42)
        km_model_test = km_test.fit(scaled_df)
        cost = km_model_test.summary.trainingCost
        wssse_values.append(cost)
        print(f"[*] k = {k_val:<2} | WSSSE = {cost:.4f}")

    # Plot Elbow Curve
    plt.figure(figsize=(8, 5))
    plt.plot(k_values, wssse_values, 'bo-', linewidth=2, markersize=8)
    plt.title("Elbow Method For Optimal k - RetailEdge Analytics", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Number of Clusters (k)", fontsize=11, labelpad=8)
    plt.ylabel("Within Set Sum of Squared Errors (WSSSE)", fontsize=11, labelpad=8)
    plt.xticks(k_values)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(elbow_chart_path, dpi=300)
    plt.close()
    print(f"\nElbow curve successfully saved to: {elbow_chart_path}")

    # -------------------------------------------------------------------------
    # TASK 14: COMPARISON OF K=3, K=5 AND K=7
    # -------------------------------------------------------------------------
    print_separator("TASK 14: COMPARISON OF K=3, K=5 AND K=7")
    idx_3 = k_values.index(3)
    idx_5 = k_values.index(5)
    idx_7 = k_values.index(7)
    
    print(f"K = 3 | WSSSE = {wssse_values[idx_3]:.4f}")
    print(f"K = 5 | WSSSE = {wssse_values[idx_5]:.4f}")
    print(f"K = 7 | WSSSE = {wssse_values[idx_7]:.4f}")
    
    reduction_3_to_5 = ((wssse_values[idx_3] - wssse_values[idx_5]) / wssse_values[idx_3]) * 100
    reduction_5_to_7 = ((wssse_values[idx_5] - wssse_values[idx_7]) / wssse_values[idx_5]) * 100
    
    print(f"\nWSSSE Reduction (k=3 to k=5): {reduction_3_to_5:.2f}% (Significant cohesion gain)")
    print(f"WSSSE Reduction (k=5 to k=7): {reduction_5_to_7:.2f}% (Diminishing returns)")
    print("Observation: k = 5 provides a strong balance between mathematical cohesion and business interpretability.")

    # -------------------------------------------------------------------------
    # TASK 15: BISECTING K-MEANS
    # -------------------------------------------------------------------------
    print_separator("TASK 15: BISECTING K-MEANS")
    print("Bisecting K-Means is a hierarchical clustering algorithm that recursively splits clusters.\n")
    
    bkm = BisectingKMeans(featuresCol="scaledFeatures", k=5, seed=42)
    bkm_model = bkm.fit(scaled_df)
    bkm_cost = bkm_model.summary.trainingCost
    
    print(f"Standard K-Means (k=5) WSSSE  : {wssse_k5:.4f}")
    print(f"Bisecting K-Means (k=5) WSSSE : {bkm_cost:.4f}")

    # -------------------------------------------------------------------------
    # TASK 16: SINGLE-NODE VS SPARK K-MEANS
    # -------------------------------------------------------------------------
    print_separator("TASK 16: SINGLE-NODE VS SPARK K-MEANS")
    
    # Collect scaled features into numpy array for sklearn
    pdf = scaled_df.select("scaledFeatures").toPandas()
    X_scaled = np.array([x.toArray() for x in pdf["scaledFeatures"]])
    
    # Sklearn Execution
    start_time_sk = time.time()
    sk_km = SklearnKMeans(n_clusters=5, random_state=42, n_init=10)
    sk_km.fit(X_scaled)
    sklearn_time = time.time() - start_time_sk
    
    print(f"{'Method':<25} | {'Execution Time':<18} | {'Number of Clusters'}")
    print("-" * 62)
    print(f"{'Scikit-learn K-Means':<25} | {sklearn_time:<15.4f} s | 5")
    print(f"{'Spark MLlib K-Means':<25} | {spark_kmeans_time:<15.4f} s | 5")
    print("\nArchitectural Comparison:")
    print("- Scikit-learn runs in-memory on a single CPU core, offering lower overhead on small local datasets.")
    print("- Spark MLlib distributes data and distance calculations across worker nodes (RDD/DataFrame partitions),")
    print("  enabling massive horizontal scalability to tens of millions of records where single-node memory fails.")

    # -------------------------------------------------------------------------
    # TASK 17: CLUSTER VISUALIZATION
    # -------------------------------------------------------------------------
    print_separator("TASK 17: CLUSTER VISUALIZATION")
    print("Creating 2D Customer Cluster Scatter Plot using Matplotlib...")
    
    pred_pd = predictions.select("total_spend", "purchase_frequency", "prediction").toPandas()
    
    plt.figure(figsize=(10, 6))
    colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231']
    
    for c_id in range(5):
        subset = pred_pd[pred_pd["prediction"] == c_id]
        plt.scatter(
            subset["purchase_frequency"],
            subset["total_spend"],
            c=colors[c_id],
            label=f"Cluster {c_id}",
            alpha=0.6,
            edgecolors='w',
            s=50
        )
        
    # Plot original scale centers
    orig_centers = segment_summary.select("prediction", "Avg_Total_Spend", "Avg_Frequency").toPandas()
    for _, row in orig_centers.iterrows():
        plt.scatter(
            row["Avg_Frequency"],
            row["Avg_Total_Spend"],
            c='black',
            marker='X',
            s=200,
            edgecolors='white',
            linewidths=2
        )
        
    plt.title("Customer Segments - Purchase Frequency vs Total Spend", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Purchase Frequency (Number of Transactions)", fontsize=11, labelpad=10)
    plt.ylabel("Total Spend ($)", fontsize=11, labelpad=10)
    plt.legend(title="Customer Clusters", loc="upper left")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(cluster_chart_path, dpi=300)
    plt.close()
    print(f"Cluster visualization successfully saved to: {cluster_chart_path}")

    # -------------------------------------------------------------------------
    # TASK 18: FINAL K-MEANS PERFORMANCE REPORT
    # -------------------------------------------------------------------------
    print_separator("TASK 18: FINAL K-MEANS PERFORMANCE REPORT")
    
    summary_table_str = f"{'Cluster':<8} | {'Customers':<10} | {'Avg Spend ($)':<14} | {'Avg Frequency':<14} | {'Avg Basket ($)':<15} | {'Avg Recency (Days)':<20}\n"
    summary_table_str += "-" * 90 + "\n"
    for r in summary_data:
        summary_table_str += f"{r['prediction']:<8} | {r['Customer_Count']:<10} | {r['Avg_Total_Spend']:<14.2f} | {r['Avg_Frequency']:<14.2f} | {r['Avg_Basket_Size']:<15.2f} | {r['Avg_Recency_Days']:<20.2f}\n"

    report_text = f"""========================================================================================
            RETAILEDGE ANALYTICS - SCALABLE CUSTOMER SEGMENTATION REPORT
========================================================================================
1. DATASET DETAILS:
   - Source File                : customer_transactions.csv
   - Total Transactions         : {valid_txns:,}
   - Total Segmented Customers  : {total_customers:,}
   - Evaluation Nature          : Generated / Sample dataset for educational evaluation

2. FEATURE DEFINITIONS:
   - Total Spend ($)            : Cumulative expenditure across all transactions (sum(amount))
   - Purchase Frequency         : Total number of completed purchases (count(transaction_id))
   - Average Basket Size ($)    : Mean transaction order value (avg(amount))
   - Recency (Days)             : Days elapsed between reference date and latest customer purchase

3. PREPROCESSING SUMMARY:
   - Null and negative records filtered; dates cast to standard ISO format.
   - Clean transaction count    : {valid_txns:,}

4. FEATURE SCALING (StandardScaler):
   - Applied StandardScaler (mean=0, std=1) across all 4 customer dimensions.
   - Prevents total_spend ($10-$1500) from overpowering frequency (1-35).

5. SPARK MLlib K-MEANS RESULTS (k = 5):
   - Number of Clusters (k)     : 5
   - Seed                       : 42
   - WSSSE Cost                 : {wssse_k5:.4f}
   - Training Duration          : {spark_kmeans_time:.4f} seconds

6. CLUSTER SIZES & SEGMENT SUMMARIES (ORIGINAL SPACE):
{summary_table_str.strip()}

7. CUSTOMER SEGMENT INTERPRETATION:
"""
    for c_id, (prof, strat) in segment_profiles.items():
        report_text += f"   - Cluster {c_id}: {prof}\n     Strategy: {strat}\n"

    report_text += f"""
8. ELBOW METHOD ANALYSIS (k = 3 to 7):
   - k=3 : WSSSE = {wssse_values[idx_3]:.4f}
   - k=4 : WSSSE = {wssse_values[1]:.4f}
   - k=5 : WSSSE = {wssse_values[idx_5]:.4f}
   - k=6 : WSSSE = {wssse_values[3]:.4f}
   - k=7 : WSSSE = {wssse_values[idx_7]:.4f}
   * Elbow Observation: Significant loss reduction occurs up to k=5 ({reduction_3_to_5:.1f}% drop from k=3);
     subsequent drops taper off ({reduction_5_to_7:.1f}%), confirming k=5 as optimal.

9. BISECTING K-MEANS COMPARISON:
   - Standard K-Means WSSSE     : {wssse_k5:.4f}
   - Bisecting K-Means WSSSE    : {bkm_cost:.4f}

10. EXECUTION BENCHMARK (Single-Node vs Distributed):
   - Scikit-learn K-Means       : {sklearn_time:.4f} seconds
   - Spark MLlib K-Means        : {spark_kmeans_time:.4f} seconds
   * Takeaway: Single-node sklearn executes quickly for small in-memory datasets due to minimal overhead.
     Spark MLlib shines when datasets scale to millions of rows across clustered worker nodes.

11. CONCLUSION:
   Parallel K-Means using Apache Spark MLlib enables robust, scalable customer segmentation
   that translates transactional big data directly into actionable marketing strategies.
========================================================================================
"""
    print(report_text)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text.strip() + "\n")
    print(f"[OK] Customer segmentation report successfully saved to: {report_path}")

    # Stop Spark Session
    spark.stop()
    print("[*] Spark Session stopped successfully.")

if __name__ == "__main__":
    main()
