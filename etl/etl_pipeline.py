"""
etl_pipeline.py - Extract and transform raw CSV data.
Optimized for Screen Time and App Usage Dataset (iOS/Android) from Kaggle.
"""

import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from .config import DATA_RAW, DATA_PROCESSED, FEED_APPS, MIDNIGHT_HOURS, LOG_FILE
import numpy as np


# Configure logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),  # UTF-8 for file
        logging.StreamHandler()  # Default for console (handles cp1252 gracefully)
    ]
)
logger = logging.getLogger(__name__)

def load_raw_csv(csv_path):
    """Load raw CSV from Kaggle dataset."""
    logger.info(f"Loading raw CSV from {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")
    logger.info(f"Columns: {list(df.columns)}")
    return df

def parse_and_validate_timestamps(df):
    """
    Parse date column and create hour, weekday columns.
    Handles both date-only and timestamp formats.
    """
    logger.info("Parsing and validating timestamps...")
    
    # Try to find and parse date column
    if 'date' not in df.columns:
        logger.error(f"No 'date' column found! Available: {list(df.columns)}")
        raise ValueError("Date column not found")
    
    # Use pandas default inference - handles all timestamp formats
    try:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        logger.info("Successfully parsed dates using pandas inference")
    except Exception as e:
        logger.error(f"Failed to parse dates: {e}")
        raise
    
    # Remove rows where date parsing failed
    invalid_dates = df[df['date'].isna()].shape[0]
    if invalid_dates > 0:
        logger.warning(f"Found {invalid_dates} rows with invalid dates, removing...")
        df = df[df['date'].notna()]
    
    # Extract hour from timestamp (important for "midnight" detection)
    if 'hour' not in df.columns:
        df['hour'] = df['date'].dt.hour
        logger.info("Extracted hour from timestamp")
    else:
        df['hour'] = df['hour'].astype(int)
    
    # Create date_only and weekday
    df['date_only'] = df['date'].dt.date
    df['weekday'] = df['date'].dt.day_name()
    
    logger.info(f"After parsing: {len(df)} valid rows")
    logger.info(f"Date range: {df['date_only'].min()} to {df['date_only'].max()}")
    logger.info(f"Hour distribution:\n{df['hour'].value_counts().sort_index()}")
    
    return df

def flag_feed_apps(df):
    """Flag rows where app_name is a feed-based app."""
    logger.info("Flagging feed apps...")
    
    # Handle different column names
    if 'app_name' not in df.columns:
        if 'App Name' in df.columns:
            df.rename(columns={'App Name': 'app_name'}, inplace=True)
        elif 'app' in df.columns:
            df.rename(columns={'app': 'app_name'}, inplace=True)
    
    df['app_name_lower'] = df['app_name'].str.lower().str.strip()
    df['is_feed_app'] = df['app_name_lower'].isin(FEED_APPS)
    
    feed_count = df['is_feed_app'].sum()
    logger.info(f"Found {feed_count} feed app sessions out of {len(df)}")
    logger.info(f"Feed apps in data: {sorted(df[df['is_feed_app']]['app_name'].unique())}")
    
    return df.drop(columns=['app_name_lower'])

def flag_midnight_sessions(df):
    """Flag rows where hour is between 00:00 and 05:59."""
    logger.info("Flagging midnight sessions (00:00–05:59)...")
    df['is_midnight'] = df['hour'].astype(int).isin(MIDNIGHT_HOURS)
    midnight_count = df['is_midnight'].sum()
    logger.info(f"Found {midnight_count} midnight sessions")
    return df

def clean_data(df):
    """Remove or impute invalid/missing data."""
    logger.info("Cleaning data...")
    
    # Rename screen_time_min to duration_minutes (YOUR CSV HAS THIS)
    if 'screen_time_min' in df.columns:
        df.rename(columns={'screen_time_min': 'duration_minutes'}, inplace=True)
        logger.info("Renamed 'screen_time_min' to 'duration_minutes'")
    # Check for other variations
    elif 'screen_time' in df.columns:
        df.rename(columns={'screen_time': 'duration_minutes'}, inplace=True)
    elif 'Screen Time' in df.columns:
        df.rename(columns={'Screen Time': 'duration_minutes'}, inplace=True)
    elif 'duration' in df.columns:
        df.rename(columns={'duration': 'duration_minutes'}, inplace=True)
    elif 'Duration' in df.columns:
        df.rename(columns={'Duration': 'duration_minutes'}, inplace=True)
    
    # Remove rows with missing critical values
    initial_count = len(df)
    required_cols = [col for col in ['user_id', 'app_name', 'date_only', 'duration_minutes'] if col in df.columns]
    if required_cols:
        df = df.dropna(subset=required_cols)
    
    dropped_rows = initial_count - len(df)
    if dropped_rows > 0:
        logger.info(f"Dropped {dropped_rows} rows with missing critical values")
    
    # Remove rows with invalid durations
    if 'duration_minutes' in df.columns:
        df = df[(df['duration_minutes'] > 0) & (df['duration_minutes'] <= 1000)]
        logger.info(f"Kept rows with duration in (0, 1000] minutes")
    
    # Ensure numeric columns
    if 'user_id' in df.columns:
        df['user_id'] = pd.to_numeric(df['user_id'], errors='coerce').fillna(0).astype(int)
    if 'duration_minutes' in df.columns:
        df['duration_minutes'] = pd.to_numeric(df['duration_minutes'], errors='coerce')
    
    # Remove duplicates
    initial_count = len(df)
    subset_cols = [col for col in ['user_id', 'app_name', 'date_only', 'hour'] if col in df.columns]
    if subset_cols:
        df = df.drop_duplicates(subset=subset_cols, keep='first')
    
    dropped_duplicates = initial_count - len(df)
    if dropped_duplicates > 0:
        logger.info(f"Dropped {dropped_duplicates} duplicate sessions")
    
    logger.info(f"After cleaning: {len(df)} rows remain")
    return df


def transform_pipeline(csv_path):
    """Run full ETL transformation pipeline."""
    try:
        # Extract
        df = load_raw_csv(csv_path)
        
        # Transform
        df = parse_and_validate_timestamps(df)
        df = flag_feed_apps(df)
        df = flag_midnight_sessions(df)
        df = clean_data(df)
        
        # Rename columns for database schema
        df = df.rename(columns={
            'date_only': 'session_date',
            'weekday': 'session_weekday',
            'hour': 'session_hour'
        })
        
        # Handle app_category if it exists
        if 'app_category' not in df.columns:
            if 'App Category' in df.columns:
                df.rename(columns={'App Category': 'app_category'}, inplace=True)
            elif 'category' in df.columns:
                df.rename(columns={'category': 'app_category'}, inplace=True)
            else:
                df['app_category'] = 'Unknown'
        
        # Select and order columns for database insertion
        output_cols = [
            'user_id', 'app_name', 'session_date', 'session_hour', 'session_weekday',
            'duration_minutes', 'app_category', 'is_feed_app', 'is_midnight'
        ]
        df = df[[col for col in output_cols if col in df.columns]]
        
        logger.info(f"[SUCCESS] Transformation complete. Final shape: {df.shape}")
        logger.info(f"\nData Summary:")
        logger.info(f"  Total sessions: {len(df)}")
        logger.info(f"  Date range: {df['session_date'].min()} to {df['session_date'].max()}")
        logger.info(f"  Unique users: {df['user_id'].nunique()}")
        logger.info(f"  Feed sessions: {df['is_feed_app'].sum()}")
        logger.info(f"  Midnight sessions: {df['is_midnight'].sum()}")
        logger.info(f"  Midnight feed sessions: {(df['is_feed_app'] & df['is_midnight']).sum()}")
        
        return df
    
    except Exception as e:
        logger.error(f"Error in transform pipeline: {e}", exc_info=True)
        raise

def save_cleaned_csv(df, output_path):
    """Save cleaned dataframe to CSV."""
    df.to_csv(output_path, index=False)
    logger.info(f"[SUCCESS] Saved cleaned data to {output_path}")

if __name__ == '__main__':
    input_csv = DATA_RAW / 'screen_time_app_usage_dataset.csv'
    output_csv = DATA_PROCESSED / 'cleaned_sessions.csv'
    
    if not input_csv.exists():
        logger.error(f" Input CSV not found: {input_csv}")
        logger.info(f"\n Please download the dataset from Kaggle:")
        logger.info(f"   https://www.kaggle.com/datasets/khushikyad001/screen-time-and-app-usage-dataset-iosandroid")
        logger.info(f"   And place the CSV file at: {input_csv}")
        exit(1)
    
    df_clean = transform_pipeline(input_csv)
    save_cleaned_csv(df_clean, output_csv)
    logger.info("\n[SUCCESS] ETL pipeline completed successfully!")

