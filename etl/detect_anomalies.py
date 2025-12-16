"""
detect_anomalies.py - Detect anomalies in MDI using z-scores.
"""

import pandas as pd
import numpy as np
import logging
from sqlalchemy import create_engine, text
from .config import DATABASE_URL, Z_SCORE_THRESHOLD, LOG_FILE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def detect_anomalies():
    """Detect and log anomalies in MDI scores."""
    
    try:
        engine = create_engine(DATABASE_URL)
        logger.info("[SUCCESS] Database connection established")
        
        # Fetch MDI daily data
        query = "SELECT date_recorded, mdi_score FROM mdi_daily ORDER BY date_recorded ASC;"
        df_mdi = pd.read_sql(query, con=engine)
        
        if len(df_mdi) == 0:
            logger.warning("[WARNING]  No MDI data found. Run calculate_mdi.py first.")
            return
        
        logger.info(f"[SUCCESS] Fetched {len(df_mdi)} days of MDI data")
        
        # Compute z-scores
        mean_mdi = df_mdi['mdi_score'].mean()
        std_mdi = df_mdi['mdi_score'].std()
        
        if std_mdi == 0:
            logger.warning("[WARNING]  MDI has zero standard deviation; skipping z-score calculation")
            return
        
        df_mdi['z_score'] = (df_mdi['mdi_score'] - mean_mdi) / std_mdi
        
        logger.info(f"\n MDI Statistics:")
        logger.info(f"  Mean: {mean_mdi:.4f}")
        logger.info(f"  Std Dev: {std_mdi:.4f}")
        logger.info(f"  Min: {df_mdi['mdi_score'].min():.4f}")
        logger.info(f"  Max: {df_mdi['mdi_score'].max():.4f}")
        
        # Flag anomalies
        df_anomalies = df_mdi[df_mdi['z_score'].abs() > Z_SCORE_THRESHOLD].copy()
        
        logger.info(f"\n Found {len(df_anomalies)} anomalies (|z| > {Z_SCORE_THRESHOLD})")
        
        if len(df_anomalies) > 0:
            # Assign severity
            def assign_severity(z):
                if abs(z) > 2.0:
                    return 'extreme'
                elif abs(z) > 1.5:
                    return 'moderate'
                else:
                    return 'mild'
            
            df_anomalies['severity'] = df_anomalies['z_score'].apply(assign_severity)
            df_anomalies['message'] = df_anomalies.apply(
                lambda row: f"Midnight doomscroll spike detected. MDI={row['mdi_score']:.2f}, z={row['z_score']:.2f}",
                axis=1
            )
            df_anomalies = df_anomalies.rename(columns={'date_recorded': 'date_of_anomaly'})
            df_anomalies = df_anomalies[['date_of_anomaly', 'mdi_score', 'z_score', 'severity', 'message']]
            
            # Insert into anomaly_log table
            df_anomalies.to_sql(
                'anomaly_log',
                con=engine,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=100
            )
            
            logger.info(f"[SUCCESS] Inserted {len(df_anomalies)} anomalies into 'anomaly_log' table")
            
            # Print anomalies
            logger.info(f"\n Anomalies Detected:")
            for _, row in df_anomalies.iterrows():
                logger.info(f"  {row['date_of_anomaly']}: {row['severity'].upper()} | MDI={row['mdi_score']:.2f} | z={row['z_score']:.2f}")
        
        # Update mdi_daily with z_scores
        with engine.connect() as conn:
            for _, row in df_mdi.iterrows():
                conn.execute(
                    text("""
                        UPDATE mdi_daily 
                        SET z_score = :z_score
                        WHERE date_recorded = :date_recorded
                    """),
                    {"z_score": row['z_score'], "date_recorded": row['date_recorded']}
                )
            conn.commit()
        
        logger.info("[SUCCESS] Updated mdi_daily table with z_scores")
        
        engine.dispose()
        return df_anomalies if len(df_anomalies) > 0 else None
    
    except Exception as e:
        logger.error(f"[ERROR] Error detecting anomalies: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    df_anomalies = detect_anomalies()
    logger.info("[SUCCESS] Anomaly detection complete!")
