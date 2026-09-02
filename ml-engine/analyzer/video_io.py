"""Video read/write helpers."""

from __future__ import annotations

import logging
import os
import subprocess
from dataclasses import dataclass

import cv2
import numpy as np

from analyzer.exceptions import ValidationError
import config

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VideoMeta:
    path: str
    width: int
    height: int
    fps: float
    frame_count: int
    duration_sec: float


def read_video_meta(path: str) -> VideoMeta:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValidationError("Video tidak dapat dibaca. Pastikan format MP4/MOV valid.", code="invalid_video")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    if frame_count <= 0 or fps <= 0:
        raise ValidationError("Video rusak atau tidak memiliki frame yang valid.", code="corrupt_video")

    duration = frame_count / fps

    return VideoMeta(
        path=path,
        width=width,
        height=height,
        fps=fps,
        frame_count=frame_count,
        duration_sec=duration,
    )


def validate_video_meta(meta: VideoMeta) -> None:
    if meta.duration_sec < config.MIN_DURATION_SEC:
        raise ValidationError(
            f"Video terlalu pendek (min {config.MIN_DURATION_SEC}s). Rekam minimal satu swing penuh.",
            code="video_too_short",
        )
    if meta.duration_sec > config.MAX_DURATION_SEC:
        raise ValidationError(
            f"Video terlalu panjang (maks {config.MAX_DURATION_SEC}s). Potong ke bagian swing saja.",
            code="video_too_long",
        )
    if meta.frame_count < config.MIN_FRAME_COUNT:
        raise ValidationError("Frame video tidak cukup untuk analisis.", code="insufficient_frames")
    if meta.width < config.MIN_WIDTH or meta.height < config.MIN_HEIGHT:
        raise ValidationError(
            f"Resolusi terlalu rendah (min {config.MIN_WIDTH}x{config.MIN_HEIGHT}).",
            code="low_resolution",
        )
    if meta.fps < config.MIN_FPS:
        raise ValidationError(
            f"FPS terlalu rendah (min {config.MIN_FPS}). Rekam dengan frame rate lebih tinggi.",
            code="low_fps",
        )


def iter_frames(path: str, start_frame: int = 0, end_frame: int | None = None):
    """Yield frames from video, optionally bounded to [start_frame, end_frame] inclusive."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValidationError("Gagal membuka video.", code="invalid_video")

    if start_frame > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    try:
        frame_idx = start_frame
        while end_frame is None or frame_idx <= end_frame:
            ok, frame = cap.read()
            if not ok:
                break
            yield frame
            frame_idx += 1
    finally:
        cap.release()


def iter_all_frames(path: str):
    """Yield all frames from video."""
    yield from iter_frames(path)


def sample_frame_indices(frame_count: int, sample_size: int) -> list[int]:
    if frame_count <= sample_size:
        return list(range(frame_count))
    step = frame_count // sample_size
    return [min(i * step, frame_count - 1) for i in range(sample_size)]


def read_sample_frames(path: str, indices: list[int]) -> list[np.ndarray]:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValidationError("Gagal membaca sample frame.", code="invalid_video")

    frames: list[np.ndarray] = []
    try:
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if ok:
                frames.append(frame)
    finally:
        cap.release()

    return frames


def measure_sharpness(frame: np.ndarray) -> float:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def create_video_writer(path: str, width: int, height: int, fps: float) -> cv2.VideoWriter:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, fps, (width, height))
    if not writer.isOpened():
        raise ValidationError("Gagal membuat video output.", code="output_failed")
    return writer


def transcode_for_browser(path: str) -> str:
    """
    Re-encode OpenCV mpeg4 output to H.264/yuv420p for HTML5 <video> playback.
    Raises if ffmpeg is missing or transcode fails.
    """
    temp_path = f"{path}.web.mp4"
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", path,
        "-c:v", "libx264",
        "-profile:v", "baseline",
        "-level", "3.1",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-an",
        temp_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise ValidationError(
                f"Transcode video gagal: {result.stderr.strip() or 'ffmpeg error'}",
                code="transcode_failed",
            )
        if not _is_browser_compatible_h264(temp_path):
            raise ValidationError(
                "Output video tidak kompatibel browser setelah transcode.",
                code="transcode_failed",
            )
        os.replace(temp_path, path)
        return path
    except FileNotFoundError:
        raise ValidationError(
            "ffmpeg tidak ditemukan. Install ffmpeg agar video analisis dapat diputar di browser.",
            code="ffmpeg_missing",
        ) from None
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def _is_browser_compatible_h264(path: str) -> bool:
    """Return True when the file contains H.264 video in a browser-friendly pixel format."""
    probe = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,pix_fmt",
        "-of", "csv=p=0",
        path,
    ]
    try:
        result = subprocess.run(probe, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return False
        line = result.stdout.strip().lower()
        return line.startswith("h264,") and "yuv420p" in line
    except FileNotFoundError:
        return False
