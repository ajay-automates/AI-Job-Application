# 🚀 Quick Start - Job Automation

## Setup (One Time)

```bash
cd /Users/ajaykumarreddy/Desktop/PROJECTS/Job\ Application\ MCP/job-automation-platform
./setup-automation.sh
```

## Start All Services

### Terminal 1: Job Board Aggregator
```bash
cd ../job-application-automator-mcp/job-board-aggregator
python run_server.py
```

### Terminal 2: Backend
```bash
cd backend
source venv/bin/activate
python -m app.main
```

### Terminal 3: Frontend
```bash
cd frontend
npm run dev
```

## Test Features

### 1. Scrape Jobs (30 seconds)
1. Go to http://localhost:3000/dashboard/jobs
2. Click **"Scrape New Jobs"**
3. Enter: "Software Engineer"
4. Click **"Start Scraping"**
5. Wait, then refresh

### 2. AI Matching (1 minute)
1. Go to http://localhost:3000/dashboard/profile
2. Paste your resume
3. Click **"Save"**
4. See: "AI Matching Started! 🤖"
5. Go to Dashboard → See match scores!

### 3. Auto Apply (2 minutes)
1. Go to http://localhost:3000/dashboard/jobs
2. Find high match score job
3. Click **"Auto Apply"**
4. Confirm
5. Browser opens → Form fills!
6. Review and submit

## Production Deploy

### Railway
Add these env vars:
```bash
JOB_AUTOMATOR_PATH=/app/job-application-automator-mcp
JOB_BOARD_AGGREGATOR_URL=http://localhost:8080
API_AUTH_HASH=job-automate-secure-hash-2026
```

### Vercel
Already configured! Just push to GitHub.

## Troubleshooting

**"Failed to scrape"** → Check job-board-aggregator is running on port 8080

**"Resume required"** → Upload resume in Profile first

**"Script not found"** → Check `JOB_AUTOMATOR_PATH` in backend/.env

## 📖 Full Documentation

- `AUTOMATION_COMPLETE.md` - Complete guide
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `backend/ENVIRONMENT_SETUP.md` - Environment variables

---

**You're ready to automate your job search! 🎯**
