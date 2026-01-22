# 🚀 Getting Started with JobAutomate

Welcome! This guide will get you up and running in **15 minutes**.

## ⚡ Quick Start (TL;DR)

```bash
# 1. Setup Supabase (5 min)
# - Go to supabase.com, create project
# - Run migrations from supabase/migrations/
# - Copy API credentials

# 2. Start Frontend (2 min)
cd frontend
npm install
# Edit .env.local with Supabase credentials
npm run dev
# → http://localhost:3000

# 3. Start Backend (2 min)
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Edit .env with credentials
python -m app.main
# → http://localhost:8000

# 4. Start Aggregator (1 min)
cd ../job-application-automator-mcp/job-board-aggregator
python run_server.py
# → http://localhost:8080

# Done! 🎉
```

## 📋 What You're Building

A complete job automation platform with:

- ✅ **Beautiful Web UI** - Track jobs and applications
- ✅ **AI Job Matching** - Smart recommendations based on your resume
- ✅ **Automated Form Filling** - Apply with one click
- ✅ **Application Tracking** - Never lose track of where you applied
- ✅ **Resume Management** - Upload and parse your resume
- ✅ **Secure & Private** - Your data is yours

## 🎯 Prerequisites

You need:

1. **Supabase account** (free) - [Sign up](https://supabase.com)
2. **OpenAI API key** - [Get one](https://platform.openai.com) (~$5 credit works)
3. **Node.js 18+** - [Download](https://nodejs.org)
4. **Python 3.11+** - [Download](https://python.org)

Check you have them:
```bash
node --version  # Should show v18 or higher
python3 --version  # Should show 3.11 or higher
```

## 📖 Step-by-Step Guide

### Step 1: Supabase Setup (5 minutes)

1. **Create Project**
   - Go to [supabase.com/dashboard](https://supabase.com/dashboard)
   - Click "New Project"
   - Name: `JobAutomate`
   - Choose a password and region
   - Wait 2 minutes for setup

2. **Run Migrations**
   - Click **SQL Editor** in left sidebar
   - Click **New Query**
   - Open `supabase/migrations/001_initial_schema.sql`
   - Copy entire content
   - Paste into SQL Editor
   - Click **Run** (green button)
   - Should see "Success. No rows returned"
   - Repeat for `002_row_level_security.sql`

3. **Get Credentials**
   - Click **Settings** → **API** in sidebar
   - You'll need these 3 values:
     * **Project URL**: `https://xxxxx.supabase.co`
     * **anon public**: `eyJhbGc...` (long string)
     * **service_role**: `eyJhbGc...` (different long string)
   - Keep this tab open, you'll need these soon!

### Step 2: Frontend Setup (5 minutes)

```bash
# Navigate to frontend
cd job-automation-platform/frontend

# Install dependencies (takes 2-3 minutes)
npm install

# Create environment file
cp .env.local.example .env.local

# Edit with your favorite editor
nano .env.local
```

**Edit `.env.local`** - Replace with your actual values:
```env
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR_ANON_KEY_HERE
NEXT_PUBLIC_API_URL=http://localhost:8000
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY
```

Save and close (`Ctrl+X`, then `Y`, then `Enter` if using nano)

```bash
# Start development server
npm run dev
```

You should see:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  
✓ Ready in 2.5s
```

**🎉 Frontend is running!** Open http://localhost:3000

### Step 3: Backend Setup (5 minutes)

Open a **new terminal window**:

```bash
# Navigate to backend
cd job-automation-platform/backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
# On Windows: venv\Scripts\activate

# Install dependencies (takes 1-2 minutes)
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit it
nano .env
```

**Edit `.env`** - Replace with your values:
```env
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_KEY=YOUR_SERVICE_ROLE_KEY
SUPABASE_ANON_KEY=YOUR_ANON_KEY
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY
JOB_AUTOMATOR_PATH=/Users/ajaykumarreddy/Desktop/PROJECTS/Job Application MCP/job-application-automator-mcp
```

Save and close.

```bash
# Start server
python -m app.main
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**🎉 Backend is running!** API docs at http://localhost:8000/api/docs

### Step 4: Job Aggregator (Already set up!)

Open a **third terminal window**:

```bash
# Navigate to aggregator
cd job-application-automator-mcp/job-board-aggregator

# Start server
python run_server.py
```

You should see:
```
Server running on http://localhost:8080
```

**🎉 All systems running!**

## ✨ First Steps

### 1. Create Your Account

1. Go to http://localhost:3000
2. Click **"Sign Up"**
3. Enter your email and password
4. Click **"Create Account"**
5. You'll be redirected to the dashboard!

### 2. Upload Your Resume

1. Click **"Profile"** in the sidebar
2. Scroll to **"Resume"** section
3. Either:
   - Upload a file (PDF, TXT, DOC)
   - Or paste your resume text
4. Click **"Upload Resume"**
5. ✅ Your resume is now parsed and stored!

### 3. Browse Jobs

1. Click **"Jobs"** in the sidebar
2. You'll see job listings (if any exist)
3. Use filters to search by:
   - Keywords (job title, company)
   - Location
   - Job type

### 4. Create an Application

1. Click **"Applications"** in the sidebar
2. Click **"New Application"**
3. Fill in job details
4. Click **"Create"**
5. Track status in the list!

### 5. Auto-Apply (The Magic! ✨)

1. Find a job you like
2. Click **"Auto Apply"**
3. System will:
   - Extract form fields from the job page
   - Fill them with your info
   - Navigate multi-page forms
   - Keep browser open for review
4. Review and submit!

## 🎓 Learn More

- **Full Documentation**: See [README.md](README.md)
- **Setup Details**: See [SETUP.md](SETUP.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Troubleshooting**: Check terminal logs

## 🐛 Common Issues & Fixes

### "Cannot connect to Supabase"
```bash
# Check your .env files have correct URLs
# Make sure Supabase project is active (not paused)
```

### "Port already in use"
```bash
# Kill the process on that port
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:8000 | xargs kill -9  # Backend
```

### "Module not found"
```bash
# Reinstall dependencies
cd frontend && rm -rf node_modules && npm install
cd backend && pip install -r requirements.txt
```

### "OpenAI API error"
```bash
# Check your API key starts with 'sk-'
# Verify you have credits at platform.openai.com
# Make sure key is in .env files
```

## 🚀 Next Steps

Now that you're set up:

1. **Customize**: Change colors, logos, branding
2. **Add Jobs**: Use scraper or add manually
3. **Set Preferences**: Configure auto-apply settings
4. **Track Progress**: Monitor your applications
5. **Deploy**: Deploy to production (see [DEPLOYMENT.md](docs/DEPLOYMENT.md))

## 💡 Pro Tips

- **Use tmux**: Run `./start-dev.sh` to start all services in one command
- **Enable notifications**: Set up email alerts for new matches
- **Batch apply**: Select multiple jobs and auto-apply to all
- **Interview tracking**: Add interview dates to get calendar reminders
- **Notes**: Add notes to applications to remember details

## 📧 Need Help?

- **Check logs**: Look at terminal output for errors
- **Inspect browser**: Open DevTools (F12) for frontend errors
- **API docs**: Visit http://localhost:8000/api/docs
- **Supabase logs**: Check logs in Supabase dashboard

## 🎉 You're Ready!

Start automating your job search and land your dream job faster!

---

**Happy Job Hunting! 🚀**

Made with ❤️ for job seekers everywhere
