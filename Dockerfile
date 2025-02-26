# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Ensure SQLite DB directory exists
RUN mkdir -p /data

# Expose port
EXPOSE 8080

# Run the app
CMD ["python", "app.py"]