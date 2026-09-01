"""
ML Engine — Golf Swing Analyzer
FastAPI service that processes uploaded swing videos using YOLOv8-pose and OpenCV.
"""

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from ultralytics import YOLO

# ---------------------------------------------------------------------------
# Global model initialization — loaded once at startup to avoid per-request cost
# ---------------------------------------------------------------------------
MODEL_PATH = "yolov8n-pose.pt"
model = YOLO(MODEL_PATH)

app = FastAPI(
    title="Golf Swing Analyzer — ML Engine",
    description="Processes golf swing videos and returns pose-based analysis.",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    """Liveness probe for orchestration and load balancers."""
    return {"status": "ok"}


@app.post("/analyze-swing")
async def analyze_swing(video: UploadFile = File(...)):
    """
    Accept a video upload, run pose estimation, and return swing analysis.

    Request:
        multipart/form-data with a single 'video' field.

    Response:
        JSON with status, score, and recommendation.
    """
    if not video.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Persist upload to a temporary file so OpenCV / YOLO can read from disk
    suffix = Path(video.filename).suffix or ".mp4"
    tmp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            prefix="temp_swing_", suffix=suffix, delete=False
        ) as tmp:
            tmp_path = tmp.name
            content = await video.read()
            tmp.write(content)

        # -------------------------------------------------------------------
        # TODO: Insert YOLOv8-pose + OpenCV processing logic here.
        #
        # Example workflow:
        #   1. cap = cv2.VideoCapture(tmp_path)
        #   2. Loop frames, run model(frame) for pose keypoints
        #   3. Compute swing metrics (hip rotation, club path, tempo, etc.)
        #   4. Derive score and recommendation from metrics
        # -------------------------------------------------------------------
        _ = model  # reference model so linters don't flag it as unused

        return {
            "status": "success",
            "score": 85,
            "recommendation": "Mock recommendation",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Analysis failed: {exc}"
        ) from exc

    finally:
        # Always remove the temporary file to prevent disk leaks
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
