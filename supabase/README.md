# Supabase Database Setup

This directory contains SQL migrations for the JobAutomate platform database.

## Quick Setup

### Option 1: Supabase Dashboard (Easiest)

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and paste each migration file in order:
   - `001_initial_schema.sql`
   - `002_row_level_security.sql`
4. Run each migration

### Option 2: Supabase CLI

```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_REF

# Push migrations
supabase db push
```

## Database Schema

### Tables

1. **profiles** - User profiles (extends auth.users)
   - Stores resume, contact info, preferences

2. **jobs** - Job listings
   - Scraped from various job boards
   - Indexed for fast search

3. **job_matches** - AI match scores
   - Links users to jobs with match percentage
   - Stores AI analysis

4. **applications** - Application tracking
   - Status, notes, interview dates
   - Automation status

5. **automation_logs** - Activity logs
   - Debugging and monitoring
   - Performance metrics

6. **saved_searches** - User saved searches
   - Auto-apply settings
   - Notification preferences

## Row Level Security (RLS)

All tables have RLS enabled:
- Users can only access their own data
- Jobs are public (read-only)
- Service role can insert system data

## Getting Your Supabase Credentials

1. Go to https://supabase.com/dashboard
2. Create a new project (or select existing)
3. Go to Settings > API
4. Copy:
   - Project URL
   - Anon/Public Key
   - Service Role Key (keep secret!)

5. Update `.env.local` in frontend:
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## Migrations

Migrations are numbered and should be run in order:
- `001` - Initial schema (tables, indexes, triggers)
- `002` - Row Level Security policies

## Testing

After running migrations, verify:

```sql
-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';

-- Test profile creation
SELECT * FROM profiles LIMIT 1;
```

## Troubleshooting

### Migration fails with "permission denied"
- Make sure you're using the service role key or dashboard SQL editor

### Tables already exist
- Drop existing tables: `DROP TABLE IF EXISTS table_name CASCADE;`
- Or modify migration to use `CREATE TABLE IF NOT EXISTS`

### RLS blocks all access
- Check you're authenticated: `SELECT auth.uid();`
- Verify policies match your use case

## Need Help?

See main README or open an issue on GitHub.
