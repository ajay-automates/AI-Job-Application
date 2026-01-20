# Setup Guide - JobAutomate Platform

Complete step-by-step guide to get JobAutomate running on your machine.

## 📋 Prerequisites Checklist

Before you begin, make sure you have:

- [ ] **Node.js 18+** - [Download](https://nodejs.org/)
- [ ] **Python 3.11+** - [Download](https://python.org/)
- [ ] **npm or yarn** - Comes with Node.js
- [ ] **Supabase account** - [Sign up free](https://supabase.com/)
- [ ] **OpenAI API key** - [Get one here](https://platform.openai.com/)
- [ ] **Git** - For cloning repositories

## 🎯 Step 1: Supabase Setup (10 minutes)

### 1.1 Create Supabase Project

1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Fill in:
   - **Name**: JobAutomate
   - **Database Password**: (save this!)
   - **Region**: Choose closest to you
4. Click "Create new project"
5. Wait 2-3 minutes for provisioning

### 1.2 Run Database Migrations

1. In your Supabase project, click **SQL Editor** in sidebar
2. Click **New Query**
3. Copy entire content of `supabase/migrations/001_initial_schema.sql`
4. Paste and click **Run**
5. Should see "Success. No rows returned"
6. Repeat for `supabase/migrations/002_row_level_security.sql`

### 1.3 Get API Credentials

1. Go to **Settings** > **API** in sidebar
2. Copy these values (you'll need them later):
   ```
   Project URL: https://xxxxxxxxxxxxx.supabase.co
   anon public key: eyJhbGc...
   service_role key: eyJhbGc... (⚠️ Keep secret!)
   ```

## 🎨 Step 2: Frontend Setup (5 minutes)

```bash
# Navigate to frontend directory
cd job-automation-platform/frontend

# Install dependencies
npm install

# Create environment file
cat > .env.local << 'EOF'
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
OPENAI_API_KEY=your_openai_key_here
EOF

# Edit .env.local with your actual values
nano .env.local  # or use your preferred editor

# Start development server
npm run dev
```

Frontend should now be running at **http://localhost:3000** 🎉

## 🔧 Step 3: Backend API Setup (5 minutes)

```bash
# Navigate to backend directory
cd ../backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cat > .env << 'EOF'
HOST=0.0.0.0
PORT=8000

SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_KEY=your_service_key_here
SUPABASE_ANON_KEY=your_anon_key_here

OPENAI_API_KEY=your_openai_key_here

REDIS_URL=redis://localhost:6379

JOB_AUTOMATOR_PATH=/Users/ajaykumarreddy/Desktop/PROJECTS/Job Application MCP/job-application-automator-mcp
JOB_BOARD_AGGREGATOR_URL=http://localhost:8080

ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

JWT_SECRET=change-this-to-a-secure-random-string
EOF

# Edit .env with your actual values
nano .env

# Start development server
python -m app.main
```

Backend API should now be running at **http://localhost:8000** 🎉

## 🤖 Step 4: MCP Servers Setup (Already Done!)

Your existing MCP servers should already be configured. Let's verify:

```bash
# Start job-board-aggregator (keep this running in a terminal)
cd ../job-application-automator-mcp/job-board-aggregator
python run_server.py
```

Should see: `Server running on http://localhost:8080`

The form filler (`job-application-automator`) is integrated and will be called by the backend API when needed.

## ✅ Step 5: Verification

### 5.1 Test Frontend

1. Open http://localhost:3000
2. Should see landing page with "JobAutomate" branding
3. Click "Sign Up"
4. Create account with email/password
5. Should redirect to dashboard

### 5.2 Test Backend API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return: {"status":"healthy"}

# View API docs
open http://localhost:8000/api/docs
```

### 5.3 Test Database

1. In Supabase Dashboard, go to **Table Editor**
2. Should see tables: profiles, jobs, applications, job_matches, etc.
3. Click **profiles** - should see your user profile

### 5.4 Test Complete Flow

1. **Upload Resume**:
   - Go to http://localhost:3000/dashboard/profile
   - Upload your resume or paste resume text
   - Click "Upload Resume"
   - Should see success message

2. **Browse Jobs** (if any exist):
   - Go to http://localhost:3000/dashboard/jobs
   - Should see job listings (may be empty initially)

3. **Create Application**:
   - Go to http://localhost:3000/dashboard/applications
   - Click "New Application"
   - Fill in details
   - Should appear in list

## 🎉 Success!

You now have a fully functional job automation platform!

## 🔄 Daily Usage

### Start All Services

```bash
# Terminal 1 - Frontend
cd frontend
npm run dev

# Terminal 2 - Backend
cd backend
source venv/bin/activate
python -m app.main

# Terminal 3 - Job Aggregator
cd job-application-automator-mcp/job-board-aggregator
python run_server.py
```

### Stop All Services

Press `Ctrl+C` in each terminal

## 🐛 Common Issues

### "Module not found" errors

```bash
# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install

# Backend
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

### "Connection refused" to Supabase

- Check `.env` files have correct SUPABASE_URL
- Verify project is not paused (free tier pauses after inactivity)
- Check internet connection

### "OpenAI API error"

- Verify API key is correct and active
- Check you have credits: https://platform.openai.com/usage
- Ensure key starts with `sk-`

### "Port already in use"

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

## 📚 Next Steps

1. **Customize**: Modify UI colors, branding in `frontend/src`
2. **Add Jobs**: Use job scraper or manually add jobs
3. **Configure Automation**: Set up auto-apply preferences
4. **Deploy**: See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment

## 🆘 Still Stuck?

1. Check main [README.md](README.md)
2. Review [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
3. Check Supabase logs in Dashboard
4. Review browser console for frontend errors
5. Check backend terminal for API errors

---

**Happy Job Hunting! 🚀**
