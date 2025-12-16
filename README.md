🌙 Midnight Doomscroll Intensity (MDI) - Data Engineering Project
A complete end-to-end data engineering pipeline that measures late-night social media addiction through the Midnight Doomscroll Intensity (MDI) metric.

🎯 Project Overview
This project demonstrates professional data engineering skills by building a real-world ETL pipeline with:

Data extraction & transformation using Python + Pandas

Database design with PostgreSQL

Containerization with Docker

Anomaly detection with statistical analysis (Z-scores)

Data visualization with Metabase

🏗️ Architecture
text
CSV Data (Kaggle)
    ↓
Python ETL Pipeline (Extract, Transform, Load)
    ↓
PostgreSQL Database (Docker)
    ↓
SQL Aggregations & MDI Calculation
    ↓
Anomaly Detection (Z-scores)
    ↓
Metabase Dashboard
📊 The Metric: Midnight Doomscroll Intensity (MDI)
text
MDI = (feed_time_minutes / total_midnight_time) × avg_feed_session_minutes
Where:

feed_time_minutes: Total minutes on social media (TikTok, Instagram, etc.) between 00:00-05:59

total_midnight_time: Total app usage between 00:00-05:59

avg_feed_session_minutes: Average duration per social media session

High MDI scores indicate heavy late-night social media addiction!

🚀 Quick Start
Prerequisites
Docker Desktop

Python 3.10+

PostgreSQL (runs in Docker)

Metabase (runs in Docker)

Setup
Clone repository

bash
git clone https://github.com/Mayank1Deshmukh/midnight-doomscroll-intensity.git
cd midnight-doomscroll-intensity
Download dataset

Download from: https://www.kaggle.com/datasets/khushikyad001/screen-time-and-app-usage-dataset-iosandroid

Place at: data/raw/screen_time_app_usage_dataset.csv

Create virtual environment

bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Mac/Linux
Install dependencies

bash
pip install -r requireme
