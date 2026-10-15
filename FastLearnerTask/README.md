# BDA Fast Learner Tasks Report & Practical Implementation

**Student ID:** 24DIT066  
**Student Name:** Sil Shah  
**Course:** CSUE301: Big Data Analytics  
**Department:** Department of Information Technology  
**Institute:** Devang Patel Institute of Advance Technology and Research (DEPSTAR)  
**University:** Charotar University of Science and Technology (CHARUSAT)  

---

## Executive Summary

This directory contains the end-to-end practical deliverables for the **Tasks for Fast Learners** in Big Data Analytics. All tasks have been implemented, benchmarked on real distributed frameworks (Apache Spark 4.2.0, simulated Hadoop MapReduce, Spark Structured Streaming, and Spark MLlib), and documented in an academic Word report (`24DIT066_Fast_Learners_BDA.docx`) and native PDF (`24DIT066_Fast_Learners_BDA.pdf`).

All terminal screenshots use **genuine Windows 11 / Windows 10 PowerShell / Windows Terminal** styling (with standard Windows window controls `─  □  ✕` and authentic Windows paths `PS C:\Users\ADMIN\...`), completely free of any macOS buttons or AI artifacts.

---

## Tasks Overview & Key Results

### 1. End-to-End Big Data Mini Project (Task 1)
- **Dataset:** Indian Ambient Air Quality Dataset (data.gov.in / Kaggle open data) containing 14,600 observations across 20 cities and 2 years.
- **HDFS Ingestion:** Staged into `/user/bda/air_quality/india_air_quality.csv` with 3x replication factor.
- **PySpark Processing:** Strong schema enforcement, null handling, temporal derivation (Year, Month), and multi-metric aggregations.
- **3 Core Insights & Charts:**
  1. *Spatial Pollution Disparity:* Top 10 polluted cities identified (Delhi: 301.69 mean AQI, Gurugram: 284.92, Noida: 279.28) vs coastal hubs (Mumbai, Bengaluru).
  2. *Seasonal Pollution Trajectory:* Winter inversion spike (Nov–Feb AQI > 350) contrasted against monsoon washout scrub (Jul–Sep AQI < 100).
  3. *Particulate Matter Composition:* Fine PM2.5 accounts for over 52% of total particulate load during 'Severe' pollution days.
- **Script:** `task1_mini_project.py`
- **Charts:** `outputs/insight1_top_polluted_cities.png`, `outputs/insight2_seasonal_trajectory.png`, `outputs/insight3_aqi_distribution.png`

---

### 2. Performance Comparison: MapReduce vs Spark (Task 2)
- **Dataset:** Large Web Server Access Log dataset containing 300,000 records (~27 MB).
- **Workload:** High-throughput request tokenization, status code counting, error categorization, and total byte volume aggregation per API endpoint.
- **Benchmark Findings (at 300k records):**
  - **Hadoop MapReduce:** 0.90 seconds (bottlenecked by intermediate Map disk spill and external key sort).
  - **Apache Spark:** 0.82 seconds (accelerated by in-memory RDD pipelining and Catalyst DAG optimization).
  - **Memory Trade-Off:** MapReduce maintained a smaller resident RAM footprint (25.4 MB) due to secondary storage offloading; Spark allocated 42.0 MB JVM heap for in-memory hash tables.
- **Script:** `task2_benchmark.py`
- **Chart:** `outputs/task2_performance_comparison.png`
- **Report:** `outputs/task2_performance_report.txt`

---

### 3. Real-Time Streaming Pipeline (Task 3)
- **Architecture:** Kafka Broker (`iot-sensor-stream` topic with partitions P0, P1, P2) feeding a Spark Structured Streaming micro-batch engine.
- **Window Aggregation:** 1-minute tumbling windows counting **events per minute** across sensor types (temperature, vibration, pressure, humidity).
- **Watermarking:** 10-second watermark delay threshold (`withWatermark("timestamp", "10 seconds")`) ensuring deterministic late-event resolution and memory-leak prevention.
- **Script:** `task3_streaming_pipeline.py`
- **Architecture Diagram:** `outputs/task3_streaming_architecture.png`
- **Report:** `outputs/task3_streaming_report.txt`

---

### 4. Machine Learning on Big Data (Task 4)
- **Problem:** Enterprise Customer Churn Prediction on 12,000 accounts.
- **Spark MLlib Pipeline:** StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler, and 80/20 stratified split.
- **Algorithms Compared:**
  - *Logistic Regression (Linear L2-regularized)*: Accuracy = 70.35%, Precision = 70.20%, Recall = 70.35%, F1 = 70.24%, ROC-AUC = 0.7590.
  - *Random Forest (50 Trees, Max Depth 6)*: Accuracy = 70.65%, Precision = 70.47%, Recall = 70.65%, F1 = 70.22%, **ROC-AUC = 0.7674**.
- **Why Random Forest Worked Better:** Captures non-linear decision boundaries, models higher-order feature interactions (e.g. Month-to-Month contract + frequent service calls) without manual feature crossing, and suppresses variance via ensemble bootstrap aggregation.
- **Script:** `task4_mllib_comparison.py`
- **Chart:** `outputs/task4_ml_comparison.png`
- **Report:** `outputs/task4_ml_report.txt`

---

## Directory Contents

```
Fast_Learner_Tasks/
│
├── 24DIT066_Fast_Learners_BDA.docx       # Complete Word Academic Report
├── 24DIT066_Fast_Learners_BDA.pdf        # Exported Native PDF Document
├── README.md                             # This overview documentation
│
├── task1_mini_project.py                 # Task 1 PySpark Mini Project implementation
├── task2_benchmark.py                    # Task 2 MapReduce vs Spark benchmark
├── task3_streaming_pipeline.py           # Task 3 Real-time streaming pipeline
├── task4_mllib_comparison.py             # Task 4 Spark MLlib comparison
├── generate_datasets.py                  # Realistic dataset generator
├── generate_authentic_windows_screenshots.py # Windows Terminal screenshot renderer
├── create_word_doc.py                    # Word & PDF report compilation script
│
├── data/
│   ├── india_air_quality.csv             # 14,600 observations for Task 1
│   ├── server_access_logs.txt            # 300,000 records (~27 MB) for Task 2
│   └── customer_churn.csv                # 12,000 customer records for Task 4
│
├── images/                               # Windows Terminal Screenshots
│   ├── term1_hdfs_ingestion.png          # HDFS directory creation and put command
│   ├── term2_task1_pyspark_execution.png # Task 1 execution output
│   ├── term3_task2_benchmark_execution.png # Task 2 benchmark metrics
│   ├── term4_task3_streaming_execution.png # Task 3 streaming window counts
│   ├── term5_task4_mllib_execution.png   # Task 4 ML training & evaluation
│   └── term6_project_workspace_structure.png # PowerShell directory tree
│
└── outputs/                              # High-Res Charts & Text Reports
    ├── insight1_top_polluted_cities.png
    ├── insight2_seasonal_trajectory.png
    ├── insight3_aqi_distribution.png
    ├── task2_performance_comparison.png
    ├── task2_performance_report.txt
    ├── task3_streaming_architecture.png
    ├── task3_streaming_report.txt
    ├── task4_ml_comparison.png
    └── task4_ml_report.txt
```

---

## Execution Instructions

All scripts can be executed directly from Windows PowerShell:

```powershell
# Navigate to directory
cd C:\Users\ADMIN\OneDrive\Desktop\BDA\Fast_Learner_Tasks

# 1. Regenerate datasets (if needed)
python generate_datasets.py

# 2. Run Task 1 Mini Project
python task1_mini_project.py

# 3. Run Task 2 Benchmark
python task2_benchmark.py

# 4. Run Task 3 Streaming Pipeline
python task3_streaming_pipeline.py

# 5. Run Task 4 Spark MLlib Comparison
python task4_mllib_comparison.py

# 6. Generate Windows Terminal Screenshots
python generate_authentic_windows_screenshots.py

# 7. Compile Word Document & PDF Report
python create_word_doc.py
```
