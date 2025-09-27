-- Weather Briefings Table Schema for Supabase
-- This table stores generated weather briefings for retrieval and historical analysis

CREATE TABLE IF NOT EXISTS weather_briefings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    briefing_id VARCHAR(50) UNIQUE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Route Information
    route_type VARCHAR(20) NOT NULL CHECK (route_type IN ('single', 'multi_airport')),
    airports TEXT[] NOT NULL,
    detail_level VARCHAR(20) NOT NULL CHECK (detail_level IN ('summary', 'detailed')),
    
    -- Core Briefing Content
    executive_summary TEXT,
    weather_data JSONB,
    ml_predictions JSONB,
    risk_assessment JSONB,
    
    -- Optional Features
    alternative_routes JSONB,
    flight_monitoring_enabled BOOLEAN DEFAULT FALSE,
    monitoring_id VARCHAR(50),
    
    -- Metadata
    data_sources TEXT[],
    generated_at TIMESTAMPTZ NOT NULL,
    last_updated TIMESTAMPTZ NOT NULL,
    valid_until TIMESTAMPTZ NOT NULL,
    
    -- Status
    success BOOLEAN NOT NULL DEFAULT TRUE,
    message TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_weather_briefings_briefing_id ON weather_briefings(briefing_id);
CREATE INDEX IF NOT EXISTS idx_weather_briefings_user_id ON weather_briefings(user_id);
CREATE INDEX IF NOT EXISTS idx_weather_briefings_generated_at ON weather_briefings(generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_weather_briefings_valid_until ON weather_briefings(valid_until);
CREATE INDEX IF NOT EXISTS idx_weather_briefings_airports ON weather_briefings USING GIN(airports);

-- Row Level Security (RLS)
ALTER TABLE weather_briefings ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own briefings
CREATE POLICY "Users can view their own weather briefings" ON weather_briefings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own weather briefings" ON weather_briefings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own weather briefings" ON weather_briefings
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own weather briefings" ON weather_briefings
    FOR DELETE USING (auth.uid() = user_id);

-- Policy: Allow anonymous access for briefings without user_id
CREATE POLICY "Allow anonymous access to public briefings" ON weather_briefings
    FOR SELECT USING (user_id IS NULL);

CREATE POLICY "Allow anonymous insertion of public briefings" ON weather_briefings
    FOR INSERT WITH CHECK (user_id IS NULL);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_weather_briefings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER update_weather_briefings_updated_at
    BEFORE UPDATE ON weather_briefings
    FOR EACH ROW EXECUTE FUNCTION update_weather_briefings_updated_at();

-- Function to clean up expired briefings (can be called periodically)
CREATE OR REPLACE FUNCTION cleanup_expired_weather_briefings()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM weather_briefings WHERE valid_until < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE weather_briefings IS 'Stores generated weather briefings for flight routes';
COMMENT ON COLUMN weather_briefings.briefing_id IS 'Unique identifier for the briefing (e.g., WB-20250927-001)';
COMMENT ON COLUMN weather_briefings.route_type IS 'Type of route: single (2 airports) or multi_airport (3+ airports)';
COMMENT ON COLUMN weather_briefings.airports IS 'Array of ICAO airport codes in route order';
COMMENT ON COLUMN weather_briefings.weather_data IS 'JSONB containing weather data for each airport';
COMMENT ON COLUMN weather_briefings.ml_predictions IS 'JSONB containing ML model predictions';
COMMENT ON COLUMN weather_briefings.risk_assessment IS 'JSONB containing risk analysis and recommendations';
COMMENT ON COLUMN weather_briefings.valid_until IS 'Timestamp when the briefing expires and can be cleaned up';