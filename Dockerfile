FROM python:3.9-FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Start the server
CMD ["uvicorn", "motion_server:app", "--host", "0.0.0.0", "--port", "8000"]
