FROM python:3.9-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set working dir
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port (optional for clarity)
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "motion_server:app", "--host", "0.0.0.0", "--port", "8000"]
