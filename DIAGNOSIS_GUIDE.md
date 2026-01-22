# Auto-Apply "In Progress" Diagnosis Guide

## ✅ Backend Status
Your Railway logs show:
- ✅ Backend container starting successfully
- ✅ Playwright dependencies installing (required for automation)
- ✅ Uvicorn server running on port 8000

**These are STARTUP logs** - we need RUNTIME logs to diagnose the "in_progress" issue.

## 🔍 Critical Issues to Verify

### 1. Database Migration 003 - MUST CHECK FIRST

**Action Required:**
1. Go to Supabase Dashboard → SQL Editor
2. Run this query to check if columns exist:
```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'applications' 
AND column_name IN ('error_code', 'error_message', 'retry_count', 'application_outcome', 'last_attempted_at');
```

**Expected Result:** Should return 5 rows (one for each column)

**If columns are MISSING:**
- Run migration 003 in Supabase SQL Editor:
```sql
-- Copy and paste the entire content of:
-- supabase/migrations/003_add_error_tracking.sql
```

### 2. Frontend User ID - ✅ FIXED

**Status:** Just fixed - now uses real user.id instead of hardcoded "test-user-id"

**What was wrong:**
- Frontend was sending `user_id: "test-user-id"` 
- Backend couldn't find profile for this fake user
- Background task would fail silently

**What's fixed:**
- AutoApplyButton now accepts `userId` prop
- Page component passes `user.id` from Supabase auth
- Real user_id is now sent to backend

### 3. Background Task Execution - NEEDS VERIFICATION

**Check Railway Runtime Logs:**
After triggering auto-apply, look for these log messages:

**Expected logs if working:**
```
Starting auto-apply for application {id}
[{id}] Step 1: Starting form extraction
[{id}] Step 2: Filling form fields
[{id}] Step 3: Submitting form (running script)
```

**If you see timeout:**
```
AUTO-APPLY TIMEOUT: Application {id} took > 5 minutes
```

**If you see errors:**
```
Error in fill_and_apply: {error message}
```

**If you see NOTHING:**
- Background tasks may not be executing
- Check Railway configuration for background task support

## 📊 Step-by-Step Diagnosis Process

### Step 1: Verify Database Schema
```sql
-- Run in Supabase SQL Editor
SELECT 
  column_name, 
  data_type, 
  is_nullable
FROM information_schema.columns 
WHERE table_name = 'applications' 
AND column_name IN (
  'error_code', 
  'error_message', 
  'retry_count', 
  'application_outcome',
  'last_attempted_at'
);
```

**If missing:** Apply migration 003 immediately

### Step 2: Trigger Auto-Apply and Monitor

1. **Trigger auto-apply** on a test job
2. **Immediately check database:**
```sql
SELECT 
  id,
  automation_status,
  error_code,
  error_message,
  retry_count,
  last_attempted_at,
  created_at,
  updated_at
FROM applications
ORDER BY created_at DESC
LIMIT 1;
```

**Expected immediately after click:**
- `automation_status`: "queued" or "in_progress"
- `error_code`: NULL
- `error_message`: NULL

3. **Check Railway logs** for:
   - "Starting auto-apply"
   - "Step 1", "Step 2", "Step 3"
   - Any error messages

### Step 3: Wait 5 Minutes and Check Again

**After 5 minutes, check database again:**
```sql
SELECT 
  id,
  automation_status,
  error_code,
  error_message,
  retry_count,
  last_attempted_at,
  updated_at
FROM applications
WHERE id = '{your_application_id}';
```

**Expected outcomes:**

**If timeout occurred:**
- `automation_status`: "failed"
- `error_code`: "timeout"
- `error_message`: "Form filling timeout: Process exceeded 5 minute limit"

**If exception occurred:**
- `automation_status`: "failed"
- `error_code`: "exception"
- `error_message`: {error details}

**If still "in_progress":**
- Background task may not be running
- Check Railway logs for errors
- Verify FastAPI background tasks are supported

### Step 4: Check Automation Logs

```sql
SELECT 
  action,
  success,
  error_code,
  metadata,
  created_at
FROM automation_logs
WHERE application_id = '{your_application_id}'
ORDER BY created_at DESC;
```

**Expected logs:**
- `form_extraction_started` (success: true)
- `form_filling_timeout` or `form_filling_error` (if failed)
- Or `form_filled_success` (if completed)

## 🐛 Common Root Causes

### Cause 1: Migration Not Applied (HIGH PROBABILITY)
**Symptom:** `error_code` and `error_message` are NULL even after timeout
**Fix:** Apply migration 003 in Supabase

### Cause 2: Background Tasks Not Running
**Symptom:** No logs appear after triggering auto-apply
**Fix:** 
- Check Railway configuration
- Verify FastAPI BackgroundTasks are supported
- May need to use Celery or similar for production

### Cause 3: JOB_AUTOMATOR_PATH Not Set
**Symptom:** Status stays "queued" or "in_progress" indefinitely
**Fix:** Set `JOB_AUTOMATOR_PATH` environment variable in Railway

### Cause 4: Profile Not Found
**Symptom:** Background task fails silently
**Fix:** ✅ Already fixed - now uses real user_id

## 🔧 Quick Fixes Applied

1. ✅ **Fixed frontend user_id** - Now uses real user from auth
2. ✅ **All Phase 1 code verified** - Timeout, error handling, logging all present

## 📝 Next Actions

1. **Apply migration 003** if columns are missing
2. **Trigger test auto-apply** and monitor logs
3. **Check database** immediately and after 5 minutes
4. **Share results** for further diagnosis

## 📞 What to Share for Further Help

If still stuck, provide:

1. **Database schema check result:**
   ```sql
   -- Run and share output
   SELECT column_name FROM information_schema.columns 
   WHERE table_name = 'applications' 
   AND column_name IN ('error_code', 'error_message');
   ```

2. **Application record after 5 minutes:**
   ```sql
   -- Share the full row
   SELECT * FROM applications 
   WHERE id = '{latest_application_id}';
   ```

3. **Railway logs** (last 50 lines after triggering auto-apply)

4. **Automation logs:**
   ```sql
   SELECT * FROM automation_logs 
   WHERE application_id = '{latest_application_id}'
   ORDER BY created_at DESC;
   ```
