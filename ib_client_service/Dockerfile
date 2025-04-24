# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# We use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container at /app/src
COPY ./src ./src

# Make port 5001 available to the world outside this container (for the MCP server)
EXPOSE 5001

# Define environment variable for the port (optional, but good practice)
ENV PORT=5001

# Run service.py when the container launches
# Using uvicorn for FastAPI/Starlette, or flask run for Flask
# Assuming FastAPI/uvicorn for now, adjust if using Flask
CMD ["uvicorn", "src.service:app", "--host", "0.0.0.0", "--port", "5001"]
