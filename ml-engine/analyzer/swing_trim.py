"""Auto-detect swing segment and compute trim window (Tier 1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import config
from analyzer.metrics.biomechanics import GolfBiomechanicsAnalyzer, SwingPhases
from analyzer.pose import FramePose, PoseExtractor
from analyzer.video_io import VideoMeta, iter_frames


@dataclass(frozen=True)
class TrimWindow:
    """Inclusive source-frame range used for pose extraction and annotated output."""

    applied: bool
    source_start_frame: int
    source_end_frame: int
    address_frame_source: int
    top_frame_source: int
    impact_frame_source: int
    original_frame_count: int
    trimmed_frame_count: int
    original_duration_sec: float
    trimmed_duration_sec: float
    setup_trimmed_sec: float
    scan_step: int
    padding_before_sec: float
    padding_after_sec: float
    fps: float = 30.0

    @staticmethod
    def no_trim(meta: VideoMeta) -> TrimWindow:
        return TrimWindow(
            applied=False,
            source_start_frame=0,
            source_end_frame=max(0, meta.frame_count - 1),
            address_frame_source=0,
            top_frame_source=0,
            impact_frame_source=0,
            original_frame_count=meta.frame_count,
            trimmed_frame_count=meta.frame_count,
            original_duration_sec=meta.duration_sec,
            trimmed_duration_sec=meta.duration_sec,
            setup_trimmed_sec=0.0,
            scan_step=1,
            padding_before_sec=0.0,
            padding_after_sec=0.0,
            fps=meta.fps,
        )

    def phase_hints_in_trim(self) -> tuple[int, int, int] | None:
        if not self.applied:
            return None
        offset = self.source_start_frame
        return (
            self.address_frame_source - offset,
            self.top_frame_source - offset,
            self.impact_frame_source - offset,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "applied": self.applied,
            "source_start_frame": self.source_start_frame,
            "source_end_frame": self.source_end_frame,
            "address_frame_source": self.address_frame_source,
            "top_frame_source": self.top_frame_source,
            "impact_frame_source": self.impact_frame_source,
            "original_frame_count": self.original_frame_count,
            "trimmed_frame_count": self.trimmed_frame_count,
            "original_duration_sec": round(self.original_duration_sec, 2),
            "trimmed_duration_sec": round(self.trimmed_duration_sec, 2),
            "setup_trimmed_sec": round(self.setup_trimmed_sec, 2),
            "trimmed_start_sec": round(self.source_start_frame / self.fps, 2) if self.fps > 0 else 0.0,
            "trimmed_end_sec": round(self.source_end_frame / self.fps, 2) if self.fps > 0 else 0.0,
            "scan_step": self.scan_step,
            "padding_before_sec": self.padding_before_sec,
            "padding_after_sec": self.padding_after_sec,
        }


def scout_trim_window(
    video_path: str,
    meta: VideoMeta,
    pose_extractor: PoseExtractor,
    scan_step: int | None = None,
) -> TrimWindow:
    """
    Fast subsampled pose pass to locate address/top/impact in source video,
    then return padded [start, end] frame range for full analysis.
    """
    step = scan_step or config.TRIM_SCAN_STEP
    sparse_poses: list[FramePose] = []

    for i, frame in enumerate(iter_frames(video_path)):
        if i % step != 0:
            continue
        pose = pose_extractor.detect(frame, i)
        if pose is not None:
            sparse_poses.append(pose)

    if len(sparse_poses) < 8:
        return TrimWindow.no_trim(meta)

    bio = GolfBiomechanicsAnalyzer(sparse_poses).analyze()
    phases = bio.phases

    try:
        address_src = sparse_poses[phases.address].frame_index
        top_src = sparse_poses[phases.top].frame_index
        impact_src = sparse_poses[phases.impact].frame_index
    except IndexError:
        return TrimWindow.no_trim(meta)

    pad_before = int(meta.fps * config.TRIM_PADDING_BEFORE_ADDRESS_SEC)
    pad_after = int(meta.fps * config.TRIM_PADDING_AFTER_IMPACT_SEC)

    start = max(0, address_src - pad_before)
    end = min(meta.frame_count - 1, impact_src + pad_after)

    # Ensure enough frames for analysis; don't trim if detection looks invalid
    min_span = max(config.TRIM_MIN_FRAMES, config.MIN_FRAME_COUNT // 2)
    if end <= start or (end - start + 1) < min_span:
        return TrimWindow.no_trim(meta)

    # Skip trim if we'd only shave off negligible setup (< 0.3s) and keep almost all video
    setup_sec = start / meta.fps if meta.fps > 0 else 0.0
    trimmed_frames = end - start + 1
    if setup_sec < 0.3 and trimmed_frames >= meta.frame_count * 0.92:
        return TrimWindow.no_trim(meta)

    trimmed_sec = trimmed_frames / meta.fps if meta.fps > 0 else meta.duration_sec

    return TrimWindow(
        applied=True,
        source_start_frame=start,
        source_end_frame=end,
        address_frame_source=address_src,
        top_frame_source=top_src,
        impact_frame_source=impact_src,
        original_frame_count=meta.frame_count,
        trimmed_frame_count=trimmed_frames,
        original_duration_sec=meta.duration_sec,
        trimmed_duration_sec=trimmed_sec,
        setup_trimmed_sec=setup_sec,
        scan_step=step,
        padding_before_sec=config.TRIM_PADDING_BEFORE_ADDRESS_SEC,
        padding_after_sec=config.TRIM_PADDING_AFTER_IMPACT_SEC,
        fps=meta.fps,
    )
