-- Row Level Security (RLS) Policies
-- Ensures users can only access their own data

-- ============================================================================
-- ENABLE RLS ON ALL TABLES
-- ============================================================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE automation_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_searches ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- PROFILES TABLE POLICIES
-- Users can only view and update their own profile
-- ============================================================================
CREATE POLICY "Users can view own profile"
  ON profiles
  FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON profiles
  FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
  ON profiles
  FOR INSERT
  WITH CHECK (auth.uid() = id);

-- ============================================================================
-- JOBS TABLE POLICIES
-- Jobs are public (anyone can read), only system can write
-- ============================================================================
CREATE POLICY "Anyone can view active jobs"
  ON jobs
  FOR SELECT
  USING (is_active = TRUE);

-- Allow service role to insert/update jobs (for scraping)
CREATE POLICY "Service role can insert jobs"
  ON jobs
  FOR INSERT
  WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role can update jobs"
  ON jobs
  FOR UPDATE
  USING (auth.role() = 'service_role');

-- ============================================================================
-- JOB_MATCHES TABLE POLICIES
-- Users can only view their own matches
-- ============================================================================
CREATE POLICY "Users can view own matches"
  ON job_matches
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own matches"
  ON job_matches
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own matches"
  ON job_matches
  FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own matches"
  ON job_matches
  FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================================
-- APPLICATIONS TABLE POLICIES
-- Users can only view and manage their own applications
-- ============================================================================
CREATE POLICY "Users can view own applications"
  ON applications
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own applications"
  ON applications
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own applications"
  ON applications
  FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own applications"
  ON applications
  FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================================
-- AUTOMATION_LOGS TABLE POLICIES
-- Users can view their own logs, service role can insert
-- ============================================================================
CREATE POLICY "Users can view own logs"
  ON automation_logs
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Service role can insert logs"
  ON automation_logs
  FOR INSERT
  WITH CHECK (auth.role() = 'service_role' OR auth.uid() = user_id);

-- ============================================================================
-- SAVED_SEARCHES TABLE POLICIES
-- Users can manage their own saved searches
-- ============================================================================
CREATE POLICY "Users can view own saved searches"
  ON saved_searches
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own saved searches"
  ON saved_searches
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own saved searches"
  ON saved_searches
  FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own saved searches"
  ON saved_searches
  FOR DELETE
  USING (auth.uid() = user_id);

-- RLS policies complete
