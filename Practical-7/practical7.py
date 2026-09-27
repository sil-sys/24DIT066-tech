"""
========================================================================================
BDA Practical 7: Spark Performance Optimization using Caching and Partitioning
Scenario: MovieFlix Technologies - Movie Recommendation Engine Optimization
Student Practical Implementation (PySpark)
========================================================================================
"""

import os
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, round as spark_round
from pyspark.storagelevel import StorageLevel

def print_separator(title=""):
    print("\n" + "=" * 70)
    if title:
        print(f" >>> {title.upper()} <<<")
        print("=" * 70)

def main():
    # -------------------------------------------------------------------------
    # TASK 1: Create Spark Session
    # -------------------------------------------------------------------------
    print_separator("Task 1: Creating Spark Session")
    
    spark = SparkSession.builder \
        .appName("MovieFlix-Performance-Optimization") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
        
    # Suppress verbose INFO logs for clean console output and clear screenshots
    spark.sparkContext.setLogLevel("ERROR")
    
    print(f"[*] Spark Version: {spark.version}")
    print(f"[*] Spark App Name: {spark.sparkContext.appName}")
    print(f"[*] Master URL: {spark.sparkContext.master}")

    # Determine dataset path (works whether run from workspace root or Practical-7 dir)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "ratings.csv")
    report_path = os.path.join(base_dir, "performance_report.txt")

    # -------------------------------------------------------------------------
    # TASK 2: Load ratings dataset into Spark DataFrame
    # -------------------------------------------------------------------------
    print_separator("Task 2: Loading Dataset into DataFrame")
    print(f"[*] Loading CSV data from: {dataset_path}")
    
    df = spark.read.csv(
        dataset_path,
        header=True,
        inferSchema=True
    )
    print("[*] Dataset successfully loaded.")
    print("\nSample Records (First 5 rows):")
    df.show(5)

    # -------------------------------------------------------------------------
    # TASK 3: Display Dataset Schema
    # -------------------------------------------------------------------------
    print_separator("Task 3: Dataset Schema & Data Types")
    print("DataFrame Schema:")
    df.printSchema()

    # -------------------------------------------------------------------------
    # TASK 4: Check Number of Records & Current Number of Partitions
    # -------------------------------------------------------------------------
    print_separator("Task 4: Record Count & Initial Partitions")
    total_records = df.count()
    initial_partitions = df.rdd.getNumPartitions()
    
    print(f"[*] Total Number of Records: {total_records:,}")
    print(f"[*] Initial Partition Count : {initial_partitions}")

    # -------------------------------------------------------------------------
    # TASK 5 & 6: Calculate Average Ratings & Measure Time Before Optimization
    # -------------------------------------------------------------------------
    print_separator("Task 5 & 6: Average Ratings & Execution Time BEFORE Caching")
    
    # Calculate overall average rating
    overall_avg_row = df.agg(avg("rating").alias("overall_avg")).first()
    overall_avg = overall_avg_row["overall_avg"]
    print(f"[*] Overall Average Rating across all movies: {overall_avg:.2f} / 5.00")

    # Measure execution time for complex aggregation before caching
    print("\nComputing movie-wise average ratings (Uncached)...")
    start_time = time.time()
    
    movie_avg_uncached = df.groupBy("movieId") \
        .agg(
            spark_round(avg("rating"), 2).alias("avg_rating"),
            count("rating").alias("total_ratings")
        ) \
        .orderBy(col("total_ratings").desc())
    
    # Force action to compute
    top_movies_before = movie_avg_uncached.take(5)
    time_before_cache = time.time() - start_time
    
    print("\nTop 5 Most Rated Movies (Before Caching):")
    print(f"{'Movie ID':<10} | {'Avg Rating':<12} | {'Total Ratings':<15}")
    print("-" * 42)
    for row in top_movies_before:
        print(f"{row['movieId']:<10} | {row['avg_rating']:<12} | {row['total_ratings']:<15}")
        
    print(f"\n[>>>] Execution Time BEFORE Caching: {time_before_cache:.4f} seconds")

    # -------------------------------------------------------------------------
    # TASK 7 & 8: Apply cache() and Trigger Caching
    # -------------------------------------------------------------------------
    print_separator("Task 7 & 8: Applying cache() and Triggering Caching")
    df.cache()
    print("[*] Applied df.cache() (StorageLevel: MEMORY_AND_DISK_DESER)")
    
    trigger_start = time.time()
    cached_record_count = df.count()
    trigger_time = time.time() - trigger_start
    print(f"[*] Count used to trigger caching: {cached_record_count:,} records")
    print(f"[*] Time taken to populate cache: {trigger_time:.4f} seconds")
    print("[*] DataFrame is now cached in Spark Memory.")

    # -------------------------------------------------------------------------
    # TASK 9 & 10: Recalculate Average Ratings & Measure Time After Caching
    # -------------------------------------------------------------------------
    print_separator("Task 9 & 10: Recalculating Average Ratings AFTER Caching")
    
    start_time = time.time()
    movie_avg_cached = df.groupBy("movieId") \
        .agg(
            spark_round(avg("rating"), 2).alias("avg_rating"),
            count("rating").alias("total_ratings")
        ) \
        .orderBy(col("total_ratings").desc())
        
    top_movies_after = movie_avg_cached.take(5)
    time_after_cache = time.time() - start_time
    
    print("\nTop 5 Most Rated Movies (After Caching):")
    print(f"{'Movie ID':<10} | {'Avg Rating':<12} | {'Total Ratings':<15}")
    print("-" * 42)
    for row in top_movies_after:
        print(f"{row['movieId']:<10} | {row['avg_rating']:<12} | {row['total_ratings']:<15}")
        
    print(f"\n[>>>] Execution Time AFTER Caching : {time_after_cache:.4f} seconds")

    # -------------------------------------------------------------------------
    # TASK 13 (Part 1): Performance Comparison (Before vs After Cache)
    # -------------------------------------------------------------------------
    print_separator("Task 13: Caching Performance Comparison")
    speedup_cache = (time_before_cache / time_after_cache) if time_after_cache > 0 else 1.0
    time_saved_pct = ((time_before_cache - time_after_cache) / time_before_cache) * 100 if time_before_cache > 0 else 0.0
    
    print(f"Execution Time Before Cache : {time_before_cache:.4f} s")
    print(f"Execution Time After Cache  : {time_after_cache:.4f} s")
    print(f"Performance Speedup Factor  : {speedup_cache:.2f}x faster")
    print(f"Time Reduction Percentage   : {time_saved_pct:.2f}%")

    # Free cache before partitioning experiments
    df.unpersist()

    # -------------------------------------------------------------------------
    # TASK 11 & 12: Repartitioning the Dataset (2, 4, 8 Partitions)
    # -------------------------------------------------------------------------
    print_separator("Task 11 & 12: Repartitioning (2, 4, and 8 Partitions)")
    
    # 2 Partitions
    df_2 = df.repartition(2)
    p2_count = df_2.rdd.getNumPartitions()
    start_time = time.time()
    _ = df_2.groupBy("movieId").agg(avg("rating")).count()
    time_p2 = time.time() - start_time
    print(f"[*] Repartitioned to 2 Partitions  | Actual Count: {p2_count} | Execution Time: {time_p2:.4f} s")

    # 4 Partitions
    df_4 = df.repartition(4)
    p4_count = df_4.rdd.getNumPartitions()
    start_time = time.time()
    _ = df_4.groupBy("movieId").agg(avg("rating")).count()
    time_p4 = time.time() - start_time
    print(f"[*] Repartitioned to 4 Partitions  | Actual Count: {p4_count} | Execution Time: {time_p4:.4f} s")

    # 8 Partitions
    df_8 = df.repartition(8)
    p8_count = df_8.rdd.getNumPartitions()
    start_time = time.time()
    _ = df_8.groupBy("movieId").agg(avg("rating")).count()
    time_p8 = time.time() - start_time
    print(f"[*] Repartitioned to 8 Partitions  | Actual Count: {p8_count} | Execution Time: {time_p8:.4f} s")

    # -------------------------------------------------------------------------
    # SUPPLEMENTARY 1: coalesce() vs repartition()
    # -------------------------------------------------------------------------
    print_separator("Supplementary 1: coalesce() vs repartition()")
    print("coalesce() avoids full network shuffle by merging existing partitions on same nodes.")
    print(f"Reducing partitions from 8 down to 2 using coalesce()...")
    
    df_coalesced = df_8.coalesce(2)
    coalesce_partitions = df_coalesced.rdd.getNumPartitions()
    
    start_time = time.time()
    _ = df_coalesced.groupBy("movieId").agg(avg("rating")).count()
    time_coalesce = time.time() - start_time
    
    print(f"[*] coalesce() Partition Count     : {coalesce_partitions}")
    print(f"[*] coalesce() Execution Time      : {time_coalesce:.4f} s")
    print(f"[*] repartition(2) Execution Time  : {time_p2:.4f} s")

    # -------------------------------------------------------------------------
    # SUPPLEMENTARY 2: StorageLevel.DISK_ONLY vs cache()
    # -------------------------------------------------------------------------
    print_separator("Supplementary 2: persist(StorageLevel.DISK_ONLY)")
    print("Persisting DataFrame using StorageLevel.DISK_ONLY...")
    
    df_disk = df.persist(StorageLevel.DISK_ONLY)
    _ = df_disk.count() # trigger disk persist
    
    start_time = time.time()
    _ = df_disk.groupBy("movieId").agg(avg("rating")).count()
    time_disk = time.time() - start_time
    
    print(f"[*] Execution Time with DISK_ONLY  : {time_disk:.4f} s")
    print(f"[*] Execution Time with cache()    : {time_after_cache:.4f} s")
    df_disk.unpersist()

    # -------------------------------------------------------------------------
    # SUPPLEMENTARY 3: Execution Time for Multiple Spark Actions
    # -------------------------------------------------------------------------
    print_separator("Supplementary 3: Multiple Spark Actions Timing")
    
    # Action 1: count()
    t0 = time.time()
    c_res = df.count()
    t_count = time.time() - t0
    
    # Action 2: take(10)
    t0 = time.time()
    take_res = df.take(10)
    t_take = time.time() - t0
    
    # Action 3: filter() + count()
    t0 = time.time()
    high_rating_count = df.filter(col("rating") >= 4.0).count()
    t_filter = time.time() - t0
    
    print(f"[*] Action count()               : {c_res:,} rows returned in {t_count:.4f} s")
    print(f"[*] Action take(10)              : {len(take_res)} rows returned in {t_take:.4f} s")
    print(f"[*] Action filter(rating>=4.0)   : {high_rating_count:,} rows matched in {t_filter:.4f} s")

    # -------------------------------------------------------------------------
    # TASK 14: Generate Performance Report
    # -------------------------------------------------------------------------
    print_separator("Task 14 & 20: Final Performance Summary")
    summary_text = f"""
========================================================================================
            MOVIEFLIX SPARK PERFORMANCE OPTIMIZATION REPORT
========================================================================================
1. DATASET DETAILS:
   - File Name                 : ratings.csv
   - Total Records             : {total_records:,}
   - Schema                    : userId (int), movieId (int), rating (double)
   - Initial Partitions        : {initial_partitions}
   - Overall Average Rating    : {overall_avg:.2f} / 5.00

2. CACHING BENCHMARK:
   - Before Caching Time       : {time_before_cache:.4f} seconds
   - After Caching Time        : {time_after_cache:.4f} seconds
   - Performance Speedup       : {speedup_cache:.2f}x faster
   - Time Saved                : {time_saved_pct:.2f}%

3. PARTITIONING BENCHMARK:
   - 2 Partitions Execution    : {time_p2:.4f} seconds
   - 4 Partitions Execution    : {time_p4:.4f} seconds
   - 8 Partitions Execution    : {time_p8:.4f} seconds

4. REPARTITION vs COALESCE:
   - repartition(2) Time       : {time_p2:.4f} seconds (Full Shuffle)
   - coalesce(2) Time          : {time_coalesce:.4f} seconds (No Full Shuffle)

5. STORAGE LEVEL COMPARISON:
   - cache() (Memory & Disk)   : {time_after_cache:.4f} seconds
   - persist(DISK_ONLY)        : {time_disk:.4f} seconds

6. OBSERVATIONS & KEY FINDINGS:
   a) Caching drastically cuts repetitive calculation latency by keeping pre-parsed
      records in executor memory, eliminating repetitive disk read and parsing overhead.
   b) Partitioning allows Spark to execute tasks concurrently across CPU cores. Having
      partitions aligned with available CPU cores achieves optimal task balancing.
   c) coalesce() is significantly more lightweight than repartition() when downsizing
      partitions because it avoids expensive cross-node shuffles.
   d) In-memory caching outperforms DISK_ONLY persist because RAM I/O has orders of
      magnitude higher throughput and lower latency than disk read/write cycles.

7. CONCLUSION:
   For MovieFlix recommendation pipelines, combining DataFrame cache() for iterative
   queries with appropriate partition sizing achieves maximum throughput and minimal
   query latency.
========================================================================================
"""
    print(summary_text)

    # Write report file
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(summary_text.strip() + "\n")
    print(f"[OK] Performance report successfully saved to: {report_path}")

    # Stop Spark Session
    spark.stop()
    print("[*] Spark Session stopped successfully.")

if __name__ == "__main__":
    main()
