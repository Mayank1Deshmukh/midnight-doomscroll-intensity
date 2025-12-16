"""
calculate_mdi.py - Compute daily MDI scores and store in mdi_daily table.
"""

import pandas as pd
import logging
from sqlalchemy import create_engine, text
from .config import DATABASE_URL, LOG_FILE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def compute_mdi():
    """Compute MDI for each day and store in mdi_daily table."""
    
    try:
        engine = create_engine(DATABASE_URL)
        logger.info("[SUCCESS] Database connection established")
        
        # Raw aggregation: group by date
        query = """
        SELECT
            session_date as date_recorded,
            session_weekday as weekday,
            SUM(CASE WHEN is_feed_app AND is_midnight THEN duration_minutes ELSE 0 END) 
                as feed_time_minutes,
            SUM(CASE WHEN is_midnight THEN duration_minutes ELSE 0 END) 
                as total_midnight_time_minutes,
            AVG(CASE WHEN is_feed_app AND is_midnight THEN duration_minutes ELSE NULL END) 
                as avg_feed_session_minutes,
            COUNT(CASE WHEN is_feed_app AND is_midnight THEN 1 ELSE NULL END) 
                as num_feed_midnight_sessions,
            COUNT(CASE WHEN is_midnight THEN 1 ELSE NULL END) 
                as num_midnight_sessions
        FROM sessions
        GROUP BY session_date, session_weekday
        ORDER BY session_date ASC;
        """
        
        logger.info("Executing aggregation query...")
        df_agg = pd.read_sql(query, con=engine)
        logger.info(f"[SUCCESS] Aggregated {len(df_agg)} days of data")
        
        # Compute MDI score
        epsilon = 0.001  # Avoid division by zero
        df_agg['total_midnight_time_minutes'] = df_agg['total_midnight_time_minutes'].fillna(0)
        df_agg['feed_time_minutes'] = df_agg['feed_time_minutes'].fillna(0)
        df_agg['avg_feed_session_minutes'] = df_agg['avg_feed_session_minutes'].fillna(0)
        
        df_agg['mdi_score'] = (
            df_agg['feed_time_minutes'] / 
            (df_agg['total_midnight_time_minutes'] + epsilon)
        ) * df_agg['avg_feed_session_minutes']
        
        logger.info(f"[SUCCESS] Computed MDI for {len(df_agg)} days")
        logger.info(f"\n MDI Statistics:")
        logger.info(df_agg['mdi_score'].describe())
        
        # Insert into mdi_daily table
        logger.info(f"Inserting into 'mdi_daily' table...")
        df_agg.to_sql(
            'mdi_daily',
            con=engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=100
        )
        
        logger.info(f"[SUCCESS] Inserted {len(df_agg)} rows into 'mdi_daily' table")
        
        engine.dispose()
        return df_agg
    
    except Exception as e:
        logger.error(f"[ERROR] Error computing MDI: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    df_mdi = compute_mdi()
    logger.info("[SUCCESS] MDI computation complete!")
