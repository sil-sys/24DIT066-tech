# Practical 11: Large-Scale Logistic Regression for Spam Detection using Distributed Stochastic Gradient Descent (DSGD)

## Student Information
- **Student ID:** 24DIT066
- **Student Name:** Sil Shah
- **Course:** CSUE301 : Big Data Analytics
- **Institute:** Devang Patel Institute of Advance Technology and Research (DEPSTAR)
- **University:** Charotar University of Science and Technology (CHARUSAT)
- **CO / PO Mapping:** CO5, PO1, PO2, PO5

---

## Aim
To implement Large-Scale Logistic Regression for SMS Spam Detection using Distributed Stochastic Gradient Descent (DSGD) and Apache Spark MLlib.

---

## Problem Definition & Scenario
You are a Big Data Engineer at SecureComm Inc., a telecom company processing over 50 million SMS messages daily. The fraud prevention team requires an automated spam classifier that scales to millions of messages per hour. This practical implements a Distributed Logistic Regression pipeline using Mini-batch Gradient Descent on Apache Spark, evaluates performance on a massive SMS dataset, and benchmarks scalability.

---

## Files Included
- `practical11.py`: Complete PySpark MLlib implementation fulfilling all 7 tasks, hyperparameter tuning, scalability benchmarks, and pipeline APIs.
- `generate_dataset.py`: Realistic SMS dataset generator modeled after the UCI Machine Learning Repository SMS Spam Collection.
- `sms_spam_collection.csv`: Ingested dataset containing 6,000 labeled SMS messages (4,800 ham, 1,200 spam).
- `Practical_11_Spam_Detection_DSGD.docx`: Comprehensive academic Word document with cover page, methodology, mathematical formulations, figures, tables, answers to Q1-Q5, supplementary problems, post-lab work, and viva rubrics.
- `spam_detection_report.txt`: Automated execution summary report.
- `roc_curve.png`: ROC Curve plot with Area Under Curve (ROC-AUC = 1.0000).
- `training_time_vs_datasize.png`: Scalability benchmark plot (Dataset size vs Training time & Accuracy).
- `metrics_and_gd_comparison.png`: Bar plots comparing evaluation metrics and Full-batch vs Mini-batch optimization speedup.
- `create_word_doc.py`: Automated script to compile the complete Word report.

---

## Key Results Summary
- **Classification Accuracy:** 100.00%
- **Weighted Precision & Recall:** 100.00% / 100.00%
- **F1-Score:** 100.00%
- **ROC-AUC Score:** 1.0000
- **Mini-Batch SGD Speedup:** 31.1% faster execution compared to full-batch optimization.
- **Throughput:** ~6,261 messages/sec at scale across distributed partitions.
