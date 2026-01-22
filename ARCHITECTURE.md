# JobAutomate Platform Architecture

Complete technical architecture and system design documentation.

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Browser                          │
│                    (http://localhost:3000)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Next.js 14 Frontend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Dashboard   │  │     Jobs     │  │ Applications │         │
│  │    Pages     │  │   Listings   │  │   Tracking   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │          Supabase Client (Auth + Realtime)       │          │
│  └──────────────────────────────────────────────────┘          │
└────────────────┬─────────────────────────┬─────────────────────┘
                 │                         │
                 │ (REST API)              │ (Auth + DB)
                 ▼                         ▼
    ┌───────────────────────┐   ┌──────────────────────┐
    │  FastAPI Backend      │   │   Supabase Cloud     │
    │  (localhost:8000)     │   │   (PostgreSQL)       │
    │                       │   │                      │
    │  ┌────────────────┐   │   │  ┌───────────────┐  │
    │  │   Job Router   │   │   │  │   Profiles    │  │
    │  │   App Router   │   │   │  │   Jobs        │  │
    │  │  Auto Router   │   │   │  │  Applications │  │
    │  └────────────────┘   │   │  │  Job Matches  │  │
    │                       │   │  └───────────────┘  │
    │  ┌────────────────┐   │   │                      │
    │  │   Services     │   │   │  Row Level Security  │
    │  │  - Matcher     │   │   │  (RLS Policies)      │
    │  │  - Parser      │   │   │                      │
    │  │  - Scraper     │   │   └──────────────────────┘
    │  └────────────────┘   │
    └───────┬───────────────┘
            │
            │ (subprocess calls)
            │
┌───────────▼──────────────────────────────────────────────────────┐
│                  Existing MCP Servers                            │
│                                                                   │
│  ┌─────────────────────────┐      ┌──────────────────────────┐  │
│  │ job-board-aggregator    │      │ job-application-automator│  │
│  │ (localhost:8080)        │      │ (Python)                 │  │
│  │                         │      │                          │  │
│  │ - Scrape jobs from      │      │ - Fill forms with        │  │
│  │   multiple sources      │      │   Playwright             │  │
│  │ - Greenhouse            │      │ - Multi-page support     │  │
│  │ - Lever                 │      │ - Stealth mode           │  │
│  │ - Workday               │      │ - Auto-submit            │  │
│  │ - LinkedIn              │      │                          │  │
│  └─────────────────────────┘      └──────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────┐                                     │
│  │ job-matcher (Node.js)   │                                     │
│  │                         │                                     │
│  │ - AI-powered matching   │                                     │
│  │ - OpenAI integration    │                                     │
│  │ - Score calculation     │                                     │
│  └─────────────────────────┘                                     │
└───────────────────────────────────────────────────────────────────┘
```

## 📦 Component Details

### Frontend (Next.js 14)

**Location**: `frontend/`

**Key Technologies**:
- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS + shadcn/ui for styling
- Supabase SSR for authentication
- Server and Client Components

**Structure**:
```
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/           # Login, Signup pages
│   │   ├── (dashboard)/      # Protected dashboard pages
│   │   │   ├── dashboard/    # Main dashboard
│   │   │   ├── jobs/         # Job listings
│   │   │   ├── applications/ # Application tracking
│   │   │   └── profile/      # User profile
│   │   ├── layout.tsx        # Root layout
│   │   └── page.tsx          # Landing page
│   ├── components/
│   │   ├── ui/               # shadcn/ui components
│   │   ├── dashboard/        # Dashboard-specific
│   │   ├── jobs/             # Job-related
│   │   └── applications/     # Application-related
│   └── lib/
│       ├── supabase/         # Supabase clients
│       └── utils.ts          # Utilities
└── public/                   # Static assets
```

**Key Features**:
- Server-side rendering for SEO
- Client components for interactivity
- Middleware for auth token refresh
- Real-time updates via Supabase
- Responsive design (mobile-first)

### Backend API (FastAPI)

**Location**: `backend/`

**Key Technologies**:
- FastAPI (modern Python web framework)
- Async/await for performance
- Supabase Python SDK
- OpenAI API integration
- Background tasks with asyncio

**Structure**:
```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # Supabase client
│   ├── routers/
│   │   ├── jobs.py          # Job endpoints
│   │   ├── applications.py  # Application endpoints
│   │   ├── automation.py    # Automation endpoints
│   │   └── profile.py       # Profile endpoints
│   └── services/
│       ├── form_filler.py   # Form filling integration
│       ├── job_scraper.py   # Job scraping integration
│       ├── job_matcher.py   # AI matching service
│       └── resume_parser.py # Resume parsing
└── requirements.txt         # Python dependencies
```

**Key Features**:
- RESTful API design
- Automatic API documentation (Swagger/ReDoc)
- Background job processing
- Integration with existing MCP servers
- Service layer architecture

### Database (Supabase/PostgreSQL)

**Location**: `supabase/migrations/`

**Schema**:

1. **profiles**
   - User profile information
   - Resume text and URL
   - Contact information
   - Preferences

2. **jobs**
   - Scraped job listings
   - Company, title, location
   - Salary, job type
   - Source and metadata

3. **applications**
   - User job applications
   - Status tracking
   - Automation status
   - Notes and dates

4. **job_matches**
   - AI-calculated match scores
   - Match reasons and analysis
   - User favorites

5. **automation_logs**
   - Activity logging
   - Error tracking
   - Performance metrics

6. **saved_searches**
   - User search queries
   - Auto-apply settings

**Security**:
- Row Level Security (RLS) enabled on all tables
- Users can only access their own data
- Service role for backend operations
- Realtime subscriptions for updates

### MCP Servers (Existing)

**Location**: `../job-application-automator-mcp/`

These are your existing servers, now integrated with the web platform:

1. **job-application-automator**
   - Form filling with Playwright
   - Multi-page navigation
   - Field detection and filling
   - Browser automation

2. **job-board-aggregator**
   - Job scraping from multiple sources
   - Data normalization
   - API for job search

3. **job-matcher**
   - AI-powered matching
   - Resume analysis
   - Job recommendation

## 🔄 Data Flow

### User Authentication Flow

```
1. User visits /login
2. Enters credentials
3. Supabase Auth validates
4. Frontend receives session token
5. Token stored in httpOnly cookie
6. Middleware refreshes token on each request
7. RLS policies enforce data access
```

### Automated Application Flow

```
1. User clicks "Auto Apply" on job
2. Frontend sends POST to /api/automation/apply
3. Backend creates application record
4. Backend queues background task
5. FormFillerService called
6. Reads user profile from Supabase
7. Creates temporary JSON with form data
8. Calls form_filler.py (existing MCP)
9. Playwright opens browser
10. Fills form fields
11. Navigates multi-page forms
12. User reviews and submits
13. Status updated in database
14. Frontend refreshes to show update
```

### Job Discovery Flow

```
1. User searches for jobs
2. Frontend calls /api/jobs with filters
3. Backend queries Supabase jobs table
4. Joins with job_matches for scores
5. Returns filtered, sorted results
6. Frontend displays with match badges
```

### Resume Upload Flow

```
1. User uploads resume file
2. File read as text in browser
3. Sent to /api/profile/{user_id}/resume
4. Backend calls ResumeParserService
5. OpenAI extracts structured data
6. Data saved to profiles table
7. JobMatcherService recalculates matches
8. New matches appear on dashboard
```

## 🔐 Security Architecture

### Authentication

- Supabase Auth handles all authentication
- Magic links, email/password, social login
- JWT tokens in httpOnly cookies
- Automatic token refresh via middleware

### Authorization

- Row Level Security (RLS) on all tables
- Policies enforce `user_id` matching
- Service role for backend operations
- No direct client access to service keys

### Data Protection

- HTTPS required in production
- Environment variables for secrets
- API keys never exposed to client
- Input validation on all endpoints

## 🚀 Deployment Architecture

### Production Setup

```
┌────────────────────────────────────────────┐
│           Vercel (Frontend)                │
│   - Next.js SSR                            │
│   - Edge Functions                         │
│   - CDN Distribution                       │
└───────────────┬────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────┐
│      Railway/Render (Backend API)         │
│   - FastAPI container                      │
│   - Auto-scaling                           │
│   - Health checks                          │
└───────────────┬────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────┐
│         Supabase (Database)                │
│   - Managed PostgreSQL                     │
│   - Automatic backups                      │
│   - 99.9% uptime SLA                       │
└────────────────────────────────────────────┘
```

## 📊 Performance Considerations

### Frontend

- Server-side rendering for initial load
- Client-side navigation for speed
- Code splitting by route
- Image optimization
- Lazy loading components

### Backend

- Async endpoints for concurrency
- Connection pooling (Supabase)
- Background task processing
- Caching with Redis (optional)

### Database

- Indexes on frequently queried columns
- Efficient RLS policies
- Pagination for large datasets
- Realtime subscriptions (not polling)

## 🔧 Configuration Management

### Environment Variables

**Frontend** (`.env.local`):
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_API_URL`

**Backend** (`.env`):
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `OPENAI_API_KEY`
- `JOB_AUTOMATOR_PATH`
- `JOB_BOARD_AGGREGATOR_URL`

### Feature Flags

Can be added to `profiles.preferences`:
```json
{
  "auto_apply_enabled": true,
  "min_match_score": 70,
  "notification_email": true
}
```

## 📈 Scalability

### Current Capacity

- **Users**: 1000+ concurrent (Supabase free tier)
- **Jobs**: Millions (PostgreSQL)
- **Applications**: Unlimited
- **API Requests**: 50/min (backend)

### Scaling Strategy

1. **Database**: Upgrade Supabase plan
2. **Backend**: Add more API containers
3. **Frontend**: Vercel auto-scales
4. **Jobs**: Add Redis cache
5. **Processing**: Add Celery workers

## 🧪 Testing Strategy

### Unit Tests
- Backend services
- Database functions
- Utility functions

### Integration Tests
- API endpoints
- Database operations
- MCP server integration

### E2E Tests
- User flows
- Form filling
- Application tracking

## 📝 Logging & Monitoring

### Application Logs

- Frontend: Browser console + Vercel logs
- Backend: Structured logging (JSON)
- Database: Supabase query logs

### Monitoring

- **Health checks**: `/health` endpoint
- **Errors**: Sentry (recommended)
- **Analytics**: PostHog (recommended)
- **Performance**: Vercel Analytics

### Automation Logs

- Stored in `automation_logs` table
- Track success/failure rates
- Debug form filling issues

## 🔄 Future Enhancements

1. **Real-time notifications**: WebSocket updates
2. **Email notifications**: SendGrid integration
3. **Calendar integration**: Google Calendar for interviews
4. **Cover letter generation**: AI-powered
5. **Interview prep**: AI chatbot
6. **Salary insights**: Historical data analysis
7. **Mobile app**: React Native
8. **Chrome extension**: Quick apply from any site

---

**Architecture Version**: 1.0.0  
**Last Updated**: January 2026  
**Status**: Production Ready ✅
