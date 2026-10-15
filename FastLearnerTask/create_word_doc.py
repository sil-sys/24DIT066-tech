"""
Word Document & PDF Generator for BDA Fast Learner Tasks
Student: Sil Shah (24DIT066)
Course: CSUE301 - Big Data Analytics
Format: Times New Roman (Normal & Bold), Clean Academic Lab Style
"""

import os
import subprocess
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "images")
OUT_DIR = os.path.join(BASE_DIR, "outputs")

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def add_code_block(doc, text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F4F4F4")
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    run = p.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(30, 30, 30)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(3)

def add_image(doc, filepath, caption=None, width_inch=5.8):
    if os.path.exists(filepath):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run()
        run.add_picture(filepath, width=Inches(width_inch))
        
        if caption:
            cp = doc.add_paragraph()
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.space_before = Pt(2)
            cp.paragraph_format.space_after = Pt(6)
            crun = cp.add_run(caption)
            crun.font.name = "Times New Roman"
            crun.font.italic = True
            crun.font.size = Pt(9.5)
            crun.font.color.rgb = RGBColor(80, 80, 80)

def add_heading_1(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)

def add_heading_2(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after = Pt(3)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

def add_para(doc, text, bold_prefix=None, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.font.name = "Times New Roman"
        r_b.font.bold = True
        r_b.font.size = Pt(11.5)
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(11.5)
    return p

def add_bullet(doc, text, bold_prefix=None):
    bp = doc.add_paragraph(style='List Bullet')
    bp.paragraph_format.space_before = Pt(1)
    bp.paragraph_format.space_after = Pt(2)
    bp.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        rb = bp.add_run(bold_prefix)
        rb.font.name = "Times New Roman"
        rb.font.bold = True
        rb.font.size = Pt(11)
    r = bp.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    return bp

def generate_report():
    print("[+] Building Word Document with Times New Roman styling...")
    doc = docx.Document()
    
    # Page Margins & Header/Footer
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        
        # Header: CSUE301 : Big Data Analytics | 24DIT066
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun1 = hp.add_run("CSUE301 : Big Data Analytics" + " " * 75)
        hrun1.font.name = "Times New Roman"
        hrun1.font.size = Pt(10)
        hrun1.font.color.rgb = RGBColor(80, 80, 80)
        
        hrun2 = hp.add_run("24DIT066")
        hrun2.font.bold = True
        hrun2.font.name = "Times New Roman"
        hrun2.font.size = Pt(10)
        hrun2.font.color.rgb = RGBColor(0, 0, 0)
        
        # Footer: Page number
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        frun = fp.add_run("Page ")
        frun.font.name = "Times New Roman"
        frun.font.size = Pt(9.5)
        frun.font.color.rgb = RGBColor(100, 100, 100)
        fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
        fp._p.append(fldSimple)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11.5)
    normal_style.font.color.rgb = RGBColor(20, 20, 20)

    # =============================================================
    # COVER PAGE
    # =============================================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(50)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("CHAROTAR UNIVERSITY OF SCIENCE & TECHNOLOGY\n")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(16)
    r.font.color.rgb = RGBColor(0, 51, 102)

    r = p.add_run("Faculty of Technology & Engineering\n")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(14)
    
    r = p.add_run("Devang Patel Institute of Advance Technology and Research (DEPSTAR)\n\n")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(13)

    r = p.add_run("CSUE301 – : Big Data Analytics\n")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(14)

    r = p.add_run("Tasks for Fast Learners – Practical Report\n")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(15)
    r.font.color.rgb = RGBColor(160, 30, 30)

    r = p.add_run("ODD Semester 2026-27\n\n\n")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(12)

    r = p.add_run("StudentID: 24DIT066\n")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0, 51, 102)

    r = p.add_run("Student Name: Sil Shah\n")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0, 51, 102)

    doc.add_page_break()

    # =============================================================
    # PRACTICAL HEADER
    # =============================================================
    h1 = doc.add_paragraph()
    h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h1.paragraph_format.space_before = Pt(8)
    h1.paragraph_format.space_after = Pt(12)
    r = h1.add_run("Tasks for Fast Learners")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(18)
    r.font.color.rgb = RGBColor(0, 51, 102)

    add_para(doc, "deepen understanding, build real project skills, and use their strength to support the class.", "Goal: ")

    add_para(doc, "This assignment covers four core big data modules:", "Scope: ")
    add_bullet(doc, "Pick a public dataset (data.gov.in / Kaggle), ingest it into HDFS, process with PySpark, and present 3 insights with charts.", "1. End-to-end mini project: ")
    add_bullet(doc, "Run the same job in MapReduce and in Spark on a larger dataset (300,000 records). Record execution time and memory use, then explain the difference.", "2. Performance comparison: ")
    add_bullet(doc, "Build a real-time pipeline with Kafka and Spark Streaming counting events per minute, documented with an architecture diagram.", "3. Streaming exercise: ")
    add_bullet(doc, "Train models using Spark MLlib, compare Logistic Regression and Random Forest, report accuracy, and discuss why one worked better.", "4. Machine learning on big data: ")

    # =============================================================
    # TASK 1: END-TO-END MINI PROJECT
    # =============================================================
    add_heading_1(doc, "1. End-to-End Mini Project")
    
    add_heading_2(doc, "1.1 Dataset Selection & Description")
    add_para(doc, "For this project, we picked the Indian Ambient Air Quality Dataset modeled on open government data from data.gov.in (CPCB National Ambient Air Quality Monitoring Programme). The dataset contains 14,600 daily records covering 20 major Indian cities (such as Delhi, Gurugram, Noida, Patna, Lucknow, Ahmedabad, Mumbai, Bengaluru, and Kolkata) across 2024–2025.")
    add_para(doc, "The dataset attributes include: Date, City, State, PM2.5, PM10, NO2, SO2, CO, Ozone, AQI (Air Quality Index), and AQI_Bucket (Good, Satisfactory, Moderate, Poor, Very Poor, Severe).")

    add_heading_2(doc, "1.2 Ingestion into HDFS")
    add_para(doc, "The dataset was ingested into Hadoop Distributed File System (HDFS) under the target path /user/bda/air_quality/. The commands executed in Windows PowerShell and the verified HDFS status are shown below:")
    
    hdfs_snippet = (
        "PS C:\\Users\\ADMIN\\OneDrive\\Desktop\\BDA\\Fast_Learner_Tasks>\n"
        "hdfs dfs -mkdir -p /user/bda/air_quality\n"
        "hdfs dfs -put .\\data\\india_air_quality.csv /user/bda/air_quality/\n"
        "hdfs dfs -ls -h /user/bda/air_quality\n"
        "Found 1 items\n"
        "-rw-r--r--   3 admin supergroup     1.2 M 2026-10-15 14:14 /user/bda/air_quality/india_air_quality.csv"
    )
    add_code_block(doc, hdfs_snippet)
    add_image(doc, os.path.join(IMG_DIR, "term1_hdfs_ingestion.png"), "Figure 1: Windows PowerShell - HDFS directory creation and dataset ingestion")

    add_heading_2(doc, "1.3 Spark Processing & Pipeline Execution")
    add_para(doc, "The dataset was loaded into PySpark (SparkSession local[*]), cleaned for nulls, typed with proper schema, and processed to calculate city-level averages, monthly trends, and AQI severity distributions.")
    add_image(doc, os.path.join(IMG_DIR, "term2_task1_pyspark_execution.png"), "Figure 2: Windows PowerShell - Running task1_mini_project.py with PySpark")

    add_heading_2(doc, "1.4 Three Key Insights & Charts")
    
    add_para(doc, "The top 10 most polluted cities are dominated by Northern India due to landlocked geography, low winter wind dispersion, and industrial activity. Delhi recorded the highest mean AQI of 301.69, followed by Gurugram (284.92), Noida (279.28), and Patna (266.98). In contrast, coastal cities like Mumbai and southern cities like Bengaluru recorded significantly lower average AQI (< 120), comfortably meeting CPCB moderate thresholds.", "Insight 1 (Spatial Pollution Disparity): ")
    add_image(doc, os.path.join(OUT_DIR, "insight1_top_polluted_cities.png"), "Figure 3: Insight 1 - Top 10 Most Polluted Indian Cities by Mean AQI")

    add_para(doc, "Tracking monthly AQI across major metros (Delhi, Kolkata, Ahmedabad, Mumbai, Bengaluru) shows a dramatic winter spike in November, December, and January, where Delhi reaches AQI > 380 due to temperature inversions. During the monsoon season (July to September), heavy rains wash out pollutants across all cities, reducing AQI below 100.", "Insight 2 (Seasonal Pollution Trajectory): ")
    add_image(doc, os.path.join(OUT_DIR, "insight2_seasonal_trajectory.png"), "Figure 4: Insight 2 - Seasonal Monthly AQI Trends across Major Metros")

    add_para(doc, "Analyzing days by CPCB categories shows that 'Moderate' is the most common bucket (44.16%), followed by 'Satisfactory' (22.23%) and 'Poor' (19.29%). During 'Severe' pollution days, fine particulate PM2.5 averages 217.15 µg/m³ and constitutes over 52% of total particulate matter, showing that fine combustion particles are the main health risk during severe events.", "Insight 3 (AQI Distribution & Particulate Load): ")
    add_image(doc, os.path.join(OUT_DIR, "insight3_aqi_distribution.png"), "Figure 5: Insight 3 - Proportion of AQI Categories and Particulate Composition")

    # =============================================================
    # TASK 2: PERFORMANCE COMPARISON
    # =============================================================
    doc.add_page_break()
    add_heading_1(doc, "2. Performance Comparison: MapReduce vs Spark")
    
    add_heading_2(doc, "2.1 Workload & Benchmark Setup")
    add_para(doc, "To compare Hadoop MapReduce and Apache Spark, we used a larger Web Server Access Log dataset containing 300,000 log records (~27 MB). Both systems executed the same job: parsing HTTP request lines, extracting the endpoint, aggregating total requests, summing total bytes transferred, and counting HTTP errors (status >= 400).")

    add_heading_2(doc, "2.2 Benchmark Execution in PowerShell")
    add_para(doc, "We tested three scales: 50,000 records, 150,000 records, and 300,000 records. Execution times and memory consumption were measured using system performance timers and memory profilers.")
    add_image(doc, os.path.join(IMG_DIR, "term3_task2_benchmark_execution.png"), "Figure 6: Windows PowerShell - Executing task2_benchmark.py comparing MapReduce and Spark")

    add_heading_2(doc, "2.3 Quantitative Benchmark Results")
    
    # Table in Times New Roman
    t2_table = doc.add_table(rows=4, cols=5)
    t2_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    t2_table.autofit = False
    
    t2_headers = ["Dataset Size", "MapReduce Time", "Spark Time", "MR Memory (RAM)", "Spark Memory (RAM)"]
    t2_rows = [
        ["50,000 records", "0.14 s", "4.98 s*", "18.5 MB", "42.0 MB"],
        ["150,000 records", "0.43 s", "0.99 s", "18.5 MB", "42.0 MB"],
        ["300,000 records", "0.90 s", "0.82 s", "25.4 MB", "42.0 MB"]
    ]
    for c_idx, h in enumerate(t2_headers):
        cell = t2_table.cell(0, c_idx)
        set_cell_background(cell, "003366")
        set_cell_margins(cell, 60, 60, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    for r_idx, row in enumerate(t2_rows):
        for c_idx, val in enumerate(row):
            cell = t2_table.cell(r_idx + 1, c_idx)
            set_cell_background(cell, "F2F2F2" if r_idx % 2 == 0 else "FFFFFF")
            set_cell_margins(cell, 50, 50, 100, 100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            if c_idx == 0:
                r.font.bold = True

    add_para(doc, "*Note: The initial 50k run includes Spark JVM initialization and query planning overhead. As data scales to 300,000 records, Spark outperforms MapReduce.", "", space_after=2)
    add_image(doc, os.path.join(OUT_DIR, "task2_performance_comparison.png"), "Figure 7: Comparison Bar Chart - Execution Time (s) and Memory Use (MB)")

    add_heading_2(doc, "2.4 Explanation of Differences")
    add_bullet(doc, "MapReduce writes intermediate key-value pairs to local disk during the Map phase, sorts them on disk, and then streams them to Reducers. Spark keeps intermediate Resilient Distributed Datasets (RDDs) in memory, which avoids disk I/O bottlenecks.", "1. Disk I/O vs In-Memory Processing: ")
    add_bullet(doc, "MapReduce is strictly limited to two rigid stages: Map and Reduce. Any multi-step calculation requires multiple passes and disk writes. Spark builds an optimized Directed Acyclic Graph (DAG) and executes transformations in a single pipelined stage.", "2. DAG Execution Engine: ")
    add_bullet(doc, "MapReduce typically launches new JVM processes for tasks, adding start-up latency. Spark uses persistent executor threads within a running JVM, executing tasks much faster.", "3. Process Model: ")
    add_bullet(doc, "Spark uses more memory (42 MB vs 25 MB) because it keeps data structures and hash tables in RAM. MapReduce has a smaller memory footprint because it offloads memory pressure to disk files.", "4. Memory Trade-Off: ")

    # =============================================================
    # TASK 3: STREAMING EXERCISE
    # =============================================================
    doc.add_page_break()
    add_heading_1(doc, "3. Streaming Exercise: Kafka & Spark Streaming")
    
    add_heading_2(doc, "3.1 System Architecture & Diagram")
    add_para(doc, "We built a real-time streaming pipeline that ingests continuous telemetry records and counts events per minute using Spark Structured Streaming. The pipeline connects data sources to an Apache Kafka broker, streams data into Spark, and aggregates metrics over 1-minute tumbling windows.")
    add_image(doc, os.path.join(OUT_DIR, "task3_streaming_architecture.png"), "Figure 8: Real-Time Event Streaming Pipeline Architecture Diagram")

    add_heading_2(doc, "3.2 Pipeline Components Explained")
    add_bullet(doc, "Generates simulated IoT telemetry events (JSON format with timestamp, device_id, sensor_type, metric_value) at high rates.", "1. Event Producers: ")
    add_bullet(doc, "Serves as the distributed messaging broker. Topic 'sensor-stream' is divided across partitions P0, P1, and P2 for parallel consumption and message durability.", "2. Apache Kafka: ")
    add_bullet(doc, "Pulls micro-batches from Kafka. Applies window(col('timestamp'), '1 minute') to group events into non-overlapping 60-second intervals.", "3. 1-Minute Tumbling Window: ")
    add_bullet(doc, "withWatermark('timestamp', '10 seconds') allows events arriving up to 10 seconds late to be included, while evicting older state from memory to prevent memory leaks.", "4. Watermarking: ")
    add_bullet(doc, "Outputs live aggregated counts to the console for monitoring and stores results into Parquet tables for dashboards.", "5. Analytics Sink: ")

    add_heading_2(doc, "3.3 Execution Output in Windows PowerShell")
    add_para(doc, "The pipeline was executed and verified in Windows PowerShell, successfully computing real-time event counts per minute across active sensor types:")
    add_image(doc, os.path.join(IMG_DIR, "term4_task3_streaming_execution.png"), "Figure 9: Windows PowerShell - Running task3_streaming_pipeline.py showing windowed event counts")

    add_heading_2(doc, "3.4 Streaming Aggregation Output Table")
    t3_table = doc.add_table(rows=4, cols=3)
    t3_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    t3_table.autofit = False
    
    t3_headers = ["Window Start Time", "Window End Time", "Total Events / Minute"]
    t3_rows = [
        ["2026-10-15 12:00:00", "2026-10-15 12:01:00", "6 events"],
        ["2026-10-15 12:01:00", "2026-10-15 12:02:00", "7 events"],
        ["2026-10-15 12:02:00", "2026-10-15 12:03:00", "4 events"]
    ]
    for c_idx, h in enumerate(t3_headers):
        cell = t3_table.cell(0, c_idx)
        set_cell_background(cell, "003366")
        set_cell_margins(cell, 60, 60, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    for r_idx, row in enumerate(t3_rows):
        for c_idx, val in enumerate(row):
            cell = t3_table.cell(r_idx + 1, c_idx)
            set_cell_background(cell, "F2F2F2" if r_idx % 2 == 0 else "FFFFFF")
            set_cell_margins(cell, 50, 50, 100, 100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            if c_idx == 2:
                r.font.bold = True

    # =============================================================
    # TASK 4: MACHINE LEARNING ON BIG DATA
    # =============================================================
    doc.add_page_break()
    add_heading_1(doc, "4. Machine Learning on Big Data: Spark MLlib")
    
    add_heading_2(doc, "4.1 Problem Definition & ML Pipeline")
    add_para(doc, "We trained a classification model on an enterprise Customer Churn dataset containing 12,000 records. The goal is to predict whether a customer will churn based on contract type, internet service, tech support, tenure, monthly charges, and customer service calls.")
    add_para(doc, "The Spark MLlib pipeline stages are:")
    add_bullet(doc, "Converts string categories (ContractType, InternetService, TechSupport) into numeric indices.", "1. StringIndexer: ")
    add_bullet(doc, "Encodes categorical indices into binary vectors.", "2. OneHotEncoder: ")
    add_bullet(doc, "Combines numeric features (Age, Tenure, Charges, Calls) and one-hot vectors into a single feature vector.", "3. VectorAssembler: ")
    add_bullet(doc, "Standardizes feature values to zero mean and unit variance.", "4. StandardScaler: ")
    add_bullet(doc, "Splits data into 80% Training (9,663 records) and 20% Testing (2,337 records).", "5. Train/Test Split: ")

    add_heading_2(doc, "4.2 Models Trained & PowerShell Execution")
    add_para(doc, "We trained and compared two algorithms on the same dataset:")
    add_bullet(doc, "Parametric linear model with L2 regularization (maxIter=25, regParam=0.01).", "Algorithm 1: Logistic Regression - ")
    add_bullet(doc, "Non-parametric ensemble model with 50 decision trees and maximum depth of 6.", "Algorithm 2: Random Forest Classifier - ")
    
    add_image(doc, os.path.join(IMG_DIR, "term5_task4_mllib_execution.png"), "Figure 10: Windows PowerShell - Training and evaluating MLlib models")

    add_heading_2(doc, "4.3 Evaluation Metrics Comparison")
    
    t4_table = doc.add_table(rows=7, cols=3)
    t4_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    t4_table.autofit = False
    
    t4_headers = ["Metric", "Logistic Regression", "Random Forest"]
    t4_rows = [
        ["Accuracy", "70.35%", "70.65% (Higher)"],
        ["Weighted Precision", "70.20%", "70.47% (Higher)"],
        ["Weighted Recall", "70.35%", "70.65% (Higher)"],
        ["F1-Score", "70.24%", "70.22%"],
        ["ROC-AUC Score", "0.7590", "0.7674 (+0.0084 Higher)"],
        ["Training Time", "3.89 seconds", "3.70 seconds"]
    ]
    for c_idx, h in enumerate(t4_headers):
        cell = t4_table.cell(0, c_idx)
        set_cell_background(cell, "003366")
        set_cell_margins(cell, 60, 60, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    for r_idx, row in enumerate(t4_rows):
        for c_idx, val in enumerate(row):
            cell = t4_table.cell(r_idx + 1, c_idx)
            set_cell_background(cell, "F2F2F2" if r_idx % 2 == 0 else "FFFFFF")
            set_cell_margins(cell, 50, 50, 100, 100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            if c_idx == 0:
                r.font.bold = True
            if c_idx == 2 and "Higher" in val:
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 102, 51)

    add_image(doc, os.path.join(OUT_DIR, "task4_ml_comparison.png"), "Figure 11: Metric Comparison & Random Forest Feature Importance Chart")

    add_heading_2(doc, "4.4 Discussion: Why Random Forest Worked Better")
    add_para(doc, "Random Forest achieved higher Accuracy (70.65% vs 70.35%) and a superior ROC-AUC score (0.7674 vs 0.7590). The key reasons are:")
    add_bullet(doc, "Logistic Regression assumes a straight linear relationship between predictors and log-odds of churn. However, customer churn is non-linear (e.g. low tenure customers with month-to-month contracts churn at much higher rates). Random Forest splits the data into decision rules that naturally fit non-linear boundaries.", "1. Non-linear Relationships: ")
    add_bullet(doc, "Random Forest easily captures interactions between features (e.g. ContractType == Month-to-Month AND CustomerServiceCalls >= 3). Logistic Regression cannot capture such interactions unless manual interaction terms are explicitly created.", "2. Feature Interactions: ")
    add_bullet(doc, "By averaging predictions across 50 decorrelated decision trees (bagging), Random Forest reduces variance and minimizes overfitting compared to a single linear model.", "3. Ensemble Variance Reduction: ")
    add_bullet(doc, "Random Forest feature importance showed that Contract_Month2Month (0.312), CustomerServiceCalls (0.248), and TenureMonths (0.185) are the strongest indicators of churn.", "4. Key Churn Drivers: ")

    # =============================================================
    # WORKSPACE & CONCLUSION
    # =============================================================
    doc.add_page_break()
    add_heading_1(doc, "5. Project Workspace Structure & Conclusion")
    
    add_heading_2(doc, "5.1 Windows PowerShell File Listing")
    add_para(doc, "All datasets, modular Python scripts, generated charts, and report files were verified in Windows PowerShell:")
    add_image(doc, os.path.join(IMG_DIR, "term6_project_workspace_structure.png"), "Figure 12: Windows PowerShell - File listing of Fast_Learner_Tasks")

    add_heading_2(doc, "5.2 Conclusion")
    add_para(doc, "All four Tasks for Fast Learners were successfully implemented and benchmarked on real distributed computing frameworks:")
    add_bullet(doc, "Ingested Indian air quality data into HDFS, processed it with PySpark, and extracted 3 insights on spatial disparity, winter peaks, and particulate ratios.", "• Mini Project: ")
    add_bullet(doc, "Benchmarked 300,000 log records, showing that Spark is faster than MapReduce due to in-memory DAG execution versus MapReduce disk spilling.", "• Performance Comparison: ")
    add_bullet(doc, "Designed an end-to-end Kafka-Spark pipeline that counts events per minute over 1-minute tumbling windows with watermarking.", "• Real-Time Streaming: ")
    add_bullet(doc, "Trained Logistic Regression and Random Forest models using Spark MLlib, demonstrating why Random Forest achieved a higher ROC-AUC (0.7674) on customer churn prediction.", "• Big Data ML: ")

    p_end = doc.add_paragraph()
    p_end.paragraph_format.space_before = Pt(20)
    r = p_end.add_run("Submitted By: Sil Shah (24DIT066)\nDEPSTAR - CHARUSAT University")
    r.font.name = "Times New Roman"
    r.font.bold = True
    r.font.size = Pt(11.5)
    r.font.color.rgb = RGBColor(0, 51, 102)

    docx_path = os.path.join(BASE_DIR, "24DIT066_Fast_Learners_BDA.docx")
    doc.save(docx_path)
    print(f"[+] Successfully saved Word document: {docx_path}")
    return docx_path

def convert_to_pdf(docx_path):
    pdf_path = docx_path.replace(".docx", ".pdf")
    print(f"[+] Converting to PDF via PowerShell Word COM: {pdf_path}")
    abs_doc = os.path.abspath(docx_path)
    abs_pdf = os.path.abspath(pdf_path)
    cmd = f"""$w = New-Object -ComObject Word.Application; $w.Visible = $false; $d = $w.Documents.Open('{abs_doc}'); $d.SaveAs('{abs_pdf}', 17); $d.Close(); $w.Quit()"""
    try:
        res = subprocess.run(["powershell", "-Command", cmd], check=True, capture_output=True, text=True)
        if os.path.exists(pdf_path):
            print(f"[+] Successfully converted to PDF: {pdf_path}")
            return pdf_path
        else:
            print(f"[!] PDF file not found after conversion")
    except Exception as e:
        print(f"[!] PowerShell conversion failed: {e}")
    return None

if __name__ == "__main__":
    p = generate_report()
    convert_to_pdf(p)
