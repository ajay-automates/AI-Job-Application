-- Initial Schema Migration for JobAutomate Platform
-- Run this migration in your Supabase SQL Editor or via Supabase CLI

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- PROFILES TABLE
-- Extends Supabase auth.users with additional profile information
-- ============================================================================
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  resume_text TEXT,
  resume_url VARCHAR(500),
  phone VARCHAR(50),
  location VARCHAR(255),
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- JOBS TABLE
-- Stores scraped job listings from various sources
-- ============================================================================
CREATE TABLE IF NOT EXISTS jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(500) NOT NULL,
  company VARCHAR(255) NOT NULL,
  url VARCHAR(1000) UNIQUE NOT NULL,
  description TEXT,
  location VARCHAR(255),
  salary_min INTEGER,
  salary_max INTEGER,
  salary_currency VARCHAR(10) DEFAULT 'USD',
  job_type VARCHAR(50), -- 'full-time', 'part-time', 'contract'
  remote_type VARCHAR(50), -- 'remote', 'hybrid', 'onsite'
  posted_date TIMESTAMPTZ,
  expires_date TIMESTAMPTZ,
  source VARCHAR(100), -- 'greenhouse', 'lever', 'workday', etc.
  raw_data JSONB,
  scraped_at TIMESTAMPTZ DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for jobs table
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_posted ON jobs(posted_date DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_active ON jobs(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_jobs_url ON jobs(url);

-- ============================================================================
-- JOB_MATCHES TABLE
-- Stores AI-calculated match scores between users and jobs
-- ============================================================================
CREATE TABLE IF NOT EXISTS job_matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  match_score FLOAT NOT NULL CHECK (match_score >= 0 AND match_score <= 100),
  match_reasons JSONB,
  ai_analysis TEXT,
  is_favorited BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, job_id)
);

-- Create indexes for job_matches table
CREATE INDEX IF NOT EXISTS idx_matches_user_score ON job_matches(user_id, match_score DESC);
CREATE INDEX IF NOT EXISTS idx_matches_favorited ON job_matches(user_id, is_favorited) WHERE is_favorited = TRUE;
CREATE INDEX IF NOT EXISTS idx_matches_job ON job_matches(job_id);

-- ============================================================================
-- APPLICATIONS TABLE
-- Tracks user job applications and their status
-- ============================================================================
CREATE TABLE IF NOT EXISTS applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  -- Status values: 'pending', 'in_progress', 'applied', 'interview', 'offer', 'rejected', 'withdrawn'
  applied_at TIMESTAMPTZ,
  form_data JSONB,
  cover_letter TEXT,
  notes TEXT,
  interview_date TIMESTAMPTZ,
  follow_up_date TIMESTAMPTZ,
  automation_enabled BOOLEAN DEFAULT FALSE,
  automation_status VARCHAR(50), -- 'queued', 'extracting', 'filling', 'completed', 'failed'
  automation_error TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for applications table
CREATE INDEX IF NOT EXISTS idx_applications_user_status ON applications(user_id, status);
CREATE INDEX IF NOT EXISTS idx_applications_user_date ON applications(user_id, applied_at DESC);
CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id);

-- ============================================================================
-- AUTOMATION_LOGS TABLE
-- Tracks automation activity for debugging and monitoring
-- ============================================================================
CREATE TABLE IF NOT EXISTS automation_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
  job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
  application_id UUID REFERENCES applications(id) ON DELETE SET NULL,
  action VARCHAR(100) NOT NULL,
  -- Actions: 'job_scraped', 'form_extracted', 'form_filled', 'application_submitted', 'match_calculated'
  success BOOLEAN NOT NULL,
  error_message TEXT,
  metadata JSONB,
  duration_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for automation_logs table
CREATE INDEX IF NOT EXISTS idx_logs_user_date ON automation_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_application ON automation_logs(application_id);
CREATE INDEX IF NOT EXISTS idx_logs_action ON automation_logs(action, created_at DESC);

-- ============================================================================
-- SAVED_SEARCHES TABLE
-- Stores user's saved job search queries
-- ============================================================================
CREATE TABLE IF NOT EXISTS saved_searches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  query_params JSONB NOT NULL,
  auto_apply BOOLEAN DEFAULT FALSE,
  notify_new_matches BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for saved_searches table
CREATE INDEX IF NOT EXISTS idx_saved_searches_user ON saved_searches(user_id);

-- ============================================================================
-- TRIGGERS
-- Automatically update updated_at timestamps
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_applications_updated_at
  BEFORE UPDATE ON applications
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- FUNCTIONS
-- Helper functions for common operations
-- ============================================================================

-- Function to create profile on user signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically create profile when user signs up
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();

-- ============================================================================
-- COMMENTS
-- Add helpful comments to tables and columns
-- ============================================================================
COMMENT ON TABLE profiles IS 'User profiles extending auth.users';
COMMENT ON TABLE jobs IS 'Scraped job listings from various sources';
COMMENT ON TABLE job_matches IS 'AI-calculated match scores between users and jobs';
COMMENT ON TABLE applications IS 'User job applications and their status';
COMMENT ON TABLE automation_logs IS 'Logs of automation activity';
COMMENT ON TABLE saved_searches IS 'User saved job search queries';

-- Migration complete
