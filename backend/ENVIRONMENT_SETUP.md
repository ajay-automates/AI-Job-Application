# Backend Environment Variables Setup

Add these variables to your `backend/.env` file:

```bash
# Existing variables
HOST=0.0.0.0
PORT=8000
SUPABASE_URL=https://bbsombmpefldgjflwjsr.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
SUPABASE_ANON_KEY=your-anon-key
OPENAI_API_KEY=your-openai-key
ALLOWED_ORIGINS=https://ai-job-application-six.vercel.app,http://localhost:3000
JWT_SECRET=my-super-secret-jwt-key-production-2026

# NEW: MCP Server Integration (ADD THESE)
JOB_AUTOMATOR_PATH=/Users/ajaykumarreddy/Desktop/PROJECTS/Job Application MCP/job-application-automator-mcp
JOB_BOARD_AGGREGATOR_URL=http://localhost:8080
API_AUTH_HASH=job-automate-secure-hash-2026
```

## What These Do

- **JOB_AUTOMATOR_PATH**: Path to the form filler MCP server
- **JOB_BOARD_AGGREGATOR_URL**: URL where job-board-aggregator server runs
- **API_AUTH_HASH**: Authentication token for job-board-aggregator API
