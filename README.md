Bluestock B100 • Nifty 100 Intelligence Platform
Hey! Welcome to the Bluestock B100 project. This is a fundamental analysis and financial health-scoring platform designed for Nifty 100 companies. It features a complete end-to-end data pipeline that extracts raw Excel files, cleans and aggregates the data, runs a health-scoring algorithm, and serves it up on a clean, modern web dashboard.

🚀 What This Project Covers
This project spans across data engineering, backend development, and frontend UI design:

End-to-End ETL Pipeline (etl/):

01_extract.py: Reads raw Excel sheets (like balancesheet.xlsx, profitandloss.xlsx, etc.) and outputs them into clean, standardized CSV files.
02_clean_and_transform.py: Trims whitespace, maps stock symbols to their respective industry sectors, calculates net profit margins, and computes debt-to-equity ratios.
03_load_to_django.py: Populates the database with basic company metadata.
04_load_financial_data.py: Loads historical P&L and Balance Sheet details, calculates multi-year averages (CAGR, OPM, Debt/Equity), and updates the company-level records.
05_health_scoring.py: Evaluates each company using a weighted formula (Profitability, Leverage, Revenue Growth, Cash Flow Quality, Trend) to produce a composite Financial Health Score (0-100).
Django Backend API (backend/):

Sets up a robust REST API using Django REST Framework (api/views.py).
Uses Django models (api/models.py) to manage company and financial records, including a dynamic @property called health_label to categorize companies (EXCELLENT, GOOD, AVERAGE, WEAK, or POOR).
Standardizes response values (rounding metrics like ROE, OPM, etc. to 2 decimal places).
Frontend Dashboard (backend/frontend/):

A modern single-page dashboard built using HTML5, Vanilla JavaScript, and Tailwind CSS.
Features real-time search, sector-based filtering, and key performance indicators (KPIs) like Total Companies, Average Health Score, Count of Excellent Companies, and average ROE.
🛠️ Prerequisites & Dependencies (Libraries to Install)
To run this project, you will need Python (version 3.10+) installed on your system.

Before running the code, install the required packages. Open your terminal in the Bluestock_B100_Intelligence directory and run:

pip install -r requirements.txt
If you don't have a requirements.txt handy, you can manually install the required packages:

pip install Django==4.2.13 djangorestframework==3.15.2 django-cors-headers==4.4.0 pandas openpyxl
📦 Quick Breakdown of Installed Libraries:
Django: The core framework for our web server.
djangorestframework: Simplifies creating APIs for the frontend.
django-cors-headers: Handles cross-origin requests securely.
pandas: Powers the ETL data processing and calculations.
openpyxl: Allows Pandas to parse Excel file formats (.xlsx).
🏃‍♂️ How to Run the Project
Follow these steps sequentially to set up and run the application locally:

Step 1: Run the ETL Pipeline
We need to load and process the raw Excel files into the database. Run the scripts in the etl/ directory in order:

# 1. Extract raw Excel data to clean CSVs
python etl/01_extract.py

# 2. Clean up columns, map sectors, and save processed data
python etl/02_clean_and_transform.py

# 3. Load basic company listings into Django
python etl/03_load_to_django.py

# 4. Process and populate historical financial aggregates
python etl/04_load_financial_data.py

# 5. Compute the final Financial Health Scores
python etl/05_health_scoring.py
Step 2: Start the Web Server
Once the data is seeded, navigate to the Django root directory (if not already there) and run:

python manage.py runserver
By default, the server will launch at http://127.0.0.1:8000/.

Step 3: View the Dashboard
Open your browser and navigate to:

http://127.0.0.1:8000/
The home route automatically serves the frontend dashboard showing real-time stats and analytics!

💡 Notes for Windows Users
The scripts include a terminal encoding fix:

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
This ensures that terminal progress indicators and emoji status logs (🚀, ✅, 📌) render cleanly on Windows Command Prompt or PowerShell without throwing encoding issues.
