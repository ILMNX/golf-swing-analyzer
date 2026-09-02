"""YOLOv8-pose extraction."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from ultralytics import YOLO

import config


@dataclass
class FramePose:
    frame_index: int
    keypoints: np.ndarray  # shape (17, 3) -> x, y, confidence
    bbox: np.ndarray | None  # xyxy


class PoseExtractor:
    def __init__(self, model: YOLO | None = None):
        self._model = model or YOLO(config.MODEL_PATH)

    def detect(self, frame: np.ndarray, frame_index: int = 0) -> FramePose | None:
        results = self._model(frame, verbose=False)
        if not results or results[0].keypoints is None:
            return None

        kpts_data = results[0].keypoints.data
        if kpts_data is None or len(kpts_data) == 0:
            return None

        # Use the largest detected person (by bbox area)
        boxes = results[0].boxes
        person_idx = 0
        if boxes is not None and len(boxes) > 1:
            areas = []
            for box in boxes.xyxy:
                areas.append(float((box[2] - box[0]) * (box[3] - box[1])))
            person_idx = int(np.argmax(areas))

        keypoints = kpts_data[person_idx].cpu().numpy()
        bbox = None
        if boxes is not None and len(boxes) > person_idx:
            bbox = boxes.xyxy[person_idx].cpu().numpy()

        return FramePose(frame_index=frame_index, keypoints=keypoints, bbox=bbox)

    def detect_batch(self, frames: list[np.ndarray], start_index: int = 0) -> list[FramePose | None]:
        return [self.detect(frame, start_index + i) for i, frame in enumerate(frames)]

    @staticmethod
    def visible_ratio(pose: FramePose, min_conf: float = config.MIN_POSE_CONFIDENCE) -> float:
        visible = np.sum(pose.keypoints[:, 2] >= min_conf)
        return float(visible / pose.keypoints.shape[0])

    @staticmethod
    def person_height_ratio(pose: FramePose, frame_height: int) -> float:
        if pose.bbox is None:
            ys = pose.keypoints[pose.keypoints[:, 2] >= config.MIN_POSE_CONFIDENCE, 1]
            if len(ys) == 0:
                return 0.0
            return float((ys.max() - ys.min()) / frame_height)

        return float((pose.bbox[3] - pose.bbox[1]) / frame_height)
