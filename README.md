# 🌙 Midnight Doomscroll Intensity (MDI) - Data Engineering Project

A complete **end-to-end data engineering pipeline** that measures late-night social media addiction through the Midnight Doomscroll Intensity (MDI) metric.

## 🎯 Project Overview

This project demonstrates professional data engineering skills by building a real-world ETL pipeline with:
- **Data extraction & transformation** using Python + Pandas
- **Database design** with PostgreSQL
- **Containerization** with Docker
- **Anomaly detection** with statistical analysis (Z-scores)
- **Data visualization** with Metabase

## 🏗️ Architecture

```
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
```

## 📊 The Metric: Midnight Doomscroll Intensity (MDI)

```
MDI = (feed_time_minutes / total_midnight_time) × avg_feed_session_minutes
```

Where:
- **feed_time_minutes**: Total minutes on social media (TikTok, Instagram, etc.) between 00:00-05:59
- **total_midnight_time**: Total app usage between 00:00-05:59
- **avg_feed_session_minutes**: Average duration per social media session

High MDI scores indicate heavy late-night social media addiction!

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Python 3.10+
- PostgreSQL (runs in Docker)
- Metabase (runs in Docker)

### Setup

1. **Clone repository**
   ```bash
   git clone https://github.com/Mayank1Deshmukh/midnight-doomscroll-intensity.git
   cd midnight-doomscroll-intensity
   ```

2. **Download dataset**
   - Download from: https://www.kaggle.com/datasets/khushikyad001/screen-time-and-app-usage-dataset-iosandroid
   - Place at: `data/raw/screen_time_app_usage_dataset.csv`

3. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   source venv/bin/activate     # Mac/Linux
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start PostgreSQL**
   ```bash
   docker run -d --name doomscroll-postgres \
     -e POSTGRES_USER=doomscroll_user \
     -e POSTGRES_PASSWORD=secure_password_123 \
     -e POSTGRES_DB=doomscroll_db \
     -p 5432:5432 \
     postgres:15-alpine
   ```

6. **Initialize database schema**
   ```bash
   docker exec -i doomscroll-postgres psql -U doomscroll_user -d doomscroll_db < sql/01_schema.sql
   ```

7. **Run ETL pipeline**
   ```bash
   python -m etl.etl_pipeline
   python -m etl.load_to_db
   python -m etl.calculate_mdi
   python -m etl.detect_anomalies
   ```

8. **Start Metabase**
   ```bash
   docker run -d -p 3000:3000 --name metabase metabase/metabase
   ```

9. **View dashboards**
   - Open http://localhost:3000
   - Create account and connect to PostgreSQL (localhost:5432)
   - Create dashboards!

## 📁 Project Structure

```
midnight-doomscroll-intensity/
├── data/
│   ├── raw/                        # Original Kaggle CSV
│   ├── processed/                  # Cleaned data
│   └── logs/                       # ETL logs
├── etl/
│   ├── __init__.py
│   ├── config.py                   # Configuration & constants
│   ├── etl_pipeline.py             # Extract & Transform
│   ├── load_to_db.py               # Load to PostgreSQL
│   ├── calculate_mdi.py            # Compute MDI scores
│   └── detect_anomalies.py         # Z-score anomaly detection
├── sql/
│   ├── 01_schema.sql               # Database schema
│   ├── 02_compute_mdi.sql          # Aggregation logic (reference)
│   └── 03_views.sql                # Optional views
├── scripts/
│   ├── setup_db.ps1                # Docker setup script
│   ├── run_pipeline.ps1            # Full pipeline orchestration
│   └── reset_db.ps1                # Reset database (dev only)
├── notebooks/
│   └── 01_exploratory_analysis.ipynb  # Optional: Jupyter exploration
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore file
├── .env.example                    # Environment template
└── README.md                       # This file
```

## 🔍 Key Findings

- **3,000 app sessions** analyzed (Jan-Apr 2024)
- **101 unique users** tracked
- **876 feed app sessions** detected (29%)
- **751 midnight sessions** identified (25%)
- **225 midnight doomscroll sessions** flagged (7.5%)
- **8 anomalies** detected (unusual spike days)

## 🛠️ Technologies Used

- **Python**: Pandas, NumPy, SciPy, SQLAlchemy
- **Database**: PostgreSQL 15 (Docker)
- **Containerization**: Docker & Docker Desktop
- **Business Intelligence**: Metabase
- **Version Control**: Git/GitHub




## 🔧 Common Commands

### Run the full pipeline
```bash
.\venv\Scripts\Activate.ps1
python -m etl.etl_pipeline
python -m etl.load_to_db
python -m etl.calculate_mdi
python -m etl.detect_anomalies
```

### Check Docker containers
```bash
docker ps
docker logs doomscroll-postgres
docker logs metabase
```

### Stop services
```bash
docker stop metabase doomscroll-postgres
deactivate
```

### Restart services
```bash
docker start doomscroll-postgres metabase
.\venv\Scripts\Activate.ps1
```

### Reset database (development only)
```bash
docker stop doomscroll-postgres
docker rm doomscroll-postgres
# Then recreate with docker run command above
```

## 📊 Database Schema

### sessions table (3000 rows)
- `session_id`: Primary key
- `user_id`: User identifier
- `app_name`: Application name
- `session_date`: Date of session
- `session_hour`: Hour (0-23)
- `session_weekday`: Day of week
- `duration_minutes`: Session duration
- `app_category`: Category (e.g., Social Media, Utilities)
- `is_feed_app`: Boolean flag for feed-based apps
- `is_midnight`: Boolean flag for midnight sessions (00:00-05:59)

### mdi_daily table (120 rows)
- `date_recorded`: Date
- `weekday`: Day of week
- `feed_time_minutes`: Minutes on feed apps at midnight
- `total_midnight_time_minutes`: Total minutes at midnight
- `avg_feed_session_minutes`: Average feed session duration
- `mdi_score`: Calculated MDI metric
- `z_score`: Standard deviation from mean
- `num_midnight_sessions`: Count of midnight sessions
- `num_feed_midnight_sessions`: Count of feed sessions at midnight

### anomaly_log table
- `date_of_anomaly`: Date flagged as anomaly
- `mdi_score`: MDI value on that date
- `z_score`: Z-score (deviation from mean)
- `severity`: mild/moderate/extreme
- `message`: Description of anomaly



## 📚 Resources

- [Kaggle Dataset](https://www.kaggle.com/datasets/khushikyad001/screen-time-and-app-usage-dataset-iosandroid)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Metabase Docs](https://www.metabase.com/docs/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

## 🚨 Troubleshooting

### "Connection refused" error
```bash
docker ps  # Check if containers are running
docker start doomscroll-postgres  # Start if stopped
```

### "Column not found" error
Check that `etl_pipeline.py` ran successfully and created `cleaned_sessions.csv`
```bash
ls data/processed/cleaned_sessions.csv
```

### Metabase won't start
```bash
docker logs metabase  # Check logs
docker rm metabase    # Remove container
docker run -d -p 3000:3000 --name metabase metabase/metabase  # Recreate
```

### Python module import errors
```bash
deactivate
rmdir /s /q venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 📝 License

MIT License - feel free to use this project for learning and interviews!


