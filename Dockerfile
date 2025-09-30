FROM jrottenberg/ffmpeg:4.4-ubuntu as ffmpeg

FROM python:3.9-slim

# Copy ffmpeg binary from stage 1
COPY --from=ffmpeg /usr/local/bin/ffmpeg /usr/local/bin/

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "motion_server:app", "--host", "0.0.0.0", "--port", "8000"]
