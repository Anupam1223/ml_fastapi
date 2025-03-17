# Use the latest stable Python image
FROM python:3.10

# Set working directory inside the container
WORKDIR /app

# Copy only requirements first (leveraging Docker caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose application port
EXPOSE 8000

# Set environment variables for database connection
ENV DATABASE_URL=postgresql://postgres:anupam@ml_db:5432/ml_fastapi

# Run database migrations before starting the server
CMD alembic upgrade head && uvicorn app.main:app --reload
