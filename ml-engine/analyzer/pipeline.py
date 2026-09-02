"""Analysis pipeline orchestration."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from ultralytics import YOLO

import config
from analyzer.exceptions import ProcessingError, ValidationError
from analyzer.metrics.compute import compute_all_metrics
from analyzer.overlay import render_annotated_video
from analyzer.pose import FramePose, PoseExtractor
from analyzer.scoring import score_swing
from analyzer.swing_trim import TrimWindow, scout_trim_window
from analyzer.tuning.loader import resolve_profile
from analyzer.tuning.schema import TuningProfile
from analyzer.validator import validate_video
from analyzer.video_io import VideoMeta, iter_frames, read_video_meta


class StageId(str, Enum):
    VALIDATE = "validate"
    QUALITY_CHECK = "quality_check"
    LOCATE_SWING = "locate_swing"
    EXTRACT_POSE = "extract_pose"
    COMPUTE_METRICS = "compute_metrics"
    RENDER_VIDEO = "render_video"
    SCORE = "score"


STAGE_LABELS: dict[StageId, str] = {
    StageId.VALIDATE: "Memvalidasi video",
    StageId.QUALITY_CHECK: "Memeriksa kualitas & sudut kamera",
    StageId.LOCATE_SWING: "Mencari segmen swing",
    StageId.EXTRACT_POSE: "Mengekstrak pose per frame",
    StageId.COMPUTE_METRICS: "Menghitung metrik sendi",
    StageId.RENDER_VIDEO: "Membuat video analisis",
    StageId.SCORE: "Menghitung skor & rekomendasi",
}


@dataclass
class StageResult:
    id: str
    label: str
    status: str  # completed | failed
    duration_ms: int
    message: str = ""


@dataclass
class AnalysisResult:
    status: str
    score: int
    recommendation: str
    metrics: dict[str, Any]
    validation: dict[str, Any]
    tuning: dict[str, Any]
    trim: dict[str, Any]
    stages: list[StageResult] = field(default_factory=list)
    annotated_video_url: str = ""
    analysis_id: str = ""


StageCallback = Callable[[StageId, str], None]


class SwingAnalysisPipeline:
    def __init__(self, model: YOLO):
        self._pose = PoseExtractor(model)
        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        video_path: str,
        club: str = "iron_7",
        shot_type: str = "full_swing",
        on_stage: StageCallback | None = None,
    ) -> AnalysisResult:
        profile = resolve_profile(shot_type=shot_type, club=club)
        analysis_id = uuid.uuid4().hex[:12]
        stages: list[StageResult] = []

        def run_stage(stage_id: StageId, fn) -> Any:
            label = STAGE_LABELS[stage_id]
            if on_stage:
                on_stage(stage_id, label)
            start = time.perf_counter()
            try:
                result = fn()
                duration = int((time.perf_counter() - start) * 1000)
                stages.append(StageResult(
                    id=stage_id.value,
                    label=label,
                    status="completed",
                    duration_ms=duration,
                ))
                return result
            except ValidationError:
                raise
            except Exception as exc:
                duration = int((time.perf_counter() - start) * 1000)
                stages.append(StageResult(
                    id=stage_id.value,
                    label=label,
                    status="failed",
                    duration_ms=duration,
                    message=str(exc),
                ))
                raise ProcessingError(f"Gagal pada tahap {label}: {exc}") from exc

        meta = run_stage(StageId.VALIDATE, lambda: read_video_meta(video_path))

        validation = run_stage(
            StageId.QUALITY_CHECK,
            lambda: validate_video(video_path, meta, self._pose, profile.validation),
        )

        trim: TrimWindow = run_stage(
            StageId.LOCATE_SWING,
            lambda: scout_trim_window(video_path, meta, self._pose),
        )

        poses: list[FramePose | None] = run_stage(
            StageId.EXTRACT_POSE,
            lambda: self._extract_poses_range(
                video_path,
                trim.source_start_frame,
                trim.source_end_frame,
            ),
        )

        valid_poses = [p for p in poses if p is not None]
        if len(valid_poses) < config.MIN_FRAME_COUNT // 2:
            raise ValidationError(
                "Pose tidak cukup terdeteksi pada segmen swing. Coba rekam ulang dengan pencahayaan lebih baik.",
                code="insufficient_pose_data",
            )

        metrics = run_stage(
            StageId.COMPUTE_METRICS,
            lambda: compute_all_metrics(valid_poses, profile),
        )

        # Attach source-frame phase markers for verification (relative to original upload)
        if metrics.get("biomechanics"):
            metrics["biomechanics"]["address_frame_source"] = trim.address_frame_source
            metrics["biomechanics"]["top_frame_source"] = trim.top_frame_source
            metrics["biomechanics"]["impact_frame_source"] = trim.impact_frame_source
            metrics["biomechanics"]["trim_start_frame_source"] = trim.source_start_frame

        output_filename = f"{analysis_id}.mp4"
        output_path = str(config.OUTPUT_DIR / output_filename)

        run_stage(
            StageId.RENDER_VIDEO,
            lambda: render_annotated_video(
                video_path,
                output_path,
                poses,
                meta.width,
                meta.height,
                meta.fps,
                start_frame=trim.source_start_frame,
                end_frame=trim.source_end_frame,
            ),
        )

        score_data = run_stage(StageId.SCORE, lambda: score_swing(metrics, profile))
        metrics["summary"] = score_data["summary"]

        trim_dict = trim.to_dict()
        if meta.fps > 0:
            trim_dict["address_frame_in_trim"] = max(
                0, trim.address_frame_source - trim.source_start_frame
            )

        return AnalysisResult(
            status="success",
            score=score_data["score"],
            recommendation=score_data["recommendation"],
            metrics=metrics,
            tuning=profile.to_dict(),
            trim=trim_dict,
            validation={
                "sharpness": validation.sharpness,
                "visible_keypoint_ratio": validation.visible_keypoint_ratio,
                "person_height_ratio": validation.person_height_ratio,
                "sampled_frames": validation.sampled_frames,
                "poses_detected": validation.poses_detected,
                "video": {
                    "width": meta.width,
                    "height": meta.height,
                    "fps": meta.fps,
                    "duration_sec": round(meta.duration_sec, 2),
                    "frame_count": meta.frame_count,
                },
            },
            stages=stages,
            annotated_video_url=f"/outputs/{output_filename}",
            analysis_id=analysis_id,
        )

    def _extract_poses_range(
        self,
        video_path: str,
        start_frame: int,
        end_frame: int,
    ) -> list[FramePose | None]:
        poses: list[FramePose | None] = []
        for i, frame in enumerate(iter_frames(video_path, start_frame, end_frame)):
            poses.append(self._pose.detect(frame, i))
        return poses

    @staticmethod
    def to_dict(result: AnalysisResult) -> dict[str, Any]:
        return {
            "status": result.status,
            "score": result.score,
            "recommendation": result.recommendation,
            "metrics": result.metrics,
            "validation": result.validation,
            "tuning": result.tuning,
            "trim": result.trim,
            "stages": [
                {
                    "id": s.id,
                    "label": s.label,
                    "status": s.status,
                    "duration_ms": s.duration_ms,
                    "message": s.message,
                }
                for s in result.stages
            ],
            "annotated_video_url": result.annotated_video_url,
            "analysis_id": result.analysis_id,
        }
