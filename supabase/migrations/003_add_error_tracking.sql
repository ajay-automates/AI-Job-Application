-- Migration: Add error tracking and retry columns for Phase 1
-- Date: 2026-01-21

ALTER TABLE applications ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS last_attempted_at TIMESTAMPTZ;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS error_code VARCHAR(100);
ALTER TABLE applications ADD COLUMN IF NOT EXISTS error_message TEXT;
ALTER TABLE applications ADD COLUMN IF NOT EXISTS application_outcome VARCHAR(50); -- 'interview_scheduled', 'rejected', 'no_response', 'pending'
ALTER TABLE applications ADD COLUMN IF NOT EXISTS outcome_recorded_at TIMESTAMPTZ;

-- Create index for quick lookup of failed applications
CREATE INDEX IF NOT EXISTS idx_applications_outcome ON applications(application_outcome);
CREATE INDEX IF NOT EXISTS idx_applications_error_code ON applications(error_code);
