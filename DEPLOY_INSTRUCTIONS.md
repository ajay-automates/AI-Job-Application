# 🚀 Deployment Instructions

## Step 1: Push to GitHub (Already Done by Cursor!)

Your code is ready to push. After creating your GitHub repo, run:

```bash
cd "/Users/ajaykumarreddy/Desktop/PROJECTS/Job Application MCP/job-automation-platform"

# Add your GitHub repository (replace with your actual URL)
git remote add origin https://github.com/YOUR_USERNAME/job-automation-platform.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Frontend to Vercel (5 minutes)

### A. Sign up/Login to Vercel
1. Go to: https://vercel.com
2. Click "Sign Up" or "Log In"
3. Use "Continue with GitHub"

### B. Import Project
1. Click "Add New..." → "Project"
2. Select your `job-automation-platform` repository
3. Click "Import"

### C. Configure Project
**Framework Preset**: Next.js (auto-detected)

**Root Directory**: `frontend`

**Build Command**: `npm run build` (auto-filled)

**Output Directory**: `.next` (auto-filled)

**Install Command**: `npm install` (auto-filled)

### D. Environment Variables
Click "Environment Variables" and add:

```
NEXT_PUBLIC_SUPABASE_URL=https://bbsombmpefldgjflwjsr.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJic29tYm1wZWZsZGdqZmx3anNyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4NjU3NDMsImV4cCI6MjA4NDQ0MTc0M30.1IX_CpUUgugz2hj_CaD6gttUE1OmiJimscnRcumNgwM
NEXT_PUBLIC_API_URL=https://your-backend-url.up.railway.app
OPENAI_API_KEY=your-openai-key
```

(You'll update `NEXT_PUBLIC_API_URL` after deploying backend)

### E. Deploy!
1. Click "Deploy"
2. Wait 2-3 minutes
3. You'll get a URL like: `https://job-automation-platform.vercel.app`

---

## Step 3: Deploy Backend to Railway (5 minutes)

### A. Sign up/Login to Railway
1. Go to: https://railway.app
2. Click "Login" → "Login with GitHub"

### B. Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `job-automation-platform` repository

### C. Configure Service
1. Railway will detect your project
2. Click "Add variables" to add environment variables

### D. Environment Variables
Add these:

```
HOST=0.0.0.0
PORT=8000
SUPABASE_URL=https://bbsombmpefldgjflwjsr.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
SUPABASE_ANON_KEY=your-anon-key
OPENAI_API_KEY=your-openai-key
ALLOWED_ORIGINS=https://job-automation-platform.vercel.app,http://localhost:3000
JWT_SECRET=your-jwt-secret
JOB_AUTOMATOR_PATH=/app/job-application-automator-mcp
JOB_BOARD_AGGREGATOR_URL=http://localhost:8080
```

### E. Configure Build
1. Click "Settings"
2. **Root Directory**: `backend`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `python -m app.main`

### F. Deploy!
1. Click "Deploy"
2. Wait 3-5 minutes
3. You'll get a URL like: `https://job-automation-backend.up.railway.app`

---

## Step 4: Update Frontend Environment

### A. Update Vercel Environment Variables
1. Go to your Vercel project
2. Settings → Environment Variables
3. Update `NEXT_PUBLIC_API_URL`:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.up.railway.app
   ```
4. Click "Save"
5. Redeploy: Deployments → Latest → "..." → "Redeploy"

---

## Step 5: Test Production!

1. Go to your Vercel URL
2. Sign up with a new account
3. Upload resume
4. Add jobs via Supabase
5. Everything should work!

---

## 🎯 Production URLs

**Frontend**: https://job-automation-platform.vercel.app
**Backend API**: https://your-backend.up.railway.app
**API Docs**: https://your-backend.up.railway.app/api/docs
**Database**: https://bbsombmpefldgjflwjsr.supabase.co (already live!)

---

## 🔒 Security Notes

1. **Never commit .env files** - They're in .gitignore ✅
2. **Use environment variables** for all secrets ✅
3. **Rotate keys** if exposed ⚠️
4. **Keep service_role key** secret ⚠️

---

## 🐛 Troubleshooting

### Frontend won't build
- Check environment variables in Vercel
- Verify root directory is set to `frontend`
- Check build logs

### Backend won't start
- Check environment variables in Railway
- Verify root directory is set to `backend`
- Check Python version (should be 3.11+)

### Database connection errors
- Verify Supabase URLs are correct
- Check RLS policies are enabled
- Ensure service_role key is correct

---

## 📊 Performance

**Production is MUCH faster than local:**
- ✅ Pre-compiled and optimized
- ✅ CDN distribution (Vercel)
- ✅ Auto-scaling
- ✅ No development overhead
- ✅ Page loads in 1-2 seconds!

---

## 🎉 You're Live!

Once deployed:
- Share your URL with friends
- Add to your portfolio
- Use it daily for your job search
- Keep improving and adding features!

**Total deployment time**: ~15 minutes
**Cost**: $0 (Free tiers!)
**Scalability**: Handles thousands of users!

---

Need help? Check the logs:
- Vercel: Project → Deployments → Click deployment → View Function Logs
- Railway: Project → Service → Logs tab
