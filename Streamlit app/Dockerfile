# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies required for building some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    libgomp1 \
 && rm -rf /var/lib/apt/lists/*

# THIS IS SPECIFIC TO HUGGINFACE
# We create a new user named "user" with ID of 1000
RUN useradd -m -u 1000 user

# Ensure stdout and stderr are sent straight to the terminal (useful for logging)
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# Start both uvicorn (FastAPI) and Streamlit concurrently.
CMD uvicorn app:app --port 8000 & streamlit run streamlit_app.py --server.port 8501