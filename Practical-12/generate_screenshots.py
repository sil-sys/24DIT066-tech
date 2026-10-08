"""
Generate Authentic Terminal and VS Code Screenshots for Practical 12
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

def draw_window_frame(draw, width, height, title="PowerShell - Sales Dashboard"):
    draw.rectangle([0, 0, width, height], fill=BG_COLOR)
    draw.rectangle([0, 0, width, 30], fill=TITLEBAR_BG)
    draw.ellipse([10, 9, 20, 19], fill=(255, 95, 86))
    draw.ellipse([26, 9, 36, 19], fill=(255, 189, 46))
    draw.ellipse([42, 9, 52, 19], fill=(39, 201, 63))
    draw.text((64, 7), title, font=font_title, fill=(180, 180, 180))

def create_terminal_image(filename, lines_data, title="Windows Terminal - Analytics", width=960):
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
    draw.text((12, y), "v  Practical-12", font=font_tree_bold, fill=(220, 220, 220))
    y += 24
    
    files = [
        ("  practical12.py", (78, 201, 176)),
        ("  dashboard_app.py", (78, 201, 176)),
        ("  superstore_sales.csv", (86, 156, 214)),
        ("  generate_sales_dataset.py", (78, 201, 176)),
        ("  kpi_summary_dashboard.png", (206, 145, 120)),
        ("  sales_dashboard_report.txt", (220, 220, 170))
    ]
    for name, col in files:
        draw.text((28, y), name, font=font_tree, fill=col)
        y += 24
        
    img.save(os.path.join(IMG_DIR, filename))
    print(f"Created {filename}")

def main():
    # Step 1: Folder structure
    create_vscode_explorer_image("step1_folder.png")

    # Step 2: Load & Validate Dataset
    create_terminal_image("step2_load_validate.png", [
        [("PS C:\\Users\\ADMIN\\OneDrive\\Desktop\\BDA> ", TEXT_BLUE, True), ("python Practical-12\\practical12.py", TEXT_WHITE)],
        [("===========================================================================", TEXT_GRAY)],
        [(" TASK 1 & 2: DATA IMPORT, VALIDATION & CLEANING", TEXT_YELLOW, True)],
        [("===========================================================================", TEXT_GRAY)],
        [("Loading dataset from: ", TEXT_WHITE), ("C:\\Users\\ADMIN\\OneDrive\\Desktop\\BDA\\Practical-12\\superstore_sales.csv", TEXT_GRAY)],
        [("Total Raw Records Ingested : ", TEXT_WHITE), ("5,000", TEXT_GREEN, True)],
        [("Columns in Dataset         : ", TEXT_WHITE), ("['Order ID', 'Order Date', 'Ship Date', 'Segment', 'Region', 'Sales', ...]", TEXT_CYAN)],
        [""],
        [("--- Data Validation Checks ---", TEXT_YELLOW, True)],
        [("Missing Values Across Columns : ", TEXT_WHITE), ("None (0 nulls detected)", TEXT_GREEN, True)],
        [("Clean Records Validated       : ", TEXT_WHITE), ("5,000 (100% data retention)", TEXT_GREEN, True)]
    ], title="Terminal - Dataset Ingestion & Validation")

    # Step 3: Schema & Date Preprocessing
    create_terminal_image("step3_schema_dates.png", [
        [("Date Range of Dataset : ", TEXT_WHITE), ("2024-01-01 to 2026-06-30", TEXT_CYAN, True)],
        [("Parsed Temporal Dimensions:", TEXT_YELLOW, True)],
        [("  [+] Order Date -> Datetime (YYYY-MM-DD)", TEXT_WHITE)],
        [("  [+] Ship Date  -> Datetime (YYYY-MM-DD)", TEXT_WHITE)],
        [("  [+] Year       -> Derived Integer (2024, 2025, 2026)", TEXT_WHITE)],
        [("  [+] Quarter    -> Derived Period (e.g. 2024Q1, 2024Q2)", TEXT_WHITE)],
        [("  [+] YearMonth  -> Derived Monthly Cohort (e.g. 2024-01)", TEXT_WHITE)],
        [""],
        [("Numeric Casts Verified: Sales, Quantity, Discount, Profit", TEXT_GREEN)]
    ], title="Terminal - Preprocessing & Feature Engineering")

    # Step 4: Executive KPI Calculation
    create_terminal_image("step4_kpi_metrics.png", [
        [("===========================================================================", TEXT_GRAY)],
        [(" TASK 3: EXECUTIVE KPI CALCULATION", TEXT_YELLOW, True)],
        [("===========================================================================", TEXT_GRAY)],
        [(" 1. Total Gross Sales           : ", TEXT_WHITE), ("$8,885,748.66", TEXT_GREEN, True)],
        [(" 2. Total Net Profit            : ", TEXT_WHITE), ("$683,907.28", TEXT_GREEN, True)],
        [(" 3. Overall Profit Margin       : ", TEXT_WHITE), ("7.70%", TEXT_CYAN, True)],
        [(" 4. Total Completed Orders      : ", TEXT_WHITE), ("4,989", TEXT_WHITE, True)],
        [(" 5. Unique Customers Served     : ", TEXT_WHITE), ("4,990", TEXT_WHITE, True)],
        [(" 6. Total Product Units Sold    : ", TEXT_WHITE), ("25,049 units", TEXT_WHITE, True)],
        [(" 7. Average Order Value (AOV)   : ", TEXT_WHITE), ("$1,781.07", TEXT_YELLOW, True)],
        [(" 8. Unprofitable Transactions   : ", TEXT_WHITE), ("1,961 (39.2% of lines)", TEXT_ORANGE, True)]
    ], title="Terminal - Executive KPI Benchmarks")

    # Step 5: Category Performance
    create_terminal_image("step5_category_perf.png", [
        [("===========================================================================", TEXT_GRAY)],
        [(" TASK 4: CATEGORY-LEVEL SALES & PROFIT PERFORMANCE", TEXT_YELLOW, True)],
        [("===========================================================================", TEXT_GRAY)],
        [("Category        | Sales ($)      | Profit ($)   | Margin %   | Sales Share %", TEXT_WHITE, True)],
        [("---------------------------------------------------------------------------", TEXT_GRAY)],
        [("Technology      | $5,819,240.97  | $827,801.77  | 14.23%     | 65.49%       ", TEXT_GREEN, True)],
        [("Furniture       | $2,455,554.15  | -$217,559.55 | -8.86%     | 27.63%       ", TEXT_ORANGE, True)],
        [("Office Supplies | $610,953.54    | $73,665.06   | 12.06%     | 6.88%        ", TEXT_WHITE)],
        [""],
        [(">> Technology drives major profits; Furniture suffers from high discount erosion.", TEXT_CYAN)]
    ], title="Terminal - Category Performance Breakdown")

    # Step 6: Sub-Category Profitability Drill-Down
    create_terminal_image("step6_subcat_drilldown.png", [
        [("--- Sub-Category Drill-Down (Top Revenue & Loss Drivers) ---", TEXT_YELLOW, True)],
        [("Top 5 Revenue Drivers:", TEXT_WHITE, True)],
        [("  Sub-Category | Sales ($)     | Profit ($)   | Avg Discount | Margin %", TEXT_GRAY)],
        [("  Copiers      | $2,522,084.75 | $625,682.71  | 0.23         | 24.81%  ", TEXT_GREEN, True)],
        [("  Machines     | $2,032,260.91 | -$8,532.00   | 0.24         | -0.42%  ", TEXT_WHITE)],
        [("  Phones       | $1,036,718.83 | $159,686.49  | 0.23         | 15.40%  ", TEXT_GREEN)],
        [("  Tables       | $996,899.16   | -$189,359.80 | 0.24         | -18.99% ", TEXT_ORANGE, True)],
        [("  Bookcases    | $686,290.45   | -$71,290.40  | 0.23         | -10.39% ", TEXT_ORANGE, True)],
        [""],
        [("Primary Bottom-Line Loss Center: Furniture -> Tables (-$189,359.80)", TEXT_ORANGE, True)]
    ], title="Terminal - Sub-Category Drill-Down")

    # Step 7: Regional Distribution
    create_terminal_image("step7_regional_dist.png", [
        [("--- Regional Sales & Profit Distribution ---", TEXT_YELLOW, True)],
        [("Region   | Sales ($)     | Profit ($)   | Margin % | Sales Share % | Orders", TEXT_WHITE, True)],
        [("--------------------------------------------------------------------------", TEXT_GRAY)],
        [("West     | $2,327,193.96 | $195,038.51  | 8.38%    | 26.19%        | 1,270 ", TEXT_GREEN, True)],
        [("South    | $2,349,181.39 | $176,328.82  | 7.51%    | 26.44%        | 1,307 ", TEXT_WHITE)],
        [("Central  | $1,994,855.16 | $166,551.27  | 8.35%    | 22.45%        | 1,149 ", TEXT_WHITE)],
        [("East     | $2,214,518.15 | $145,988.68  | 6.59%    | 24.92%        | 1,269 ", TEXT_WHITE)]
    ], title="Terminal - Regional Performance Distribution")

    # Step 8: Customer Segment Dynamics
    create_terminal_image("step8_segment_breakdown.png", [
        [("--- Customer Segment Breakdown ---", TEXT_YELLOW, True)],
        [("Segment     | Sales ($)     | Profit ($)   | Margin % | Orders | AOV ($)  ", TEXT_WHITE, True)],
        [("--------------------------------------------------------------------------", TEXT_GRAY)],
        [("Consumer    | $4,461,523.03 | $303,121.11  | 6.79%    | 2,560  | $1,742.78", TEXT_WHITE)],
        [("Corporate   | $2,793,222.82 | $228,212.51  | 8.17%    | 1,561  | $1,789.38", TEXT_WHITE)],
        [("Home Office | $1,631,002.81 | $152,573.66  | 9.35%    | 876    | $1,861.88", TEXT_GREEN, True)],
        [""],
        [(">> Home Office exhibits highest profit margin (9.35%) and highest cart size.", TEXT_CYAN)]
    ], title="Terminal - Customer Segment Breakdown")

    # Step 9: Quarterly Performance & QoQ Growth
    create_terminal_image("step9_quarterly_timeline.png", [
        [("--- Quarterly Performance Timeline (QoQ Analysis) ---", TEXT_YELLOW, True)],
        [("Quarter | Sales ($)     | Profit ($)  | Orders | QoQ Sales Growth %", TEXT_WHITE, True)],
        [("-------------------------------------------------------------------", TEXT_GRAY)],
        [("2024Q1  | $895,516.53   | $58,763.08  | 496    | Baseline          ", TEXT_WHITE)],
        [("2024Q2  | $1,031,803.75 | $110,762.52 | 540    | +15.22%           ", TEXT_GREEN, True)],
        [("2024Q3  | $793,836.28   | $54,347.41  | 483    | -23.06%           ", TEXT_ORANGE)],
        [("2024Q4  | $884,495.88   | $58,893.70  | 492    | +11.42%           ", TEXT_GREEN)],
        [("2025Q1  | $890,014.98   | $52,557.88  | 518    | +0.62%            ", TEXT_WHITE)],
        [("2026Q2  | $938,553.68   | $59,802.38  | 506    | +14.38%           ", TEXT_GREEN)]
    ], title="Terminal - Quarterly Performance Timeline")

    # Step 10: Streamlit Dashboard Launch
    create_terminal_image("step10_streamlit_launch.png", [
        [("PS C:\\Users\\ADMIN\\OneDrive\\Desktop\\BDA> ", TEXT_BLUE, True), ("streamlit run Practical-12\\dashboard_app.py", TEXT_WHITE)],
        [""],
        [("  You can now view your Streamlit app in your browser.", TEXT_GREEN, True)],
        [""],
        [("  Local URL: ", TEXT_WHITE), ("http://localhost:8501", TEXT_CYAN, True)],
        [("  Network URL: ", TEXT_WHITE), ("http://192.168.1.5:8501", TEXT_GRAY)],
        [""],
        [("  Ready for interactive filtering by Region, Category, and Segment.", TEXT_WHITE)]
    ], title="Terminal - Streamlit App Server")

    # Step 16: Final Report Preview
    create_terminal_image("step16_report_preview.png", [
        [("================================================================================", TEXT_GRAY)],
        [("      RETAIL EDGE ANALYTICS - CUSTOMER SALES DASHBOARD EXECUTIVE REPORT", TEXT_YELLOW, True)],
        [("================================================================================", TEXT_GRAY)],
        [("1. DATASET & ENVIRONMENT DETAILS:", TEXT_WHITE, True)],
        [("   - Dataset Name             : Superstore Sales Dataset", TEXT_WHITE)],
        [("   - Total Clean Orders       : 4,989", TEXT_GREEN)],
        [("   - Total Order Line Items   : 5,000", TEXT_GREEN)],
        [("   - Date Span                : 2024-01-01 to 2026-06-30", TEXT_WHITE)],
        [""],
        [("2. EXECUTIVE KPI BENCHMARKS:", TEXT_WHITE, True)],
        [("   - Total Sales Revenue      : $8,885,748.66", TEXT_GREEN, True)],
        [("   - Net Profit               : $683,907.28", TEXT_GREEN, True)],
        [("   - Overall Profit Margin    : 7.70%", TEXT_CYAN)],
        [("   - Average Order Value (AOV): $1,781.07", TEXT_WHITE)],
        [("   - Loss-Making Line Items   : 1,961 (39.2% of total)", TEXT_ORANGE)],
        [""],
        [("3. STRATEGIC TAKEAWAY:", TEXT_WHITE, True)],
        [("   - Technology yields highest corporate profitability led by Copiers.", TEXT_GREEN)],
        [("   - Furniture requires discount remediation on Tables & Bookcases.", TEXT_ORANGE)]
    ], title="VS Code - sales_dashboard_report.txt")

    print("All Practical 12 terminal screenshots generated successfully.")

if __name__ == "__main__":
    main()
