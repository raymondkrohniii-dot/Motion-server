from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import subprocess
import os
import uuid

app = FastAPI(
    title="Motion Server",
    version="1.0.0",
    description="Test server for simple animation generation"
)

# Root endpoint (so you see something at /)
@app.get("/")
def read_root():
    return {"message": "Motion server running!"}

# Animate endpoint
@app.post("/animate")
async def animate(file: UploadFile = File(...)):
    try:
        # Generate unique names to avoid clashes
        file_id = uuid.uuid4().hex
        input_path = f"input_{file_id}_{file.filename}"
        output_path = f"animated_{file_id}.mp4"

        # Save uploaded file
        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())

        # Run ffmpeg and capture stdout/stderr
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-vf", "scale=320:240", output_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            # Log ffmpeg error to Railway logs
            print("FFmpeg error output:", result.stderr)
            raise HTTPException(status_code=500, detail=f"FFmpeg failed: {result.stderr}")

        # Return the processed video file for download
        return FileResponse(output_path, media_type="video/mp4", filename=output_path)

    except Exception as e:
        print("Animation server error:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Cleanup input (keep output so user can download)
        if os.path.exists(input_path):
            os.remove(input_path)
