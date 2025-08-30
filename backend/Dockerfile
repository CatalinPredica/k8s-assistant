# Use a Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install kubectl - we need to download and install the kubectl binary
# from the official Kubernetes release page.
# Using a specific version (e.g., v1.28.2) is a good practice to ensure compatibility.
# For simplicity, we'll get the latest version and make it executable.
# The `wget` command might not be available in the slim image, so we install `curl` or `wget` first.
RUN apt-get update && apt-get install -y curl && \
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
    rm kubectl && \
    apt-get purge -y --auto-remove curl && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code
COPY . .

# Expose the port the FastAPI application runs on
EXPOSE 8000

# Set the environment variable for the Gemini API key
ENV GEMINI_API_KEY=""

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
