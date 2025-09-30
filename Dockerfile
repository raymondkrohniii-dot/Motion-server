# Start from an image that already includes ffmpeg
FROM jrottenberg/ffmpeg:4.4-ubuntu AS ffmpeg

# Use slim Python as runtime
FROM python:3.9-slim

# Copy ffmpeg binary from the ffmpeg image
COPY --from=ffmpeg /usr/local/bin/ffmpeg /usr/local/bin/
COPY --from=ffmpeg /usr/local/bin/ffprobe /usr/local/bin/

# Set working dir
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "motion_server:app", "--host", "0.0.0.0", "--port", "8000"]
