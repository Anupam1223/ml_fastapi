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

# Run database migrations before starting the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
