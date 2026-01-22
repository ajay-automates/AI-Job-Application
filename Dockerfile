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

# Set Python path so imports work correctly
ENV PYTHONPATH=/app:/app/backend

# Expose port
EXPOSE 8000

# Start the app
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
