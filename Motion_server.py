import cv2, numpy as np, json, os, uuid, subprocess
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse

app = FastAPI(title="Motion Server", description="Animate a still image using a simple motion plan", version="0.1.0")

@app.post("/animate")
async def animate(
    file: UploadFile = File(..., description="Base image to animate (PNG/JPG)"),
    motion_plan: str = Form(..., description="JSON string with motion instructions"),
    fps: int = Form(24),
    duration: int = Form(5),
    width: int = Form(512),
    height: int = Form(512)
):
    try:
        # Load base image
        data = await file.read()
        npimg = np.frombuffer(data, np.uint8)
        base_img = cv2.imdecode(npimg, cv2.IMREAD_UNCHANGED)
        if base_img is None:
            raise HTTPException(status_code=400, detail="Could not decode image")
        base_img = cv2.resize(base_img, (width, height))

        # Parse motion plan JSON
        plan = json.loads(motion_plan)
        motions = plan.get("motions", [])

        total_frames = int(fps * duration)
        workdir = f"/tmp/motion_{uuid.uuid4().hex}"
        os.makedirs(workdir, exist_ok=True)

        for f in range(total_frames):
            frame = base_img.copy()

            for m in motions:
                dx = float(m.get("dx", 0))
                dy = float(m.get("dy", 0))
                cycle = int(m.get("cycle", 0))
                speed = float(m.get("speed", 1))

                # oscillating cycle (sinusoidal) or linear drift
                offset_x = int(dx * np.sin(2 * np.pi * f / max(1, cycle))) if cycle else int(dx * f * speed / fps)
                offset_y = int(dy * np.sin(2 * np.pi * f / max(1, cycle))) if cycle else int(dy * f * speed / fps)

                # apply affine transform
                M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
                shifted = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))
                frame = cv2.addWeighted(frame, 0.5, shifted, 0.5, 0)

            cv2.imwrite(os.path.join(workdir, f"frame_{f:04d}.png"), frame)

        # Assemble frames into MP4
        output = os.path.join(workdir, "output.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", os.path.join(workdir, "frame_%04d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            output
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        return FileResponse(output, media_type="video/mp4", filename="animated.mp4")

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="motion_plan must be valid JSON")
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"ffmpeg failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
