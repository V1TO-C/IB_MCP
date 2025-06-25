FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install curl and pip dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add entrypoint script
COPY entrypoint.sh .
COPY validator.py .
RUN chmod +x entrypoint.sh

# Make sure the routers output dir exists
RUN mkdir -p /app/routers

# Entrypoint
ENTRYPOINT ["bash", "entrypoint.sh"]

