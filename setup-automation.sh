#!/bin/bash

# Job Automation Platform - Setup Script
# This script helps configure the automation features

echo "🚀 Job Automation Platform - Setup"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if backend .env exists
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}❌ backend/.env not found!${NC}"
    echo "Please create backend/.env first with your Supabase credentials"
    exit 1
fi

echo -e "${YELLOW}📝 Checking backend environment variables...${NC}"

# Check if automation vars exist
if grep -q "JOB_AUTOMATOR_PATH" backend/.env; then
    echo -e "${GREEN}✅ JOB_AUTOMATOR_PATH already configured${NC}"
else
    echo -e "${YELLOW}⚠️  Adding JOB_AUTOMATOR_PATH to backend/.env${NC}"
    echo "" >> backend/.env
    echo "# MCP Server Integration" >> backend/.env
    echo "JOB_AUTOMATOR_PATH=/Users/ajaykumarreddy/Desktop/PROJECTS/Job Application MCP/job-application-automator-mcp" >> backend/.env
    echo "JOB_BOARD_AGGREGATOR_URL=http://localhost:8080" >> backend/.env
    echo "API_AUTH_HASH=job-automate-secure-hash-2026" >> backend/.env
    echo -e "${GREEN}✅ Added automation environment variables${NC}"
fi

# Check job-board-aggregator .env
echo ""
echo -e "${YELLOW}📝 Checking job-board-aggregator environment...${NC}"

JOB_BOARD_ENV="../job-application-automator-mcp/job-board-aggregator/.env"

if [ ! -f "$JOB_BOARD_ENV" ]; then
    echo -e "${YELLOW}⚠️  job-board-aggregator/.env not found, creating...${NC}"
    touch "$JOB_BOARD_ENV"
fi

if grep -q "API_AUTH_HASH" "$JOB_BOARD_ENV"; then
    echo -e "${GREEN}✅ API_AUTH_HASH already configured${NC}"
else
    echo -e "${YELLOW}⚠️  Adding API_AUTH_HASH to job-board-aggregator/.env${NC}"
    echo "API_AUTH_HASH=job-automate-secure-hash-2026" >> "$JOB_BOARD_ENV"
    echo -e "${GREEN}✅ Added API_AUTH_HASH${NC}"
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Start job-board-aggregator:"
echo "   cd ../job-application-automator-mcp/job-board-aggregator && python run_server.py"
echo ""
echo "2. Start backend (in new terminal):"
echo "   cd backend && source venv/bin/activate && python -m app.main"
echo ""
echo "3. Start frontend (in new terminal):"
echo "   cd frontend && npm run dev"
echo ""
echo "4. Open http://localhost:3000 and test!"
echo ""
echo "📖 See AUTOMATION_COMPLETE.md for full testing guide"
