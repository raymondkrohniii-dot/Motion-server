from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI(
    title="Motion Server",
    description="Server to generate simple motion video effects from images",
    version="1.1.0"
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

    # Apply Ken Burns effect with ffmpeg (slow zoom + pan)
    cmd = [
        "ffmpeg", "-y",
        "-i", in_path,
        "-vf", "zoompan=z='zoom+0.001':d=125,scale=1280:720",
        "-c:v", "libx264", "-t", "5", "-pix_fmt", "yuv420p",
        out_path
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        return {"error": f"ffmpeg failed: {e}"}

    return FileResponse(out_path, media_type="video/mp4", filename="animated.mp4")
