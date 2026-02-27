<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=24,30,35&height=170&section=header&text=JobAutomate&fontSize=52&fontAlignY=35&animation=twinkling&fontColor=ffffff&desc=Full-Stack%20AI%20Job%20Application%20Platform%20%7C%20Web%20UI%20%2B%20Automation&descAlignY=55&descSize=18" width="100%" />

[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](.)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](.)
[![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)](.)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](.)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](.)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](.)

**One-click job applications. AI matching. Full tracking dashboard.**

</div>

---

## Why This Exists

The [job-application-automator-mcp](https://github.com/ajay-automates/job-application-automator-mcp) handles the backend automation. This project wraps it in a beautiful web interface — so you can browse jobs, see match scores, auto-apply with one click, and track everything from a dashboard.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      JobAutomate Platform                       │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  Frontend     │    │  Backend     │    │  Database        │  │
│  │  Next.js 14   │←──→│  FastAPI     │←──→│  Supabase        │  │
│  │  + shadcn/ui  │    │  + OpenAI    │    │  + PostgreSQL    │  │
│  │  + Tailwind   │    │  + MCP       │    │  + RLS           │  │
│  └──────────────┘    └──────┬───────┘    └──────────────────┘  │
│                              │                                   │
│                     ┌────────▼────────┐                         │
│                     │  MCP Servers     │                         │
│                     │  ├─ Aggregator   │                         │
│                     │  ├─ Matcher      │                         │
│                     │  └─ Applicator   │                         │
│                     └─────────────────┘                         │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Features

| Feature | Description |
|---------|-------------|
| **Auto Form Filling** | AI extracts and fills job application forms via Playwright |
| **AI Job Matching** | 85%+ accuracy matching jobs to your resume with OpenAI |
| **Application Tracking** | Track applications, interviews, and offers in one place |
| **Job Discovery** | Browse thousands of jobs scraped from top companies |
| **Resume Parsing** | Upload resume, auto-extract skills and experience |
| **Secure Auth** | Supabase Auth with row-level security policies |
| **Modern Dashboard** | Real-time updates, responsive design, dark mode |

---

## Quick Start

```bash
git clone https://github.com/ajay-automates/AI-Job-Application.git
cd AI-Job-Application

# Frontend
cd frontend && npm install
cp .env.local.example .env.local  # Add Supabase credentials
npm run dev                        # http://localhost:3000

# Backend
cd ../backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env               # Add credentials
python -m app.main                  # http://localhost:8000
```

---

## Project Structure

```
AI-Job-Application/
├── frontend/                # Next.js 14 web application
│   ├── app/                 # App Router pages
│   ├── components/          # shadcn/ui components
│   └── lib/                 # Supabase client, utilities
├── backend/                 # FastAPI orchestration layer
│   ├── app/                 # API routes and services
│   └── requirements.txt
├── supabase/                # Database migrations
│   └── migrations/          # SQL schema + RLS policies
├── docs/                    # Additional documentation
├── Dockerfile               # Container deployment
└── README.md
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Next.js 14 App Router** | Server components + streaming for fast initial load |
| **FastAPI over Express** | Async Python integrates natively with MCP servers |
| **Supabase over Firebase** | PostgreSQL + RLS + real-time — all in one |
| **shadcn/ui components** | Accessible, customizable, no vendor lock-in |
| **Playwright stealth mode** | Bypass bot detection on job application sites |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/jobs` | List all discovered jobs |
| `POST` | `/api/applications` | Create new application |
| `POST` | `/api/automation/apply` | Auto-apply to a job |
| `GET` | `/api/profile/{id}` | Get user profile |

Full docs at `/api/docs` (Swagger) and `/api/redoc` when backend is running.

---

## Tech Stack

`Next.js 14` `React` `TypeScript` `Tailwind CSS` `shadcn/ui` `FastAPI` `Python` `Supabase` `PostgreSQL` `OpenAI` `Playwright` `Docker`

---

## Related Projects

| Project | Description |
|---------|-------------|
| [job-application-automator-mcp](https://github.com/ajay-automates/job-application-automator-mcp) | The MCP backend this platform builds on |
| [EazyApply](https://github.com/ajay-automates/eazyapply) | Chrome extension for one-click form filling |
| [Advanced Resume Analyzer](https://github.com/ajay-automates/advanced-resume-analyzer-qlora) | Fine-tuned Gemma 3 for resume analysis |

---

<div align="center">

**Built by [Ajay Kumar Reddy Nelavetla](https://github.com/ajay-automates)** · January 2026

*Apply smarter. Track everything. Land interviews.*

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=24,30,35&height=100&section=footer" width="100%" />

</div>
