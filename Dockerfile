# Build stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy entire project
COPY . .

# Install backend dependencies
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (needed for automation)
RUN python -m playwright install chromium

# Expose port
EXPOSE 8000

# Set working directory for running the app
WORKDIR /app/backend

# Start the app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
