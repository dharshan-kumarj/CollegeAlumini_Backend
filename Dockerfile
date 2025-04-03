FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirement.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirement.txt

# Copy application code
COPY . .

# Create directory for media uploads
RUN mkdir -p app/media/alumni_profiles

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]