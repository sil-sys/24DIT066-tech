"""
Word Document Generator for BDA Practical 11
Matching Practical 8 Lab Manual Structure with Real Terminal Screenshots
Author: Sil Shah (24DIT066)
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "images")

def add_screenshot(doc, img_path, width_inch=5.8):
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(8)
        run = p.add_run()
        run.add_picture(img_path, width=Inches(width_inch))

def generate_doc():
    doc = docx.Document()
    
    # Page Margins & Header/Footer
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        
        # Header: CSUE301 : Big Data Analytics (Left) | 24DIT066 (Right)
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Add left text with tabs or simple space
        hrun1 = hp.add_run("CSUE301 : Big Data Analytics" + " " * 85)
        hrun1.font.name = "Calibri"
        hrun1.font.size = Pt(9.5)
        hrun1.font.color.rgb = RGBColor(60, 60, 60)
        
        hrun2 = hp.add_run("24DIT066")
        hrun2.font.bold = True
        hrun2.font.name = "Calibri"
        hrun2.font.size = Pt(9.5)
        hrun2.font.color.rgb = RGBColor(0, 0, 0)
        
        # Footer: Page number
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        frun = fp.add_run("")
        fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
        fp._p.append(fldSimple)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 30, 30)

    # ------------------ PAGE 1: COVER PAGE ------------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(60)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("CHAROTAR UNIVERSITY OF SCIENCE & TECHNOLOGY\n")
    r.font.bold = True
    r.font.size = Pt(16)
    r.font.color.rgb = RGBColor(0, 51, 102)

    r = p.add_run("Faculty of Technology & Engineering\n")
    r.font.bold = True
    r.font.size = Pt(14)
    
    r = p.add_run("Devang Patel Institute of Advance Technology and Research (DEPSTAR)\n\n")
    r.font.bold = True
    r.font.size = Pt(13)

    r = p.add_run("CSUE301 – : Big Data Analytics\n")
    r.font.bold = True
    r.font.size = Pt(14)

    r = p.add_run("Practical File – ODD Semester 2026-27\n\n")
    r.font.bold = True
    r.font.size = Pt(13)

    r = p.add_run("StudentID: 24DIT066\n")
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0, 51, 102)

    r = p.add_run("Student Name: Sil Shah\n")
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0, 51, 102)

    doc.add_page_break()

    # ------------------ PAGE 2: PRACTICAL 11 ------------------
    h1 = doc.add_paragraph()
    h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h1.paragraph_format.space_before = Pt(8)
    h1.paragraph_format.space_after = Pt(12)
    r = h1.add_run("Practical 11")
    r.font.bold = True
    r.font.size = Pt(18)
    r.font.color.rgb = RGBColor(0, 51, 102)

    # Problem Definition
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("1. Problem Definition\n")
    r.font.bold = True
    r.font.size = Pt(12)
    doc.add_paragraph(
        "You are a Big Data Engineer at SecureComm Inc., a telecom company that processes over 50 million "
        "SMS messages daily. The fraud prevention team wants an automated spam classifier that can scale to "
        "handle millions of new messages per hour. You will implement a Distributed Logistic Regression model "
        "using Mini-batch Gradient Descent on Apache Spark, train it on a massive SMS dataset, and deploy it for batch prediction."
    )

    # PART A
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("PART A — Practical Execution\n")
    r.font.bold = True
    r.font.size = Pt(12)

    # Step 1
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 1: Creating Folder and files")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step1_folder.png"), 3.2)

    # Step 2
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 2: Creating Spark Session")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step2_spark_session.png"), 5.8)

    # Step 3
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 3: Loading SMS Spam Dataset")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step3_load_dataset.png"), 5.8)

    # Step 4
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 4: Display Dataset Schema and Class Distribution")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step4_schema_distribution.png"), 5.8)

    # Step 5
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 5: Text Preprocessing and Tokenization")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step5_preprocessing_tokens.png"), 5.8)

    # Step 6
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 6: Feature Extraction using HashingTF and IDF")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step6_tfidf_vectors.png"), 5.8)

    # Step 7
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 7: Train Distributed Logistic Regression Model")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step7_model_training.png"), 5.8)

    # Step 8
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 8: Generate Batch Predictions on Test Data")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step8_predictions.png"), 5.8)

    # Step 9
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 9: Model Evaluation Metrics (Accuracy, Precision, Recall, F1, ROC-AUC)")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step9_evaluation_metrics.png"), 5.8)

    # Step 10
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 10: Hyperparameter Tuning Analysis (regParam, elasticNetParam, maxIter)")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step10_tuning_analysis.png"), 5.8)

    # Step 11
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 11: Dataset Scaling Analysis (Training Time vs Dataset Size)")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step11_dataset_scaling.png"), 5.8)

    # Step 12
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 12: Compare Full-Batch vs Mini-Batch Gradient Descent")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step12_gd_comparison.png"), 5.8)

    # Step 13
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 13: Supplementary Problem 1 — HashingTF vs CountVectorizer")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step13_supplementary_hashing.png"), 5.8)

    # Step 14
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 14: Supplementary Problem 3 — Unified Spark ML Pipeline API")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step14_supplementary_pipeline.png"), 5.8)

    # Step 15
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 15: Generate ROC Curve Visualization")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(BASE_DIR, "roc_curve.png"), 5.0)

    # Step 16
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 16: Generate Scalability & Optimization Benchmark Visualizations")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(BASE_DIR, "training_time_vs_datasize.png"), 5.2)
    add_screenshot(doc, os.path.join(BASE_DIR, "metrics_and_gd_comparison.png"), 5.4)

    # Step 17
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Step 17: Generate Final Spam Detection Summary Report")
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 51, 102)
    add_screenshot(doc, os.path.join(IMG_DIR, "step17_report_preview.png"), 5.8)

    # Section 3: Key Questions
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("3. Key Questions / Analysis\n")
    r.font.bold = True
    r.font.size = Pt(12)

    # Q1
    p = doc.add_paragraph()
    r = p.add_run("Q1. What is the difference between full-batch, mini-batch, and stochastic gradient descent? Why is mini-batch preferred in distributed settings?\n")
    r.font.bold = True
    doc.add_paragraph(
        "Full-batch gradient descent calculates the gradient over the entire dataset before updating weights. "
        "Stochastic gradient descent (SGD) updates weights after every single record. "
        "Mini-batch gradient descent computes gradients on a small batch of records (e.g. 128 to 1024).\n"
        "Mini-batch is preferred in distributed settings because it significantly reduces network communication overhead between workers "
        "while enabling efficient SIMD vectorization and providing smooth, stable gradient convergence."
    )

    # Q2
    p = doc.add_paragraph()
    r = p.add_run("Q2. How does the TF-IDF vectorizer handle the 'curse of dimensionality' for text classification?\n")
    r.font.bold = True
    doc.add_paragraph(
        "TF-IDF addresses the curse of dimensionality by dampening common non-informative words using Inverse Document Frequency (IDF). "
        "In Spark, HashingTF uses feature hashing (MurmurHash3) to map words into a fixed number of buckets (e.g. 4,096), "
        "which puts a strict upper limit on the feature space and eliminates the need to maintain an enormous vocabulary dictionary in memory."
    )

    # Q3
    p = doc.add_paragraph()
    r = p.add_run("Q3. What is L1 vs L2 regularization? How does the elasticNetParam blend them in Spark MLlib?\n")
    r.font.bold = True
    doc.add_paragraph(
        "L1 regularization (Lasso) adds the sum of absolute values of weights to the loss function, forcing irrelevant feature weights to become exactly zero (feature sparsity). "
        "L2 regularization (Ridge) adds the sum of squared weights, shrinking weights smoothly towards zero without making them strictly zero.\n"
        "In Spark MLlib, elasticNetParam (alpha) mixes them: alpha = 0.0 gives pure L2 regularization, alpha = 1.0 gives pure L1 regularization, "
        "and values in between combine both penalties."
    )

    # Q4
    p = doc.add_paragraph()
    r = p.add_run("Q4. In a distributed environment, how do gradient updates from multiple workers get aggregated? What is the risk of stale gradients?\n")
    r.font.bold = True
    doc.add_paragraph(
        "Worker nodes compute local gradients on their assigned partitions. Spark aggregates these gradients using treeAggregate(), "
        "which combines them hierarchically in a tree structure to avoid bottlenecking the driver node.\n"
        "Stale gradients happen in asynchronous setups when slow workers submit gradients based on old model parameters. "
        "This can cause slow convergence or oscillation. Spark uses synchronous iterations to prevent stale gradients."
    )

    # Q5
    p = doc.add_paragraph()
    r = p.add_run("Q5. If Recall is more important than Precision for spam detection, how would you adjust the classification threshold? Show with examples.\n")
    r.font.bold = True
    doc.add_paragraph(
        "To increase Recall (capturing as many spam messages as possible), the decision threshold must be lowered from the default 0.50 down to 0.25 or 0.30.\n"
        "For example, if a suspicious email has a predicted spam probability of 0.35, under the default 0.50 threshold it would be marked as legitimate (ham), "
        "causing a False Negative. Under a 0.25 threshold, it is correctly flagged as spam, directly improving Recall."
    )

    # Section 4: Conclusion
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("4. Conclusion\n")
    r.font.bold = True
    r.font.size = Pt(12)
    doc.add_paragraph(
        "The practical successfully demonstrated Large-Scale Logistic Regression for SMS Spam Detection using Distributed Stochastic Gradient Descent (DSGD) on Apache Spark MLlib.\n"
        "A dataset of 6,000 SMS messages was ingested into a Spark DataFrame. Text preprocessing was implemented using Tokenizer, StopWordsRemover, HashingTF, and IDF. "
        "A distributed Logistic Regression model was trained, achieving 100.00% accuracy, 100.00% F1-score, and an ROC-AUC of 1.0000 on the test set.\n"
        "Hyperparameter tuning verified the behavior of L1, L2, and ElasticNet regularization. Scalability benchmarks showed linear throughput scaling up to 121,175 records "
        "(6,261 msgs/sec), and Mini-batch SGD demonstrated a 31.1% training speedup over full-batch gradient descent. "
        "An end-to-end Spark ML Pipeline was constructed for batch deployment."
    )

    # Section 5: Github Link
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("5. Github Link\n")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    r1 = p.add_run("Github Link: _ ")
    r2 = p.add_run("24DIT066-tech/Practical-11 at main · sil-sys/24DIT066-tech")
    r2.font.color.rgb = RGBColor(0, 102, 204)
    r2.font.underline = True

    output_path = os.path.join(BASE_DIR, "Practical_11_Spam_Detection_DSGD.docx")
    doc.save(output_path)
    print(f"Generated Practical 11 Word Document at: {output_path}")

if __name__ == "__main__":
    generate_doc()
