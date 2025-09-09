-- Add Google Analytics fields to settings table
ALTER TABLE settings 
ADD COLUMN google_analytics_tracking_id VARCHAR(255),
ADD COLUMN google_analytics_measurement_id VARCHAR(255),
ADD COLUMN google_analytics_api_key VARCHAR(255),
ADD COLUMN google_analytics_enabled BOOLEAN DEFAULT FALSE;