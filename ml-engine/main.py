"""FastAPI entrypoint for the ML engine."""

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO

import config
from analyzer.exceptions import AnalysisError, ValidationError
from analyzer.pipeline import SwingAnalysisPipeline

# ---------------------------------------------------------------------------
# Global model — loaded once at startup
# ---------------------------------------------------------------------------
MODEL_PATH = config.MODEL_PATH
model = YOLO(MODEL_PATH)
pipeline = SwingAnalysisPipeline(model)

config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Golf Swing Analyzer — ML Engine",
    description="Processes golf swing videos with YOLOv8-pose pose estimation.",
    version="0.2.0",
)

app.mount("/outputs", StaticFiles(directory=str(config.OUTPUT_DIR)), name="outputs")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/analyze-swing")
async def analyze_swing(
    video: UploadFile = File(...),
    club: str = Form("iron_7"),
    shot_type: str = Form("full_swing"),
):
    if not video.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    suffix = Path(video.filename).suffix or ".mp4"
    tmp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            prefix="temp_swing_", suffix=suffix, delete=False
        ) as tmp:
            tmp_path = tmp.name
            content = await video.read()
            tmp.write(content)

        result = pipeline.run(tmp_path, club=club, shot_type=shot_type)
        return pipeline.to_dict(result)

    except ValidationError as exc:
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "code": exc.code,
                "error": str(exc),
            },
        )
    except AnalysisError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
