"""
config.py - Database and ETL configuration.
Loads credentials from environment variables (.env file).
"""

import os
from pathlib import Path

# Database connection (PostgreSQL in Docker)
DB_USER = os.getenv('DB_USER', 'doomscroll_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'secure_password_123')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'doomscroll_db')

# SQLAlchemy connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# File paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / 'data' / 'raw'
DATA_PROCESSED = PROJECT_ROOT / 'data' / 'processed'
DATA_LOGS = PROJECT_ROOT / 'data' / 'logs'

# Create directories if they don't exist
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
DATA_LOGS.mkdir(parents=True, exist_ok=True)

# ETL Configuration
FEED_APPS = {
    'tiktok', 'instagram', 'twitter', 'reddit', 'x', 'youtube',
    'youtube shorts', 'facebook', 'snapchat', 'pinterest', 'threads',
    'bluesky', 'mastodon'
}

MIDNIGHT_HOURS = set(range(0, 6))  # 0–5 inclusive

# Anomaly detection threshold
Z_SCORE_THRESHOLD = 1.5

# Logging
LOG_FILE = DATA_LOGS / 'etl.log'
