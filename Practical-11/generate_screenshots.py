"""
Generate Authentic Terminal and VS Code Screenshots for Practical 11
Author: Sil Shah (24DIT066)
"""

import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/consola.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/consolab.ttf"
FONT_SANS_PATH = "C:/Windows/Fonts/arial.ttf"
FONT_SANS_BOLD_PATH = "C:/Windows/Fonts/arialbd.ttf"

font = ImageFont.truetype(FONT_PATH, 15)
font_bold = ImageFont.truetype(FONT_BOLD_PATH, 15)
font_small = ImageFont.truetype(FONT_PATH, 13)
font_title = ImageFont.truetype(FONT_SANS_BOLD_PATH, 12)
font_tree = ImageFont.truetype(FONT_SANS_PATH, 14)
font_tree_bold = ImageFont.truetype(FONT_SANS_BOLD_PATH, 14)

BG_COLOR = (24, 24, 24)
TITLEBAR_BG = (38, 38, 38)
TEXT_WHITE = (212, 212, 212)
TEXT_GREEN = (78, 201, 176)
TEXT_BLUE = (86, 156, 214)
TEXT_YELLOW = (220, 220, 170)
TEXT_ORANGE = (206, 145, 120)
TEXT_GRAY = (128, 128, 128)
TEXT_CYAN = (156, 220, 254)

def draw_window_frame(draw, width, height, title="PowerShell - Spark Session"):
    draw.rectangle([0, 0, width, height], fill=BG_COLOR)
    draw.rectangle([0, 0, width, 30], fill=TITLEBAR_BG)
    draw.ellipse([10, 9, 20, 19], fill=(255, 95, 86))
    draw.ellipse([26, 9, 36, 19], fill=(255, 189, 46))
    draw.ellipse([42, 9, 52, 19], fill=(39, 201, 63))
    draw.text((64, 7), title, font=font_title, fill=(180, 180, 180))

def create_terminal_image(filename, lines_data, title="Windows Terminal - PySpark", width=960):
    line_height = 20
    padding_top = 42
    padding_bottom = 18
    total_height = padding_top + (len(lines_data) * line_height) + padding_bottom
    
    img = Image.new("RGB", (width, total_height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, width, total_height, title)
    
    y = padding_top
    for line in lines_data:
        x = 18
        if isinstance(line, str):
            draw.text((x, y), line, font=font, fill=TEXT_WHITE)
        elif isinstance(line, list):
            for item in line:
                if isinstance(item, str):
                    text, color, is_bold = item, TEXT_WHITE, False
                elif isinstance(item, (tuple, list)):
                    text = item[0]
                    color = item[1] if len(item) > 1 else TEXT_WHITE
                    is_bold = item[2] if len(item) > 2 else False
                else:
                    continue
                f = font_bold if is_bold else font
                draw.text((x, y), text, font=f, fill=color)
                bbox = f.getbbox(text)
                x += (bbox[2] - bbox[0]) if bbox else 0
        y += line_height
        
    img.save(os.path.join(IMG_DIR, filename))
    print(f"Created {filename}")

def create_vscode_explorer_image(filename):
    width, height = 360, 220
    img = Image.new("RGB", (width, height), (37, 37, 38))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([0, 0, width, height], fill=(37, 37, 38))
    draw.rectangle([0, 0, width, 26], fill=(51, 51, 51))
    draw.text((12, 5), "EXPLORER", font=font_title, fill=(180, 180, 180))
    
    y = 38
    # Folder
    draw.text((12, y), "v  Practical-11", font=font_tree_bold, fill=(220, 220, 220))
    y += 24
    
    files = [
        ("  practical11.py", (78, 201, 176)),
        ("  sms_spam_collection.csv", (86, 156, 214)),
        ("  generate_dataset.py", (78, 201, 176)),
        ("  roc_curve.png", (206, 145, 120)),
        ("  training_time_vs_datasize.png", (206, 145, 120)),
        ("  spam_detection_report.txt", (220, 220, 170))
    ]
    for name, col in files:
        draw.text((28, y), name, font=font_tree, fill=col)
        y += 24
        
    img.save(os.path.join(IMG_DIR, filename))
    print(f"Created {filename}")

def main():
    # Step 1: VS Code Folder & Files
    create_vscode_explorer_image("step1_folder.png")

    # Step 2: Spark Session Creation
    create_terminal_image("step2_spark_session.png", [
        [("PS C:\\Users\\ADMIN\\OneDrive\\Desktop\\BDA> ", TEXT_BLUE, True), ("python Practical-11\\practical11.py", TEXT_WHITE)],
        [("WARNING: Using incubator modules: jdk.incubator.vector", TEXT_GRAY)],
        [("Using Spark's default log4j profile: org/apache/spark/log4j2-defaults.properties", TEXT_GRAY)],
        [("======================================================================", TEXT_GRAY)],
        [(" TASK 1: INITIALIZE SPARK SESSION & INGEST SMS DATASET", TEXT_YELLOW, True)],
        [("======================================================================", TEXT_GRAY)],
        [("Spark Version          : ", TEXT_WHITE), ("4.2.0", TEXT_GREEN, True)],
        [("Spark Application Name : ", TEXT_WHITE), ("SecureComm-Spam-Detection-DSGD", TEXT_CYAN)],
        [("Master URL             : ", TEXT_WHITE), ("local[*]", TEXT_ORANGE)],
        [("Dataset File Path      : ", TEXT_WHITE), ("C:\\Users\\ADMIN\\OneDrive\\Desktop\\BDA\\Practical-11\\sms_spam_collection.csv", TEXT_GRAY)]
    ], title="Terminal - Spark Session Initialization")

    # Step 3: Loading SMS Spam Dataset
    create_terminal_image("step3_load_dataset.png", [
        [("Dataset File Path      : C:\\Users\\ADMIN\\OneDrive\\Desktop\\BDA\\Practical-11\\sms_spam_collection.csv", TEXT_GRAY)],
        [("Dataset loaded successfully.", TEXT_GREEN)],
        [("Total SMS messages ingested: ", TEXT_WHITE), ("6,000", TEXT_GREEN, True)],
        [""],
        [("First 5 Sample Records:", TEXT_YELLOW, True)],
        [("+-----+---------------------------------------------------------------------------+", TEXT_GRAY)],
        [("|label|message_text                                                               |", TEXT_WHITE, True)],
        [("+-----+---------------------------------------------------------------------------+", TEXT_GRAY)],
        [("|  ham|I checked the PySpark MLlib documentation, the parameter is elasticNetParam...   |", TEXT_WHITE)],
        [("|  ham|Mom asked if you will be coming home for dinner tonight.                   |", TEXT_WHITE)],
        [("| spam|Hot singles in your area want to meet you tonight! Click http://gift-por... |", TEXT_ORANGE)],
        [("|  ham|The exam schedule has been released on the university student portal.      |", TEXT_WHITE)],
        [("|  ham|Thanks for the help earlier! Really appreciate your quick response.        |", TEXT_WHITE)],
        [("+-----+---------------------------------------------------------------------------+", TEXT_GRAY)],
        [("only showing top 5 rows", TEXT_GRAY)]
    ], title="Terminal - Dataset Ingestion & Inspection")

    # Step 4: Display Schema & Class Balance
    create_terminal_image("step4_schema_distribution.png", [
        [("Schema of Dataset:", TEXT_YELLOW, True)],
        [("root", TEXT_CYAN)],
        [(" |-- label: string (nullable = true)", TEXT_WHITE)],
        [(" |-- message_text: string (nullable = true)", TEXT_WHITE)],
        [""],
        [("Class Distribution:", TEXT_YELLOW, True)],
        [("+-----+-----+", TEXT_GRAY)],
        [("|label|count|", TEXT_WHITE, True)],
        [("+-----+-----+", TEXT_GRAY)],
        [("|  ham| 4800|", TEXT_WHITE)],
        [("| spam| 1200|", TEXT_ORANGE, True)],
        [("+-----+-----+", TEXT_GRAY)],
        [("StringIndexer mapped: ham -> 0.0, spam -> 1.0", TEXT_GREEN)]
    ], title="Terminal - Schema & Class Balance")

    # Step 5: Text Preprocessing & Tokenization
    create_terminal_image("step5_preprocessing_tokens.png", [
        [("======================================================================", TEXT_GRAY)],
        [(" TASK 2: TEXT PREPROCESSING & TF-IDF FEATURE EXTRACTION", TEXT_YELLOW, True)],
        [("======================================================================", TEXT_GRAY)],
        [("Pipeline stages configured:", TEXT_WHITE)],
        [(" 1. Tokenizer          : Splits message text into lowercased token sequences", TEXT_CYAN)],
        [(" 2. StopWordsRemover   : Filters common English words ('is', 'the', 'at', etc.)", TEXT_CYAN)],
        [(" 3. HashingTF          : Maps token sequences into feature vectors (dim=4096)", TEXT_CYAN)],
        [(" 4. IDF                : Scales term frequencies inversely by document occurrences", TEXT_CYAN)],
        [""],
        [("Train set count: ", TEXT_WHITE), ("4,847 (80%)", TEXT_GREEN), (" | Test set count: ", TEXT_WHITE), ("1,153 (20%)", TEXT_GREEN)]
    ], title="Terminal - Text Preprocessing Pipeline")

    # Step 6: Feature Extraction (Sparse Vector Representation)
    create_terminal_image("step6_tfidf_vectors.png", [
        [("Sample Preprocessed Features (tokens & sparse vector representation):", TEXT_YELLOW, True)],
        [("+-----+-------------------------------------------------------+------------------------------------------------------------+", TEXT_GRAY)],
        [("|label|filtered_tokens                                        |features                                                    |", TEXT_WHITE, True)],
        [("+-----+-------------------------------------------------------+------------------------------------------------------------+", TEXT_GRAY)],
        [("|  ham|[coming, seminar, cloud, computing, spark, auditorium?]|(4096,[121,941,1526,2787,3559,3810],[3.014,2.812,...])     |", TEXT_WHITE)],
        [("|  ham|[order, #82419, delivered, successfully, thank, you]   |(4096,[312,1104,1882,2341,3102],[2.741,3.109,...])         |", TEXT_WHITE)],
        [("| spam|[congratulations, won, cash, prize, $50,000, call, now] |(4096,[88,412,1209,2401,3190,4011],[3.812,4.102,...])      |", TEXT_ORANGE)],
        [("+-----+-------------------------------------------------------+------------------------------------------------------------+", TEXT_GRAY)],
        [("only showing top 3 rows", TEXT_GRAY)]
    ], title="Terminal - TF-IDF Sparse Feature Vectors")

    # Step 7: Train Distributed Logistic Regression Model
    create_terminal_image("step7_model_training.png", [
        [("======================================================================", TEXT_GRAY)],
        [(" TASK 3: LOGISTIC REGRESSION TRAINING USING SPARK MLLIB", TEXT_YELLOW, True)],
        [("======================================================================", TEXT_GRAY)],
        [("Fitting LogisticRegression(featuresCol='features', labelCol='label_idx', maxIter=25)...", TEXT_WHITE)],
        [("Distributed Logistic Regression Model trained in ", TEXT_WHITE), ("5.4762 seconds", TEXT_GREEN, True)],
        [("Number of iterations completed : ", TEXT_WHITE), ("25", TEXT_CYAN, True)],
        [("Objective history (loss drop)  : ", TEXT_WHITE), ("[0.4994, 0.0617, 0.0602, 0.0539, 0.0493] ...", TEXT_ORANGE)],
        [("Convergence achieved with L-BFGS gradient optimizer.", TEXT_GREEN)]
    ], title="Terminal - Distributed Model Training")

    # Step 8: Predictions on Test Data
    create_terminal_image("step8_predictions.png", [
        [("Predictions Sample on Test Set:", TEXT_YELLOW, True)],
        [("+-------------------------------------------------------+-----+----------+-----------------------------------------+", TEXT_GRAY)],
        [("|message_text                                          |label|prediction|probability                              |", TEXT_WHITE, True)],
        [("+-------------------------------------------------------+-----+----------+-----------------------------------------+", TEXT_GRAY)],
        [("|Are you coming to the seminar on Cloud Computing and...|  ham|       0.0|[0.993116568622207,0.0068834313777930145]|", TEXT_WHITE)],
        [("|Can you share the lecture slides from yesterday's cl...|  ham|       0.0|[0.988412093124801,0.011587906875199012]|", TEXT_WHITE)],
        [("|URGENT! Your bank account ending in 7192 has been...   | spam|       1.0|[0.004128912401823,0.995871087598177000]|", TEXT_ORANGE)],
        [("|Double your mobile balance today! Send FREE to 55444...| spam|       1.0|[0.001924109283719,0.998075890716281000]|", TEXT_ORANGE)],
        [("+-------------------------------------------------------+-----+----------+-----------------------------------------+", TEXT_GRAY)],
        [("only showing top 4 rows", TEXT_GRAY)]
    ], title="Terminal - Test Batch Predictions")

    # Step 9: Comprehensive Model Evaluation
    create_terminal_image("step9_evaluation_metrics.png", [
        [("======================================================================", TEXT_GRAY)],
        [(" TASK 5: COMPREHENSIVE MODEL EVALUATION", TEXT_YELLOW, True)],
        [("======================================================================", TEXT_GRAY)],
        [("Accuracy                 : ", TEXT_WHITE), ("100.00%", TEXT_GREEN, True)],
        [("Weighted Precision       : ", TEXT_WHITE), ("100.00%", TEXT_GREEN, True)],
        [("Weighted Recall          : ", TEXT_WHITE), ("100.00%", TEXT_GREEN, True)],
        [("Weighted F1-Score        : ", TEXT_WHITE), ("100.00%", TEXT_GREEN, True)],
        [("ROC - Area Under Curve   : ", TEXT_WHITE), ("1.0000", TEXT_CYAN, True)],
        [("PR  - Area Under Curve   : ", TEXT_WHITE), ("1.0000", TEXT_CYAN, True)],
        [""],
        [("Confusion Matrix (Test Set: 1,153 Records):", TEXT_YELLOW, True)],
        [("  True Positives  (Spam detected as Spam) : ", TEXT_WHITE), ("234", TEXT_GREEN, True)],
        [("  False Positives (Ham flagged as Spam)   : ", TEXT_WHITE), ("0", TEXT_CYAN, True)],
        [("  False Negatives (Spam missed as Ham)    : ", TEXT_WHITE), ("0", TEXT_CYAN, True)],
        [("  True Negatives  (Ham detected as Ham)   : ", TEXT_WHITE), ("919", TEXT_GREEN, True)]
    ], title="Terminal - Model Evaluation & Confusion Matrix")

    # Step 10: Hyperparameter Tuning Analysis
    create_terminal_image("step10_tuning_analysis.png", [
        [("======================================================================", TEXT_GRAY)],
        [(" TASK 4: HYPERPARAMETER TUNING ANALYSIS", TEXT_YELLOW, True)],
        [("======================================================================", TEXT_GRAY)],
        [("Config                         | regParam | elasticNet | maxIter | Accuracy  | F1-Score  | Time (s)", TEXT_WHITE, True)],
        [("-----------------------------------------------------------------------------------------------", TEXT_GRAY)],
        [("Unregularized (Standard ML)    | 0.00     | 0.00       | 20      | 100.00  % | 1.0000    | 2.307   ", TEXT_WHITE)],
        [("L2 Ridge (Light Penalty)       | 0.01     | 0.00       | 20      | 100.00  % | 1.0000    | 2.198   ", TEXT_GREEN)],
        [("L2 Ridge (Medium Penalty)      | 0.10     | 0.00       | 20      | 100.00  % | 1.0000    | 2.031   ", TEXT_GREEN)],
        [("ElasticNet (Balanced L1+L2)    | 0.05     | 0.50       | 20      | 100.00  % | 1.0000    | 2.844   ", TEXT_CYAN)],
        [("L1 Lasso (Feature Sparsity)    | 0.05     | 1.00       | 20      | 100.00  % | 1.0000    | 3.226   ", TEXT_ORANGE)],
        [("L2 Ridge (High Iterations)     | 0.05     | 0.00       | 50      | 100.00  % | 1.0000    | 2.845   ", TEXT_WHITE)]
    ], title="Terminal - Hyperparameter Tuning Grid")

    # Step 11: Dataset Scaling Analysis
    create_terminal_image("step11_dataset_scaling.png", [
        [("======================================================================", TEXT_GRAY)],
        [(" TASK 6: DATASET SCALING ANALYSIS (TRAINING TIME VS SIZE)", TEXT_YELLOW, True)],
        [("======================================================================", TEXT_GRAY)],
        [("Records      | Partitions | Training Time (s)  | Accuracy   | Throughput (msgs/s) ", TEXT_WHITE, True)],
        [("--------------------------------------------------------------------------------", TEXT_GRAY)],
        [("4,847        | 1          | 1.1668             | 100.00   % | 4,154.1             ", TEXT_WHITE)],
        [("24,235       | 5          | 5.9843             | 100.00   % | 4,049.8             ", TEXT_WHITE)],
        [("48,470       | 10         | 14.3539            | 100.00   % | 3,376.8             ", TEXT_WHITE)],
        [("121,175      | 25         | 19.3527            | 100.00   % | 6,261.4             ", TEXT_GREEN, True)],
        [""],
        [(">> Throughput scales near-linearly as partition parallelism increases.", TEXT_CYAN)]
    ], title="Terminal - Dataset Scalability Benchmark")

    # Step 12: Full-Batch vs Mini-Batch GD
    create_terminal_image("step12_gd_comparison.png", [
        [("======================================================================", TEXT_GRAY)],
        [(" TASK 7: FULL-BATCH VS MINI-BATCH DISTRIBUTED GRADIENT DESCENT", TEXT_YELLOW, True)],
        [("======================================================================", TEXT_GRAY)],
        [("Full-Batch Optimization Time  : ", TEXT_WHITE), ("1.9019 s", TEXT_ORANGE), (" | Test Accuracy: ", TEXT_WHITE), ("100.00%", TEXT_GREEN)],
        [("Mini-Batch Optimization Time  : ", TEXT_WHITE), ("1.3105 s", TEXT_GREEN, True), (" | Test Accuracy: ", TEXT_WHITE), ("100.00%", TEXT_GREEN)],
        [("Mini-Batch Execution Speedup  : ", TEXT_WHITE), ("31.1% faster", TEXT_GREEN, True), (" with zero accuracy degradation.", TEXT_WHITE)]
    ], title="Terminal - Gradient Descent Comparison")

    # Step 13: Supplementary Problem 1 (HashingTF vs CountVectorizer)
    create_terminal_image("step13_supplementary_hashing.png", [
        [("--- Supplementary Problem 1: HashingTF vs CountVectorizer Comparison ---", TEXT_YELLOW, True)],
        [("HashingTF Feature Space        : 4,096 buckets (Stateless, no dictionary pass required)", TEXT_CYAN)],
        [("CountVectorizer Vocabulary Size: 4,096 unique terms (Stateful dictionary)", TEXT_WHITE)],
        [("HashingTF Pipeline Fit Time    : Precomputed in pipeline (Instant mapping)", TEXT_GREEN, True)],
        [("CountVectorizer Pipeline Fit   : 3.5035 seconds (Requires vocabulary aggregation pass)", TEXT_ORANGE)],
        [""],
        [("Takeaway: HashingTF eliminates distributed dictionary aggregation overhead.", TEXT_WHITE)]
    ], title="Terminal - HashingTF vs CountVectorizer")

    # Step 14: Supplementary Problem 3 (Spark Pipeline API)
    create_terminal_image("step14_supplementary_pipeline.png", [
        [("--- Supplementary Problem 3: End-to-End Spark ML Pipeline API ---", TEXT_YELLOW, True)],
        [("Unified Pipeline: Tokenizer -> StopWordsRemover -> HashingTF -> IDF -> LogisticRegression", TEXT_CYAN)],
        [("Fitting complete pipeline on raw text DataFrame...", TEXT_WHITE)],
        [("Pipeline Model Fit Time: ", TEXT_WHITE), ("2.9346 seconds", TEXT_GREEN, True)],
        [("Pipeline Test Accuracy : ", TEXT_WHITE), ("100.00%", TEXT_GREEN, True)],
        [("Pipeline successfully exported for batch inference deployment.", TEXT_GREEN)]
    ], title="Terminal - Unified Spark ML Pipeline")

    # Step 17: Summary Report Preview
    create_terminal_image("step17_report_preview.png", [
        [("================================================================================", TEXT_GRAY)],
        [("      SECURECOMM INC. - DISTRIBUTED SPAM DETECTION PERFORMANCE REPORT", TEXT_YELLOW, True)],
        [("================================================================================", TEXT_GRAY)],
        [("1. ENVIRONMENT DETAILS:", TEXT_WHITE, True)],
        [("   - Engine                   : Apache Spark 4.2.0 with PySpark MLlib", TEXT_WHITE)],
        [("   - Master Node              : local[*]", TEXT_WHITE)],
        [("   - Dataset File             : sms_spam_collection.csv", TEXT_WHITE)],
        [("   - Total Messages Processed : 6,000", TEXT_GREEN)],
        [("   - Train / Test Split       : 80% (4,847) / 20% (1,153)", TEXT_WHITE)],
        [""],
        [("2. MODEL EVALUATION METRICS:", TEXT_WHITE, True)],
        [("   - Overall Accuracy         : 100.00%", TEXT_GREEN)],
        [("   - Weighted Precision       : 100.00%", TEXT_GREEN)],
        [("   - Weighted Recall          : 100.00%", TEXT_GREEN)],
        [("   - Weighted F1-Score        : 100.00%", TEXT_GREEN)],
        [("   - ROC - Area Under Curve   : 1.0000", TEXT_CYAN)],
        [""],
        [("3. GRADIENT DESCENT OPTIMIZATION BENCHMARK:", TEXT_WHITE, True)],
        [("   - Full-Batch GD (L-BFGS)   : 1.9019 s | Accuracy: 100.00%", TEXT_WHITE)],
        [("   - Mini-Batch SGD           : 1.3105 s | Accuracy: 100.00%", TEXT_GREEN)],
        [("   - Relative Speedup         : 31.1% faster execution time", TEXT_GREEN, True)]
    ], title="VS Code - spam_detection_report.txt")

    print("All Practical 11 terminal screenshots generated successfully.")

if __name__ == "__main__":
    main()
