-- Migration 004: Add submission tracking fields to applications table
-- Adds fields to track successful form submissions and confirmation URLs

-- Add submission_confirmed column
ALTER TABLE applications 
ADD COLUMN IF NOT EXISTS submission_confirmed BOOLEAN DEFAULT FALSE;

-- Add submitted_application_url column
ALTER TABLE applications 
ADD COLUMN IF NOT EXISTS submitted_application_url VARCHAR(1000);

-- Add comment for documentation
COMMENT ON COLUMN applications.submission_confirmed IS 'Whether the form submission was confirmed (true) or not (false)';
COMMENT ON COLUMN applications.submitted_application_url IS 'URL of the confirmation page after successful form submission';

-- Create index for faster queries on submission status
CREATE INDEX IF NOT EXISTS idx_applications_submission_confirmed 
ON applications(user_id, submission_confirmed) 
WHERE submission_confirmed = TRUE;

-- Migration complete
