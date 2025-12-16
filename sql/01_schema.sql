-- Schema initialization for Midnight Doomscroll Intensity project

-- Drop existing tables (dev only, comment out after first run)
-- DROP TABLE IF EXISTS anomaly_log;
-- DROP TABLE IF EXISTS mdi_daily;
-- DROP TABLE IF EXISTS sessions;

-- Table 1: Raw sessions data (after cleaning)
CREATE TABLE IF NOT EXISTS sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    app_name VARCHAR(100) NOT NULL,
    session_date DATE NOT NULL,
    session_hour INTEGER NOT NULL CHECK (session_hour >= 0 AND session_hour < 24),
    session_weekday VARCHAR(10) NOT NULL,
    duration_minutes NUMERIC(10, 2) NOT NULL CHECK (duration_minutes > 0),
    app_category VARCHAR(50),
    is_feed_app BOOLEAN DEFAULT FALSE,
    is_midnight BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes on sessions table
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(session_date);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_is_feed_midnight ON sessions(is_feed_app, is_midnight);
CREATE INDEX IF NOT EXISTS idx_sessions_hour ON sessions(session_hour);

-- Table 2: Daily MDI metrics
CREATE TABLE IF NOT EXISTS mdi_daily (
    day_id SERIAL PRIMARY KEY,
    date_recorded DATE NOT NULL UNIQUE,
    weekday VARCHAR(10) NOT NULL,
    feed_time_minutes NUMERIC(10, 2) DEFAULT 0,
    total_midnight_time_minutes NUMERIC(10, 2) DEFAULT 0,
    avg_feed_session_minutes NUMERIC(10, 2) DEFAULT 0,
    mdi_score NUMERIC(10, 4) DEFAULT 0,
    z_score NUMERIC(10, 4),
    num_midnight_sessions INTEGER DEFAULT 0,
    num_feed_midnight_sessions INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes on mdi_daily table
CREATE INDEX IF NOT EXISTS idx_mdi_daily_date ON mdi_daily(date_recorded);
CREATE INDEX IF NOT EXISTS idx_mdi_daily_z_score ON mdi_daily(z_score);

-- Table 3: Anomaly log
CREATE TABLE IF NOT EXISTS anomaly_log (
    anomaly_id SERIAL PRIMARY KEY,
    date_of_anomaly DATE NOT NULL,
    mdi_score NUMERIC(10, 4),
    z_score NUMERIC(10, 4),
    severity VARCHAR(20) CHECK (severity IN ('mild', 'moderate', 'extreme')),
    message TEXT,
    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes on anomaly_log table
CREATE INDEX IF NOT EXISTS idx_anomaly_log_date ON anomaly_log(date_of_anomaly);
CREATE INDEX IF NOT EXISTS idx_anomaly_log_severity ON anomaly_log(severity);

-- Summary view for Tableau
CREATE OR REPLACE VIEW v_mdi_summary AS
SELECT
    date_recorded,
    weekday,
    mdi_score,
    z_score,
    feed_time_minutes,
    total_midnight_time_minutes,
    avg_feed_session_minutes,
    num_feed_midnight_sessions,
    CASE
        WHEN ABS(z_score) > 2 THEN 'EXTREME'
        WHEN ABS(z_score) > 1.5 THEN 'MODERATE'
        WHEN ABS(z_score) > 1 THEN 'MILD'
        ELSE 'NORMAL'
    END AS anomaly_level
FROM mdi_daily
ORDER BY date_recorded DESC;
