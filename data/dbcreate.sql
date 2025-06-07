-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Transmitters table
CREATE TABLE IF NOT EXISTS transmitters (
    id INTEGER PRIMARY KEY,
    country_code TEXT NOT NULL,
    site_code TEXT NOT NULL,
    name TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    UNIQUE(country_code, site_code)
);

-- Languages table
CREATE TABLE IF NOT EXISTS languages (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    lang TEXT NOT NULL,
    area TEXT,
    code2 TEXT
);

-- Countries table
CREATE TABLE IF NOT EXISTS countries (
    id INTEGER PRIMARY KEY,
    ccode TEXT NOT NULL UNIQUE,
    cname TEXT NOT NULL
);

-- Areas table
CREATE TABLE IF NOT EXISTS area (
    id INTEGER PRIMARY KEY,
    acode TEXT NOT NULL UNIQUE,
    aname TEXT NOT NULL
);

-- Main broadcasts table
CREATE TABLE IF NOT EXISTS broadcasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    frequency_khz REAL NOT NULL,
    start_time TEXT,              -- HHMM format
    end_time TEXT,                -- HHMM format
    days_operation TEXT,          -- Days/operation modes
    country_id INTEGER,
    station_name TEXT NOT NULL,
    language_id INTEGER,
    target_area_id INTEGER,
    transmitter_site TEXT,        -- Transmitter site code
    persistence_code INTEGER,     -- Persistence code (1-8, 90+)
    start_date TEXT,              -- Start date (MMDD)
    end_date TEXT,                -- End date (MMDD)
    remarks TEXT,                 -- Notes and comments
    fleibi INTEGER DEFAULT 0,     -- Eibi imported flag
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_id) REFERENCES countries(id),
    FOREIGN KEY (language_id) REFERENCES languages(id),
    FOREIGN KEY (target_area_id) REFERENCES area(id)
);

-- Frequency bands table for quick searches
CREATE TABLE IF NOT EXISTS frequency_bands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    band_name TEXT NOT NULL UNIQUE,
    freq_start REAL NOT NULL,
    freq_end REAL NOT NULL,
    description TEXT
);

-- Table for changes history
CREATE TABLE IF NOT EXISTS broadcast_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    broadcast_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (broadcast_id) REFERENCES broadcasts(id)
);

-- =============================================
-- INDEXES
-- =============================================

-- Indexes for frequency searches
CREATE INDEX IF NOT EXISTS idx_broadcasts_frequency ON broadcasts(frequency_khz);
CREATE INDEX IF NOT EXISTS idx_broadcasts_freq_range ON broadcasts(frequency_khz, start_time, end_time);

-- Indexes for station searches
CREATE INDEX IF NOT EXISTS idx_broadcasts_station ON broadcasts(station_name);
CREATE INDEX IF NOT EXISTS idx_broadcasts_station_country ON broadcasts(station_name, country_id);

-- Indexes for geographical searches
CREATE INDEX IF NOT EXISTS idx_broadcasts_country ON broadcasts(country_id);
CREATE INDEX IF NOT EXISTS idx_broadcasts_target_area ON broadcasts(target_area_id);
CREATE INDEX IF NOT EXISTS idx_broadcasts_transmitter ON broadcasts(transmitter_site);

-- Indexes for linguistic searches
CREATE INDEX IF NOT EXISTS idx_broadcasts_language ON broadcasts(language_id);

-- Indexes for temporal searches
CREATE INDEX IF NOT EXISTS idx_broadcasts_time ON broadcasts(start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_broadcasts_days ON broadcasts(days_operation);
CREATE INDEX IF NOT EXISTS idx_broadcasts_dates ON broadcasts(start_date, end_date);

-- Indexes for technical searches
CREATE INDEX IF NOT EXISTS idx_broadcasts_persistence ON broadcasts(persistence_code);
CREATE INDEX IF NOT EXISTS idx_broadcasts_active ON broadcasts(persistence_code) WHERE persistence_code != 8;

-- Composite indexes for complex searches
CREATE INDEX IF NOT EXISTS idx_compound_geo_lang ON broadcasts(country_id, language_id, target_area_id);
CREATE INDEX IF NOT EXISTS idx_compound_freq_time ON broadcasts(frequency_khz, start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_compound_station_freq ON broadcasts(station_name, frequency_khz);

-- Indexes for support tables
CREATE INDEX IF NOT EXISTS idx_transmitters_lookup ON transmitters(country_code, site_code);
CREATE INDEX IF NOT EXISTS idx_transmitters_location ON transmitters(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_countries_code ON countries(ccode);
CREATE INDEX IF NOT EXISTS idx_languages_code ON languages(code);
CREATE INDEX IF NOT EXISTS idx_area_code ON area(acode);

-- Indexes for frequency bands
CREATE INDEX IF NOT EXISTS idx_frequency_bands_range ON frequency_bands(freq_start, freq_end);
CREATE INDEX IF NOT EXISTS idx_frequency_bands_name ON frequency_bands(band_name);

-- Indexes for history (if used)
CREATE INDEX IF NOT EXISTS idx_history_broadcast ON broadcast_history(broadcast_id);
CREATE INDEX IF NOT EXISTS idx_history_date ON broadcast_history(changed_at);

-- =============================================
-- VIEWS
-- =============================================

-- Complete view of broadcasts with all details
CREATE VIEW IF NOT EXISTS broadcasts_complete AS
SELECT
    b.id,
    b.frequency_khz,
    b.start_time,
    b.end_time,
    b.days_operation,
    c.ccode as country_code,
    c.cname as country_name,
    b.station_name,
    l.code as language_code,
    l.lang as language_name,
    a.acode as target_area_code,
    a.aname as target_area_name,
    b.transmitter_site,
    t.name as transmitter_name,
    t.latitude as transmitter_lat,
    t.longitude as transmitter_lng,
    b.persistence_code,
    CASE
        WHEN b.persistence_code = 1 THEN 'Permanent'
        WHEN b.persistence_code = 2 THEN 'Permanent (DST North)'
        WHEN b.persistence_code = 3 THEN 'Permanent (DST South)'
        WHEN b.persistence_code = 4 THEN 'Winter only'
        WHEN b.persistence_code = 5 THEN 'Summer only'
        WHEN b.persistence_code = 6 THEN 'Temporary'
        WHEN b.persistence_code = 8 THEN 'Inactive'
        WHEN b.persistence_code >= 90 THEN 'Utility station'
        ELSE 'Unknown'
    END as persistence_description,
    b.start_date,
    b.end_date,
    b.remarks,
    fb.band_name,
    fb.description as band_description,
    b.created_at,
    b.updated_at
FROM broadcasts b
LEFT JOIN countries c ON b.country_id = c.id
LEFT JOIN languages l ON b.language_id = l.id
LEFT JOIN area a ON b.target_area_id = a.id
LEFT JOIN transmitters t ON b.transmitter_site = t.site_code AND c.ccode = t.country_code
LEFT JOIN frequency_bands fb ON b.frequency_khz >= fb.freq_start AND b.frequency_khz < fb.freq_end;

-- View for quick statistics
CREATE VIEW IF NOT EXISTS broadcast_stats AS
SELECT
    COUNT(*) as total_broadcasts,
    COUNT(DISTINCT station_name) as unique_stations,
    COUNT(DISTINCT country_id) as active_countries,
    COUNT(DISTINCT language_id) as languages_used,
    MIN(frequency_khz) as min_frequency,
    MAX(frequency_khz) as max_frequency,
    AVG(frequency_khz) as avg_frequency
FROM broadcasts
WHERE persistence_code != 8;  -- Exclude inactive stations

-- =============================================
-- TRIGGERS
-- =============================================

-- Trigger to update modification timestamp
CREATE TRIGGER IF NOT EXISTS update_broadcast_timestamp
    AFTER UPDATE ON broadcasts
    FOR EACH ROW
BEGIN
    UPDATE broadcasts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger for changes logging (optional)
CREATE TRIGGER IF NOT EXISTS log_broadcast_changes
    AFTER UPDATE ON broadcasts
    FOR EACH ROW
BEGIN
    INSERT INTO broadcast_history (broadcast_id, field_name, old_value, new_value)
    SELECT NEW.id, 'frequency_khz', OLD.frequency_khz, NEW.frequency_khz
    WHERE OLD.frequency_khz != NEW.frequency_khz
    UNION ALL
    SELECT NEW.id, 'station_name', OLD.station_name, NEW.station_name
    WHERE OLD.station_name != NEW.station_name
    UNION ALL
    SELECT NEW.id, 'start_time', OLD.start_time, NEW.start_time
    WHERE OLD.start_time != NEW.start_time;
END;

