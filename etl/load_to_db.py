"""
load_to_db.py - Load cleaned CSV data into PostgreSQL.
"""

import pandas as pd
import logging
from sqlalchemy import create_engine, text
from pathlib import Path
from .config import DATABASE_URL, DATA_PROCESSED, LOG_FILE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_to_database(csv_path, chunk_size=500):
    """Load cleaned CSV into PostgreSQL 'sessions' table."""
    logger.info(f"Loading data from {csv_path} into PostgreSQL...")
    
    try:
        # Create database connection
        engine = create_engine(DATABASE_URL, echo=False)
        logger.info("[SUCCESS] Database connection established")
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Read cleaned CSV
        df = pd.read_csv(csv_path)
        logger.info(f"[SUCCESS] Loaded {len(df)} rows from cleaned CSV")
        
        # Ensure date column is datetime
        df['session_date'] = pd.to_datetime(df['session_date'])
        
        # Insert into 'sessions' table
        logger.info(f"Inserting {len(df)} rows into 'sessions' table...")
        df.to_sql(
            'sessions',
            con=engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=chunk_size
        )
        
        logger.info(f"[SUCCESS] Successfully inserted {len(df)} rows")
        
        # Verify insertion
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM sessions;"))
            total_rows = result.scalar()
            logger.info(f"[SUCCESS] Total rows in 'sessions' table: {total_rows}")
        
        engine.dispose()
        return True
    
    except Exception as e:
        logger.error(f"[ERROR] Error loading data: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    csv_file = DATA_PROCESSED / 'cleaned_sessions.csv'
    
    if not csv_file.exists():
        logger.error(f"[ERROR] Cleaned CSV not found: {csv_file}")
        logger.info("Run etl_pipeline.py first")
        exit(1)
    
    load_to_database(csv_file)
    logger.info("[SUCCESS] Data loading complete!")
