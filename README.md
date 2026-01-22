# JobAutomate - Complete Job Application Automation Platform

> AI-powered job application automation with web UI, automated form filling, and intelligent job matching.

## 🚀 Features

- **🤖 Automated Form Filling**: Automatically extract and fill job application forms using AI
- **🎯 AI Job Matching**: Match jobs to your resume with 85%+ accuracy using OpenAI
- **📊 Application Tracking**: Track all your applications, interviews, and offers in one place
- **🔍 Job Discovery**: Discover thousands of jobs from top companies automatically
- **📝 Resume Management**: Upload and manage your resume with automatic parsing
- **🔐 Secure Authentication**: Built on Supabase Auth with row-level security
- **📱 Modern UI**: Beautiful, responsive dashboard built with Next.js 14 and Tailwind CSS

## 📋 Architecture

This platform consists of three main components:

### 1. Frontend (Next.js 14)
- Modern React application with App Router
- Real-time updates with Supabase
- Responsive design with Tailwind CSS and shadcn/ui
- Server-side rendering and client components

### 2. Backend API (FastAPI)
- RESTful API for orchestration
- Integrates existing MCP servers
- Background task processing
- AI-powered job matching

### 3. Database (Supabase/PostgreSQL)
- Secure data storage with RLS
- Real-time subscriptions
- File storage for resumes
- Authentication and user management

### 4. MCP Servers (Existing)
- `job-application-automator`: Form filling with Playwright
- `job-board-aggregator`: Job scraping and aggregation
- `job-matcher`: AI-powered job matching

## 🛠️ Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Supabase Client
- React Query

**Backend:**
- FastAPI (Python)
- Supabase Python SDK
- OpenAI API
- Asyncio

**Database:**
- Supabase (PostgreSQL)
- Row Level Security (RLS)
- Realtime subscriptions

**Automation:**
- Playwright (browser automation)
- Undetected Playwright (stealth mode)
- OpenAI GPT-3.5/4 (AI matching)

## 📦 Installation

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Supabase account (free tier works)
- OpenAI API key

### 1. Clone the Repository

```bash
cd "/Users/ajaykumarreddy/Desktop/PROJECTS/Job Application MCP/job-automation-platform"
```

### 2. Setup Supabase

1. Go to [supabase.com](https://supabase.com) and create a project
2. Go to SQL Editor and run migrations in order:
   - `supabase/migrations/001_initial_schema.sql`
   - `supabase/migrations/002_row_level_security.sql`
3. Get your credentials from Settings > API:
   - Project URL
   - Anon/Public Key
   - Service Role Key (keep secret!)

### 3. Setup Frontend

```bash
cd frontend
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with your Supabase credentials

# Run development server
npm run dev
```

Frontend will be available at http://localhost:3000

### 4. Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run development server
python -m app.main
```

Backend API will be available at http://localhost:8000

### 5. Verify Existing MCP Servers

The existing MCP servers should already be set up. Verify they're working:

```bash
# From your MCP repo root
cd job-application-automator-mcp

# Start job-board-aggregator
cd job-board-aggregator
python run_server.py
# Should run on http://localhost:8080

# The job-application-automator and job-matcher 
# work through Claude Desktop and are integrated
```

## 🚀 Quick Start

1. **Sign up** at http://localhost:3000/signup
2. **Upload your resume** in Profile settings
3. **Browse jobs** in the Jobs page
4. **Apply automatically** with one click
5. **Track applications** in Applications page

## 📚 Documentation

- [Frontend Documentation](frontend/README.md)
- [Backend API Documentation](backend/README.md)
- [Supabase Setup](supabase/README.md)
- [MCP Integration](docs/MCP_INTEGRATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🔧 Configuration

### Frontend Environment Variables

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend Environment Variables

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
OPENAI_API_KEY=your-openai-key
JOB_AUTOMATOR_PATH=/path/to/job-application-automator-mcp
JOB_BOARD_AGGREGATOR_URL=http://localhost:8080
```

## 🎯 Usage

### Automated Application

1. Navigate to Jobs page
2. Click "View Details" on any job
3. Click "Auto Apply" button
4. The system will:
   - Extract form fields from the job page
   - Fill in your information automatically
   - Navigate through multi-page forms
   - Keep browser open for your review
   - Track application status

### Manual Application Tracking

1. Go to Applications page
2. Click "New Application"
3. Enter job details manually
4. Track status and add notes

### Job Matching

1. Upload your resume in Profile
2. System automatically calculates match scores
3. View top matches on Dashboard
4. Filter jobs by match score

## 🔐 Security

- **Authentication**: Supabase Auth with magic links and social login
- **Authorization**: Row Level Security (RLS) policies
- **Data Privacy**: Users can only access their own data
- **API Security**: Service role keys kept server-side only
- **HTTPS**: Required in production

## 🚢 Deployment

### Frontend (Vercel - Recommended)

```bash
cd frontend
npm run build

# Deploy to Vercel
vercel deploy --prod
```

### Backend (Railway/Render)

```bash
cd backend

# Build Docker image
docker build -t job-automate-api .

# Or deploy directly to Railway/Render
```

### Database (Supabase)

Your Supabase database is already hosted! Just update environment variables with production URLs.

## 📊 API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

Key endpoints:
- `GET /api/jobs` - List jobs
- `POST /api/applications` - Create application
- `POST /api/automation/apply` - Auto-apply to job
- `GET /api/profile/{user_id}` - Get user profile

## 🤝 Contributing

This is a personal project, but suggestions are welcome!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

MIT License - feel free to use for your own job search!

## 🆘 Troubleshooting

### Frontend won't start
- Check Node version: `node --version` (should be 18+)
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check `.env.local` has correct Supabase credentials

### Backend won't start
- Check Python version: `python --version` (should be 3.11+)
- Activate virtual environment: `source venv/bin/activate`
- Check `.env` has correct credentials
- Install dependencies: `pip install -r requirements.txt`

### Database errors
- Verify migrations ran successfully in Supabase SQL Editor
- Check RLS policies are enabled
- Ensure service role key is correct

### Form filling not working
- Verify `JOB_AUTOMATOR_PATH` in backend `.env`
- Check Playwright is installed: `python -m playwright install`
- Ensure job-application-automator is set up correctly

## 📧 Support

For issues, please check:
1. This README
2. Component-specific READMEs
3. Supabase documentation
4. Open an issue on GitHub

## 🙏 Acknowledgments

Built on top of:
- [job-application-automator-mcp](https://github.com/ajay-automates/job-application-automator-mcp)
- Next.js, React, FastAPI
- Supabase, OpenAI
- shadcn/ui components

---

**Made with ❤️ for job seekers everywhere**

Version: 1.0.0 | January 2026
