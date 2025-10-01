from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI(
    title="Motion Server",
    description="Test server for simple animation generation",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Motion server running!"}

@app.post("/animate")
async def animate(file: UploadFile = File(...)):
    # Save uploaded image
    in_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    out_path = in_path + ".mp4"

    with open(in_path, "wb") as f:
        f.write(await file.read())

    # Use ffmpeg to create a 3s video (just loops the image for now)
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", in_path,
        "-c:v", "libx264", "-t", "3", "-pix_fmt", "yuv420p",
        out_path
    ]
    subprocess.run(cmd, check=True)

    return FileResponse(out_path, media_type="video/mp4", filename="animation.mp4")
