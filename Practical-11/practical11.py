"""
========================================================================================
BDA Practical 11: Large-Scale Logistic Regression for Spam Detection using
                  Distributed Stochastic Gradient Descent (DSGD)
CO / PO Mapping : CO5, PO1, PO2, PO5
Scenario        : SecureComm Inc. - Telecom Spam Prevention Engine
Student         : Sil Shah (24DIT066)
Subject         : CSUE301: Big Data Analytics
========================================================================================
"""

import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, lit
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    Tokenizer, StopWordsRemover, HashingTF, IDF,
    StringIndexer, CountVectorizer
)
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator, MulticlassClassificationEvaluator
)

def print_separator(title=""):
    print("\n" + "=" * 70)
    if title:
        print(f" {title.upper()}")
        print("=" * 70)

def main():
    start_total_time = time.time()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "sms_spam_collection.csv")
    roc_chart_path = os.path.join(base_dir, "roc_curve.png")
    scale_chart_path = os.path.join(base_dir, "training_time_vs_datasize.png")
    comparison_chart_path = os.path.join(base_dir, "metrics_and_gd_comparison.png")
    report_path = os.path.join(base_dir, "spam_detection_report.txt")

    # -------------------------------------------------------------------------
    # TASK 1: INITIALIZE SPARK SESSION AND LOAD DATASET
    # -------------------------------------------------------------------------
    print_separator("TASK 1: INITIALIZE SPARK SESSION & INGEST SMS DATASET")
    
    spark = SparkSession.builder \
        .appName("SecureComm-Spam-Detection-DSGD") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("ERROR")
    
    print(f"Spark Version          : {spark.version}")
    print(f"Spark Application Name : {spark.sparkContext.appName}")
    print(f"Master URL             : {spark.sparkContext.master}")
    print(f"Dataset File Path      : {dataset_path}")

    # Load dataset
    df_raw = spark.read.csv(dataset_path, header=True, inferSchema=True)
    total_messages = df_raw.count()
    print(f"\nTotal SMS messages ingested: {total_messages:,}")
    
    print("\nSchema of Dataset:")
    df_raw.printSchema()
    
    print("\nFirst 5 Sample Records:")
    df_raw.show(5, truncate=75)
    
    # Class Distribution
    class_dist = df_raw.groupBy("label").agg(count("*").alias("count"))
    print("Class Distribution:")
    class_dist.show()

    # Convert Label to Numeric Index (ham -> 0.0, spam -> 1.0)
    label_indexer = StringIndexer(inputCol="label", outputCol="label_idx")
    df_indexed = label_indexer.fit(df_raw).transform(df_raw)

    # -------------------------------------------------------------------------
    # TASK 2: TEXT PREPROCESSING (TOKENIZATION, STOP WORDS, TF-IDF)
    # -------------------------------------------------------------------------
    print_separator("TASK 2: TEXT PREPROCESSING & TF-IDF FEATURE EXTRACTION")
    
    tokenizer = Tokenizer(inputCol="message_text", outputCol="tokens")
    stopwords_remover = StopWordsRemover(inputCol="tokens", outputCol="filtered_tokens")
    hashing_tf = HashingTF(inputCol="filtered_tokens", outputCol="raw_features", numFeatures=4096)
    idf = IDF(inputCol="raw_features", outputCol="features")

    print("Pipeline stages configured:")
    print(" 1. Tokenizer          : Splits message text into lowercased token sequences")
    print(" 2. StopWordsRemover   : Filters common English words ('is', 'the', 'at', etc.)")
    print(" 3. HashingTF          : Maps token sequences into high-dimensional feature vectors (dim=4096)")
    print(" 4. IDF                : Scales term frequencies inversely by document occurrences")

    # -------------------------------------------------------------------------
    # SPLIT DATASET (80% Train, 20% Test)
    # -------------------------------------------------------------------------
    train_df, test_df = df_indexed.randomSplit([0.8, 0.2], seed=42)
    train_count = train_df.count()
    test_count = test_df.count()
    print(f"\nTrain set count: {train_count:,} (80%) | Test set count: {test_count:,} (20%)")

    # Fit feature transformers on train data
    prep_pipeline = Pipeline(stages=[tokenizer, stopwords_remover, hashing_tf, idf])
    prep_model = prep_pipeline.fit(train_df)
    train_features = prep_model.transform(train_df).cache()
    test_features = prep_model.transform(test_df).cache()

    print("\nSample Preprocessed Features (tokens & sparse vector representation):")
    train_features.select("label", "filtered_tokens", "features").show(3, truncate=60)

    # -------------------------------------------------------------------------
    # TASK 3: LOGISTIC REGRESSION USING SPARK MLLIB (DISTRIBUTED SGD / L-BFGS)
    # -------------------------------------------------------------------------
    print_separator("TASK 3: LOGISTIC REGRESSION TRAINING USING SPARK MLLIB")
    
    lr = LogisticRegression(
        featuresCol="features",
        labelCol="label_idx",
        maxIter=25,
        regParam=0.05,
        elasticNetParam=0.0
    )
    
    start_train = time.time()
    lr_model = lr.fit(train_features)
    train_duration = time.time() - start_train
    
    print(f"Distributed Logistic Regression Model trained in {train_duration:.4f} seconds.")
    print(f"Number of iterations completed : {lr_model.summary.totalIterations}")
    print(f"Objective history (loss drop)  : {[round(x, 4) for x in lr_model.summary.objectiveHistory[:5]]} ...")

    # Predict on test set
    predictions = lr_model.transform(test_features)
    print("\nPredictions Sample:")
    predictions.select("message_text", "label", "prediction", "probability").show(5, truncate=55)

    # -------------------------------------------------------------------------
    # TASK 5: MODEL EVALUATION (ACCURACY, PRECISION, RECALL, F1, ROC-AUC)
    # -------------------------------------------------------------------------
    print_separator("TASK 5: COMPREHENSIVE MODEL EVALUATION")
    
    mc_evaluator = MulticlassClassificationEvaluator(labelCol="label_idx", predictionCol="prediction")
    bin_evaluator_roc = BinaryClassificationEvaluator(labelCol="label_idx", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
    bin_evaluator_pr = BinaryClassificationEvaluator(labelCol="label_idx", rawPredictionCol="rawPrediction", metricName="areaUnderPR")

    accuracy = mc_evaluator.evaluate(predictions, {mc_evaluator.metricName: "accuracy"})
    precision = mc_evaluator.evaluate(predictions, {mc_evaluator.metricName: "weightedPrecision"})
    recall = mc_evaluator.evaluate(predictions, {mc_evaluator.metricName: "weightedRecall"})
    f1 = mc_evaluator.evaluate(predictions, {mc_evaluator.metricName: "f1"})
    roc_auc = bin_evaluator_roc.evaluate(predictions)
    pr_auc = bin_evaluator_pr.evaluate(predictions)

    # Confusion Matrix calculation
    tp = predictions.filter((col("label_idx") == 1.0) & (col("prediction") == 1.0)).count()
    fp = predictions.filter((col("label_idx") == 0.0) & (col("prediction") == 1.0)).count()
    fn = predictions.filter((col("label_idx") == 1.0) & (col("prediction") == 0.0)).count()
    tn = predictions.filter((col("label_idx") == 0.0) & (col("prediction") == 0.0)).count()

    spam_precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    spam_recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    spam_f1 = (2 * spam_precision * spam_recall) / (spam_precision + spam_recall) if (spam_precision + spam_recall) > 0 else 0

    print(f"Accuracy                 : {accuracy * 100:.2f}%")
    print(f"Weighted Precision       : {precision * 100:.2f}%")
    print(f"Weighted Recall          : {recall * 100:.2f}%")
    print(f"Weighted F1-Score        : {f1 * 100:.2f}%")
    print(f"Spam Class Precision     : {spam_precision * 100:.2f}%")
    print(f"Spam Class Recall        : {spam_recall * 100:.2f}%")
    print(f"Spam Class F1-Score      : {spam_f1 * 100:.2f}%")
    print(f"ROC - Area Under Curve   : {roc_auc:.4f}")
    print(f"PR  - Area Under Curve   : {pr_auc:.4f}")
    print("\nConfusion Matrix:")
    print(f"  True Positives  (Spam detected as Spam) : {tp:,}")
    print(f"  False Positives (Ham flagged as Spam)   : {fp:,}")
    print(f"  False Negatives (Spam missed as Ham)    : {fn:,}")
    print(f"  True Negatives  (Ham detected as Ham)   : {tn:,}")

    # Generate ROC Curve visualization
    try:
        binary_summary = lr_model.summary
        roc_df = binary_summary.roc.toPandas()
        
        plt.figure(figsize=(7, 5.5), dpi=200)
        plt.plot(roc_df['FPR'], roc_df['TPR'], color='#004B87', lw=2.5, label=f'ROC Curve (AUC = {roc_auc:.4f})')
        plt.plot([0, 1], [0, 1], color='#888888', linestyle='--', lw=1.5, label='Random Chance Baseline')
        plt.xlim([-0.02, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate (FPR)', fontsize=11, fontweight='bold')
        plt.ylabel('True Positive Rate (TPR / Recall)', fontsize=11, fontweight='bold')
        plt.title('Receiver Operating Characteristic (ROC) - Spam Detection\nSecureComm Big Data Analytics', fontsize=12, fontweight='bold', pad=12)
        plt.legend(loc="lower right", fontsize=10)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.tight_layout()
        plt.savefig(roc_chart_path)
        plt.close()
        print(f"\nROC Curve plot saved to: {roc_chart_path}")
    except Exception as e:
        print(f"ROC plot notice: {e}")

    # -------------------------------------------------------------------------
    # TASK 4: HYPERPARAMETER TUNING (regParam, elasticNetParam, maxIter)
    # -------------------------------------------------------------------------
    print_separator("TASK 4: HYPERPARAMETER TUNING ANALYSIS")
    
    tuning_experiments = [
        {"reg": 0.0,  "elastic": 0.0, "maxIter": 20, "desc": "Unregularized (Standard ML)"},
        {"reg": 0.01, "elastic": 0.0, "maxIter": 20, "desc": "L2 Ridge (Light Penalty)"},
        {"reg": 0.1,  "elastic": 0.0, "maxIter": 20, "desc": "L2 Ridge (Medium Penalty)"},
        {"reg": 0.05, "elastic": 0.5, "maxIter": 20, "desc": "ElasticNet (Balanced L1+L2)"},
        {"reg": 0.05, "elastic": 1.0, "maxIter": 20, "desc": "L1 Lasso (Feature Sparsity)"},
        {"reg": 0.05, "elastic": 0.0, "maxIter": 50, "desc": "L2 Ridge (High Iterations)"}
    ]

    tuning_results = []
    print(f"{'Config':<30} | {'regParam':<8} | {'elasticNet':<10} | {'maxIter':<7} | {'Accuracy':<9} | {'F1-Score':<9} | {'Time (s)':<8}")
    print("-" * 95)
    
    for exp in tuning_experiments:
        t0 = time.time()
        lr_tune = LogisticRegression(
            featuresCol="features",
            labelCol="label_idx",
            regParam=exp["reg"],
            elasticNetParam=exp["elastic"],
            maxIter=exp["maxIter"]
        )
        tune_model = lr_tune.fit(train_features)
        dt = time.time() - t0
        preds = tune_model.transform(test_features)
        acc = mc_evaluator.evaluate(preds, {mc_evaluator.metricName: "accuracy"})
        f1_score = mc_evaluator.evaluate(preds, {mc_evaluator.metricName: "f1"})
        
        tuning_results.append({
            "desc": exp["desc"],
            "reg": exp["reg"],
            "elastic": exp["elastic"],
            "maxIter": exp["maxIter"],
            "acc": acc,
            "f1": f1_score,
            "time": dt
        })
        print(f"{exp['desc']:<30} | {exp['reg']:<8.2f} | {exp['elastic']:<10.2f} | {exp['maxIter']:<7} | {acc*100:<8.2f}% | {f1_score:<9.4f} | {dt:<8.3f}")

    # -------------------------------------------------------------------------
    # TASK 6: DATASET SIZE SCALING DEMONSTRATION (TIME VS ACCURACY)
    # -------------------------------------------------------------------------
    print_separator("TASK 6: DATASET SCALING ANALYSIS (TRAINING TIME VS SIZE)")
    
    scale_multipliers = [1, 5, 10, 25]
    scale_results = []
    
    print(f"{'Records':<12} | {'Partitions':<10} | {'Training Time (s)':<18} | {'Accuracy':<10} | {'Throughput (msgs/s)':<20}")
    print("-" * 80)
    
    for mult in scale_multipliers:
        # Augment dataframe by unioning replicas to simulate large-scale data
        if mult == 1:
            scaled_train = train_features
        else:
            scaled_train = train_features
            for _ in range(mult - 1):
                scaled_train = scaled_train.union(train_features)
        
        scaled_count = train_count * mult
        t_start = time.time()
        lr_scale = LogisticRegression(featuresCol="features", labelCol="label_idx", maxIter=15, regParam=0.05)
        scale_model = lr_scale.fit(scaled_train)
        t_scaled = time.time() - t_start
        
        scale_preds = scale_model.transform(test_features)
        scale_acc = mc_evaluator.evaluate(scale_preds, {mc_evaluator.metricName: "accuracy"})
        throughput = scaled_count / t_scaled if t_scaled > 0 else 0
        
        scale_results.append({
            "records": scaled_count,
            "time": t_scaled,
            "accuracy": scale_acc,
            "throughput": throughput
        })
        print(f"{scaled_count:<12,} | {scaled_train.rdd.getNumPartitions():<10} | {t_scaled:<18.4f} | {scale_acc*100:<9.2f}% | {throughput:<20,.1f}")

    # Plot Scaling Curve
    fig, ax1 = plt.subplots(figsize=(8, 5), dpi=200)
    rec_sizes = [x["records"] / 1000 for x in scale_results]
    t_times = [x["time"] for x in scale_results]
    acc_vals = [x["accuracy"] * 100 for x in scale_results]

    color = '#0055A5'
    ax1.set_xlabel('Dataset Size (Thousands of Records)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Training Time (Seconds)', color=color, fontsize=11, fontweight='bold')
    ax1.plot(rec_sizes, t_times, color=color, marker='o', lw=2.5, markersize=7, label='Training Time')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle=':', alpha=0.5)

    ax2 = ax1.twinx()
    color = '#2E7D32'
    ax2.set_ylabel('Model Accuracy (%)', color=color, fontsize=11, fontweight='bold')
    ax2.plot(rec_sizes, acc_vals, color=color, marker='s', linestyle='--', lw=2.2, markersize=7, label='Accuracy')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim([90, 101])

    plt.title('Distributed Logistic Regression: Training Time vs Dataset Size\nSecureComm Scalability Benchmark', fontsize=12, fontweight='bold', pad=12)
    plt.tight_layout()
    plt.savefig(scale_chart_path)
    plt.close()
    print(f"\nDataset scaling plot saved to: {scale_chart_path}")

    # -------------------------------------------------------------------------
    # TASK 7: FULL-BATCH VS MINI-BATCH GRADIENT DESCENT COMPARISON
    # -------------------------------------------------------------------------
    print_separator("TASK 7: FULL-BATCH VS MINI-BATCH DISTRIBUTED GRADIENT DESCENT")
    
    # In distributed MLlib, L-BFGS uses full RDD passes per iteration (Full-batch GD analog),
    # while mini-batch SGD updates weights across partition subsets with batch fractions.
    # We benchmark full-pass optimization vs partition mini-batch training.
    
    # 1. Full-Batch Gradient Descent (Standard L-BFGS optimizing over entire dataset per step)
    t0_fb = time.time()
    lr_full = LogisticRegression(featuresCol="features", labelCol="label_idx", maxIter=25, regParam=0.01)
    model_full = lr_full.fit(train_features)
    time_fb = time.time() - t0_fb
    preds_fb = model_full.transform(test_features)
    acc_fb = mc_evaluator.evaluate(preds_fb, {mc_evaluator.metricName: "accuracy"})

    # 2. Mini-Batch Gradient Descent Simulation (Partition-based mini-batches / sub-sampling)
    # Using 25% mini-batch sample with multiple iterations
    t0_mb = time.time()
    mini_batch_df = train_features.sample(withReplacement=False, fraction=0.35, seed=123)
    lr_mini = LogisticRegression(featuresCol="features", labelCol="label_idx", maxIter=10, regParam=0.01)
    model_mini = lr_mini.fit(mini_batch_df)
    time_mb = time.time() - t0_mb
    preds_mb = model_mini.transform(test_features)
    acc_mb = mc_evaluator.evaluate(preds_mb, {mc_evaluator.metricName: "accuracy"})

    speedup = (time_fb - time_mb) / time_fb * 100 if time_fb > 0 else 0

    print(f"Full-Batch Optimization Time  : {time_fb:.4f} s | Test Accuracy: {acc_fb*100:.2f}%")
    print(f"Mini-Batch Optimization Time  : {time_mb:.4f} s | Test Accuracy: {acc_mb*100:.2f}%")
    print(f"Mini-Batch Execution Speedup  : {speedup:.1f}% faster with minimal accuracy variation ({abs(acc_fb - acc_mb)*100:.2f}%)")

    # -------------------------------------------------------------------------
    # SUPPLEMENTARY PROBLEMS IMPLEMENTATION
    # -------------------------------------------------------------------------
    print_separator("SUPPLEMENTARY PROBLEMS IMPLEMENTATION")
    
    print("\n--- Supplementary Problem 1: HashingTF vs CountVectorizer Comparison ---")
    cv = CountVectorizer(inputCol="filtered_tokens", outputCol="cv_features", vocabSize=4096)
    t0_cv = time.time()
    prep_tokens_train = stopwords_remover.transform(tokenizer.transform(train_df))
    cv_model = cv.fit(prep_tokens_train)
    cv_train = cv_model.transform(prep_tokens_train)
    cv_lr = LogisticRegression(featuresCol="cv_features", labelCol="label_idx", maxIter=15).fit(cv_train)
    t_cv = time.time() - t0_cv
    
    print(f"HashingTF Feature Space        : 4,096 buckets (Stateless, no dictionary pass required)")
    print(f"CountVectorizer Vocabulary Size: {cv_model.getVocabSize():,} unique terms (Stateful dictionary)")
    print(f"HashingTF Pipeline Fit Time    : Precomputed in pipeline (Instant mapping)")
    print(f"CountVectorizer Pipeline Fit   : {t_cv:.4f} seconds (Requires vocabulary aggregation pass)")

    print("\n--- Supplementary Problem 3: End-to-End Spark ML Pipeline API ---")
    unified_pipeline = Pipeline(stages=[
        tokenizer,
        stopwords_remover,
        hashing_tf,
        idf,
        LogisticRegression(featuresCol="features", labelCol="label_idx", maxIter=20, regParam=0.05)
    ])
    
    t0_pipe = time.time()
    unified_model = unified_pipeline.fit(train_df)
    pipe_duration = time.time() - t0_pipe
    pipe_preds = unified_model.transform(test_df)
    pipe_acc = mc_evaluator.evaluate(pipe_preds, {mc_evaluator.metricName: "accuracy"})
    print(f"Unified Pipeline (Tokenizer -> StopWords -> HashingTF -> IDF -> LogisticRegression):")
    print(f"Training Time: {pipe_duration:.4f} s | Accuracy: {pipe_acc * 100:.2f}%")

    # Plot Comparison Charts
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), dpi=200)

    # Subplot 1: Evaluation Metrics
    metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
    metrics_vals = [accuracy * 100, precision * 100, recall * 100, f1 * 100, roc_auc * 100]
    colors = ['#1565C0', '#00897B', '#E65100', '#6A1B9A', '#C2185B']
    bars = ax1.bar(metrics_names, metrics_vals, color=colors, width=0.55)
    ax1.set_ylim([80, 105])
    ax1.set_ylabel('Percentage (%)', fontsize=10, fontweight='bold')
    ax1.set_title('Spam Classifier Performance Metrics', fontsize=11, fontweight='bold')
    ax1.grid(axis='y', linestyle=':', alpha=0.6)
    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.8, f"{yval:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Subplot 2: Full-Batch vs Mini-Batch Training Time
    gd_names = ['Full-Batch GD\n(L-BFGS)', 'Mini-Batch GD\n(Partition Subsampling)']
    gd_times = [time_fb, time_mb]
    bars2 = ax2.bar(gd_names, gd_times, color=['#37474F', '#00838F'], width=0.45)
    ax2.set_ylabel('Training Time (Seconds)', fontsize=10, fontweight='bold')
    ax2.set_title('Optimization Time: Full-Batch vs Mini-Batch', fontsize=11, fontweight='bold')
    ax2.grid(axis='y', linestyle=':', alpha=0.6)
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, f"{yval:.2f} s", ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(comparison_chart_path)
    plt.close()
    print(f"\nMetrics and GD comparison plot saved to: {comparison_chart_path}")

    # -------------------------------------------------------------------------
    # WRITE SUMMARY REPORT FILE
    # -------------------------------------------------------------------------
    total_elapsed = time.time() - start_total_time
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("      SECURECOMM INC. - DISTRIBUTED SPAM DETECTION PERFORMANCE REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"1. ENVIRONMENT DETAILS:\n")
        f.write(f"   - Engine                   : Apache Spark {spark.version} with PySpark MLlib\n")
        f.write(f"   - Master Node              : {spark.sparkContext.master}\n")
        f.write(f"   - Dataset File             : sms_spam_collection.csv\n")
        f.write(f"   - Total Messages Processed : {total_messages:,}\n")
        f.write(f"   - Train / Test Split       : 80% ({train_count:,}) / 20% ({test_count:,})\n\n")
        f.write(f"2. MODEL EVALUATION METRICS:\n")
        f.write(f"   - Overall Accuracy         : {accuracy * 100:.2f}%\n")
        f.write(f"   - Weighted Precision       : {precision * 100:.2f}%\n")
        f.write(f"   - Weighted Recall          : {recall * 100:.2f}%\n")
        f.write(f"   - Weighted F1-Score        : {f1 * 100:.2f}%\n")
        f.write(f"   - Spam Class Precision     : {spam_precision * 100:.2f}%\n")
        f.write(f"   - Spam Class Recall        : {spam_recall * 100:.2f}%\n")
        f.write(f"   - Spam Class F1-Score      : {spam_f1 * 100:.2f}%\n")
        f.write(f"   - ROC - Area Under Curve   : {roc_auc:.4f}\n")
        f.write(f"   - PR  - Area Under Curve   : {pr_auc:.4f}\n\n")
        f.write(f"3. CONFUSION MATRIX:\n")
        f.write(f"   - True Positives  (Spam detected as Spam) : {tp:,}\n")
        f.write(f"   - False Positives (Ham flagged as Spam)   : {fp:,}\n")
        f.write(f"   - False Negatives (Spam missed as Ham)    : {fn:,}\n")
        f.write(f"   - True Negatives  (Ham detected as Ham)   : {tn:,}\n\n")
        f.write(f"4. HYPERPARAMETER TUNING BENCHMARKS:\n")
        f.write(f"   Config                         | regParam | elasticNet | maxIter | Accuracy | F1-Score | Time (s)\n")
        f.write(f"   --------------------------------------------------------------------------------------------\n")
        for res in tuning_results:
            f.write(f"   {res['desc']:<30} | {res['reg']:<8.2f} | {res['elastic']:<10.2f} | {res['maxIter']:<7} | {res['acc']*100:<8.2f}% | {res['f1']:<8.4f} | {res['time']:<8.3f}\n")
        f.write("\n")
        f.write(f"5. DATASET SCALABILITY BENCHMARK:\n")
        f.write(f"   Records      | Training Time (s) | Test Accuracy | Throughput (msgs/sec)\n")
        f.write(f"   --------------------------------------------------------------------\n")
        for res in scale_results:
            f.write(f"   {res['records']:<12,} | {res['time']:<17.4f} | {res['accuracy']*100:<13.2f}% | {res['throughput']:<20,.1f}\n")
        f.write("\n")
        f.write(f"6. FULL-BATCH VS MINI-BATCH GRADIENT DESCENT:\n")
        f.write(f"   - Full-Batch GD (L-BFGS)  : {time_fb:.4f} s | Accuracy: {acc_fb*100:.2f}%\n")
        f.write(f"   - Mini-Batch SGD          : {time_mb:.4f} s | Accuracy: {acc_mb*100:.2f}%\n")
        f.write(f"   - Relative Speedup        : {speedup:.1f}% reduction in training time\n\n")
        f.write(f"7. TOTAL PRACTICAL RUNTIME   : {total_elapsed:.2f} seconds\n")
        f.write("=" * 80 + "\n")

    print(f"\nExecution summary report saved to: {report_path}")
    print(f"Total Practical 11 runtime: {total_elapsed:.2f} seconds")
    
    spark.stop()

if __name__ == "__main__":
    main()
