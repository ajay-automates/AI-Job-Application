# 🧪 Manual Testing Guide - JobAutomate Platform

**Date**: January 20, 2026  
**Status**: Both Backend and Frontend Running Successfully

---

## ✅ Services Currently Running

### Backend API
- **URL**: http://localhost:8000/api/docs
- **Status**: ✅ Running (1h 52m uptime)
- **Health**: Verified healthy

### Frontend
- **URL**: http://localhost:3000
- **Status**: ✅ Running (54m uptime)
- **Pages**: All accessible

### Database
- **Provider**: Supabase Cloud
- **Status**: ✅ Connected
- **URL**: https://bbsombmpefldgjflwjsr.supabase.co

---

## 🔐 Your Login Credentials

**Email**: ajaykumarreddynelavetla@gmail.com  
**Password**: Aj@y3303

---

## 📝 Step-by-Step Testing Instructions

### Test 1: Login to Dashboard

1. **Open your browser** and go to: http://localhost:3000

2. **Click "Login"** button in the top right

3. **Enter your credentials**:
   - Email: ajaykumarreddynelavetla@gmail.com
   - Password: Aj@y3303

4. **Click "Sign in"**

5. **Expected Result**: 
   - Should redirect to http://localhost:3000/dashboard
   - Should see your dashboard with stats
   - Should see navigation sidebar

6. **What to Check**:
   - ✅ Login successful?
   - ✅ Dashboard loads?
   - ✅ Stats cards visible?
   - ✅ Navigation menu works?

---

### Test 2: Profile & Resume Upload

1. **Click "Profile"** in the sidebar

2. **Check your profile information**:
   - Full name displayed?
   - Email displayed?
   - Phone number (if set)?

3. **Upload Resume**:
   - Scroll to "Resume" section
   - Either:
     - **Option A**: Click "Choose File" and select a .txt resume file
     - **Option B**: Paste your resume text in the textarea
   - Click "Upload Resume" or "Save"

4. **Expected Result**:
   - Success toast: "Resume uploaded successfully!"
   - Another toast: "AI Matching Started!"
   - Resume text should appear in the textarea

5. **What to Check**:
   - ✅ Resume uploaded?
   - ✅ Success messages shown?
   - ✅ Text persists after page refresh?

---

### Test 3: View Jobs

1. **Click "Jobs"** in the sidebar

2. **Browse the jobs list**:
   - How many jobs are shown?
   - Do you see job cards with:
     - Job title?
     - Company name?
     - Location?
     - Salary (if available)?
     - Match score badge (if resume uploaded)?

3. **Try filters**:
   - Search by keyword
   - Filter by location
   - Filter by job type

4. **Click "View Details"** on any job:
   - Full job description visible?
   - Company details shown?
   - Match analysis (if resume uploaded)?
   - "Auto Apply" button present?

5. **What to Check**:
   - ✅ Jobs list loads?
   - ✅ Job details page works?
   - ✅ Match scores appear (if resume uploaded)?
   - ✅ Filters work?

---

### Test 4: Applications Tracking

1. **Click "Applications"** in the sidebar

2. **View existing applications**:
   - List of your applications shown?
   - Status badges (Applied, Pending, Interview, etc.)?
   - Application dates?

3. **Create new application** (if button available):
   - Click "New Application"
   - Fill in job details manually
   - Select status
   - Add notes
   - Click "Create"

4. **What to Check**:
   - ✅ Applications list loads?
   - ✅ Can create new application?
   - ✅ Status updates work?
   - ✅ Notes save correctly?

---

### Test 5: AI Job Matching

**Prerequisites**: Resume must be uploaded (Test 2)

1. **Wait 1-2 minutes** after uploading resume

2. **Go to Dashboard**:
   - Check "Top Matches" section
   - Do you see jobs with high match scores?

3. **Go to Jobs page**:
   - Do job cards show match percentage badges?
   - Are scores reasonable (0-100%)?

4. **Click on a high-match job**:
   - View job details
   - Check "AI Match Analysis" section
   - Read match reasons

5. **What to Check**:
   - ✅ Match scores appear on jobs?
   - ✅ Top matches show on dashboard?
   - ✅ Match analysis makes sense?
   - ✅ Scores update after resume change?

---

### Test 6: Job Scraping (If Available)

1. **Go to Jobs page**

2. **Click "Scrape New Jobs"** button (if visible)

3. **Fill in the modal**:
   - Keywords: "Software Engineer" (or your preference)
   - Location: "Remote" (optional)
   - Click "Start Scraping"

4. **Expected Result**:
   - Loading indicator
   - Success toast: "Job Scraping Started! 🎯"
   - Wait 30-60 seconds
   - Refresh page
   - New jobs should appear

5. **What to Check**:
   - ✅ Scraping modal opens?
   - ✅ Can enter keywords?
   - ✅ Success message shown?
   - ✅ New jobs appear after refresh?

**Note**: Job scraping requires the job-board-aggregator service, which has a macOS issue locally. This feature works in production.

---

### Test 7: Auto-Apply Feature

**Prerequisites**: Resume uploaded

1. **Go to Jobs page**

2. **Find a job** with high match score

3. **Click "Auto Apply"** button

4. **Confirm in dialog**:
   - Job details shown?
   - Click "Start Auto-Apply" or "Confirm"

5. **Expected Result**:
   - Loading state
   - Success toast: "Auto-Apply Started! 🚀"
   - Application created
   - Check Applications page for new entry

6. **What to Check**:
   - ✅ Auto-apply button works?
   - ✅ Confirmation dialog appears?
   - ✅ Application created?
   - ✅ Status updated?

**Note**: Full browser automation requires additional setup. The application record should be created even if automation doesn't run.

---

### Test 8: Backend API (Advanced)

1. **Open**: http://localhost:8000/api/docs

2. **Test Health Endpoint**:
   - Find `/health` endpoint
   - Click "Try it out"
   - Click "Execute"
   - Should return: `{"status": "healthy"}`

3. **Test Jobs Endpoint**:
   - Find `GET /api/jobs`
   - Click "Try it out"
   - Click "Execute"
   - Should return list of jobs

4. **What to Check**:
   - ✅ API docs load?
   - ✅ Health check works?
   - ✅ Jobs endpoint returns data?
   - ✅ All endpoints documented?

---

## 🐛 Common Issues & Solutions

### Issue: "Cannot connect to server"
**Solution**: 
- Check if backend is running: http://localhost:8000
- Check if frontend is running: http://localhost:3000
- Restart servers if needed

### Issue: "Login failed" or "Invalid credentials"
**Solution**:
- Verify you're using correct email: ajaykumarreddynelavetla@gmail.com
- Verify password: Aj@y3303
- Check browser console for errors (F12)
- Try resetting password in Supabase dashboard

### Issue: "Resume upload fails"
**Solution**:
- Use .txt file format
- Keep file size under 1MB
- Try pasting text instead of uploading file
- Check browser console for errors

### Issue: "No jobs showing"
**Solution**:
- Jobs may not be in database yet
- Try scraping new jobs (if aggregator running)
- Check backend API: http://localhost:8000/api/docs
- Test `GET /api/jobs` endpoint directly

### Issue: "Match scores not appearing"
**Solution**:
- Ensure resume is uploaded
- Wait 1-2 minutes for AI matching
- Refresh the page
- Check if OpenAI API key is configured
- Check backend logs for errors

### Issue: "Auto-apply doesn't work"
**Solution**:
- This requires form filler setup
- Application record should still be created
- Check Applications page for the entry
- Full automation works in production

---

## 📊 What to Document

As you test, please note:

### ✅ Working Features:
- [ ] Login/Logout
- [ ] Dashboard loads
- [ ] Profile page
- [ ] Resume upload
- [ ] Jobs list
- [ ] Job details
- [ ] Applications list
- [ ] Create application
- [ ] AI matching (if resume uploaded)
- [ ] Match scores display
- [ ] Job scraping (if aggregator running)
- [ ] Auto-apply button

### ❌ Issues Found:
For each issue, note:
1. What you were trying to do
2. What happened instead
3. Any error messages
4. Screenshot if possible
5. Browser console errors (F12 → Console tab)

---

## 🎯 Success Criteria

Your local environment is working correctly if:

1. ✅ You can login successfully
2. ✅ Dashboard shows your stats
3. ✅ You can upload resume
4. ✅ Jobs list displays
5. ✅ Job details page works
6. ✅ Applications tracking works
7. ✅ Match scores appear (after resume upload)
8. ✅ No console errors during normal use

---

## 📞 Next Steps After Testing

### If Everything Works:
1. Document that local environment matches production
2. Test production at: https://ai-job-application-six.vercel.app
3. Compare local vs production behavior
4. Identify any production-specific issues

### If Issues Found:
1. Document each issue clearly
2. Check browser console for errors
3. Check backend logs (terminal where backend is running)
4. Take screenshots of errors
5. We'll fix issues one by one

---

## 🔧 Server Management

### To Stop Servers:
```bash
# In terminal where backend is running:
Ctrl+C

# In terminal where frontend is running:
Ctrl+C
```

### To Restart Servers:

**Backend**:
```bash
cd "/Users/ajaykumarreddy/Desktop/PROJECTS/Job Application MCP/job-automation-platform/backend"
source venv/bin/activate
python -m app.main
```

**Frontend**:
```bash
cd "/Users/ajaykumarreddy/Desktop/PROJECTS/Job Application MCP/job-automation-platform/frontend"
npm run dev
```

### To Check Server Status:
```bash
# Check if backend is running:
curl http://localhost:8000/health

# Check if frontend is running:
curl http://localhost:3000
```

---

## 📝 Testing Checklist

Print this and check off as you test:

- [ ] **Test 1**: Login successful
- [ ] **Test 2**: Resume upload works
- [ ] **Test 3**: Jobs list displays
- [ ] **Test 4**: Applications tracking works
- [ ] **Test 5**: AI matching shows scores
- [ ] **Test 6**: Job scraping (if available)
- [ ] **Test 7**: Auto-apply creates application
- [ ] **Test 8**: Backend API accessible

**Total Tests**: 8  
**Passed**: ___  
**Failed**: ___  
**Skipped**: ___

---

**Happy Testing! 🚀**

Your local environment is ready. Both backend and frontend are running successfully!
