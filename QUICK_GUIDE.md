# 🚀 JobAutomate - Quick User Guide

Your platform is LIVE! Here's how to use it:

## 🎯 Step 1: Create Your Account (1 minute)

1. You should see the landing page at http://localhost:3000
2. Click **"Sign Up"** (top right or hero button)
3. Fill in:
   - **Full Name**: Your name
   - **Email**: Your email address
   - **Password**: At least 8 characters
4. Click **"Create Account"**
5. ✅ You'll be redirected to your Dashboard!

## 📝 Step 2: Upload Your Resume (2 minutes)

**This is important - it enables AI job matching!**

1. Click **"Profile"** in the left sidebar
2. Scroll to the **"Resume"** section
3. Choose one:
   - **Option A**: Click "Choose File" and upload your resume (PDF, TXT, DOC, DOCX)
   - **Option B**: Paste your resume text in the text area
4. Click **"Upload Resume"** or **"Update Resume"**
5. ✅ Your resume is now saved and parsed!

## 🔍 Step 3: Add Your First Job (Manual)

Let's add a job manually to test the system:

1. Go to Supabase Dashboard: https://supabase.com/dashboard/project/bbsombmpefldgjflwjsr
2. Click **"Table Editor"** → **"jobs"**
3. Click **"Insert row"**
4. Fill in (example):
   ```
   title: "Software Engineer"
   company: "Tech Company"
   url: "https://example.com/job"
   location: "San Francisco, CA"
   job_type: "full-time"
   remote_type: "hybrid"
   is_active: true (check the box)
   ```
5. Click **"Save"**
6. Go back to your app: http://localhost:3000/dashboard/jobs
7. ✅ You should see the job listed!

## 🎯 Step 4: Browse Jobs

1. Click **"Jobs"** in the sidebar
2. You'll see job listings with:
   - **Match scores** (if you uploaded resume)
   - Company, location, salary
   - Job type badges
3. Use filters:
   - Search by keyword or company
   - Filter by location
   - Filter by job type
4. Click **"View Details"** to see full job info

## 📊 Step 5: Track an Application

1. Click **"Applications"** in the sidebar
2. Click **"New Application"** button
3. You can manually track applications you've submitted
4. Update status as you progress:
   - Pending → Applied → Interview → Offer
5. Add notes, interview dates, follow-up reminders

## 🤖 Step 6: Auto-Apply Feature

**The automation magic!**

To use auto-apply:
1. Find a job posting URL (Greenhouse, Lever, Workday, etc.)
2. Make sure your profile is complete
3. In the future, you'll be able to click "Auto Apply" on any job
4. The system will:
   - Open the application form in a browser
   - Extract all form fields
   - Fill them with your information
   - Navigate multi-page forms
   - Let you review before submitting

## 📈 Your Dashboard

The dashboard shows:
- **Total Jobs**: Available in system
- **Applications**: Your submissions
- **Pending**: Applications in progress
- **Interviews**: Scheduled interviews
- **Top Matches**: Best jobs for your profile (based on AI)
- **Recent Applications**: Your latest submissions

## 🎨 Features Overview

### ✅ What Works Now:
- User authentication (sign up, login, logout)
- Profile management
- Resume upload and storage
- Job browsing with filters
- Manual application tracking
- Status updates
- Notes and reminders
- Dashboard statistics

### 🚀 What's Coming:
- Automated job scraping from multiple sources
- AI-powered job matching (with OpenAI)
- One-click auto-apply with form filling
- Email notifications
- Interview calendar sync
- Cover letter generation

## 🎯 Recommended Workflow

1. **Upload resume** (one time)
2. **Add jobs** you're interested in (manually or via scraper)
3. **Review matches** on dashboard
4. **Apply** to jobs (manually or auto)
5. **Track progress** in Applications page
6. **Update status** as you hear back
7. **Add interview dates** and notes
8. **Get hired!** 🎉

## 📚 Where to Go Next

- **Profile**: Update contact info, upload new resume
- **Jobs**: Browse and filter available positions
- **Applications**: Track your application pipeline
- **Settings**: Customize preferences

## 🆘 Need Help?

- Check the main README.md
- Review SETUP.md for configuration
- See ARCHITECTURE.md for technical details
- Open browser console (F12) for frontend errors
- Check terminal logs for backend errors

## 🎉 You're All Set!

Start tracking your applications and land your dream job! 🚀

---

**Your Platform URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/docs
- Supabase: https://supabase.com/dashboard/project/bbsombmpefldgjflwjsr
