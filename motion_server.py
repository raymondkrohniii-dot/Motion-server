from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import subprocess
import os
import uuid
import imghdr

app = FastAPI(
    title="Motion Server",
    version="1.0.0",
    description="Test server for simple animation generation"
)

@app.get("/")
def root():
    return {"message": "Motion server running!"}

@app.post("/animate")
async def animate(file: UploadFile = File(...)):
    try:
        file_id = uuid.uuid4().hex
        input_path = f"input_{file_id}_{file.filename}"
        output_path = f"animated_{file_id}.mp4"

        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())

        # Check if it's an image or video
        is_image = imghdr.what(input_path) is not None

        if is_image:
            # Turn image into 3s video loop
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", input_path,
                "-t", "3", "-vf", "scale=320:240", output_path
            ]
        else:
            # Process video
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", "scale=320:240", output_path
            ]

        result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print("FFmpeg error:", result.stderr)
            raise HTTPException(status_code=500, detail="FFmpeg failed. Check logs.")

        return FileResponse(output_path, media_type="video/mp4", filename="animated.mp4")

    except Exception as e:
        print("Server error:", e)
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
