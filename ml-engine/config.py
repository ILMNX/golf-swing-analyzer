"""ML engine configuration."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
VIDEO_DIR = BASE_DIR / "video"

MODEL_PATH = "yolov8n-pose.pt"

# Video technical limits
MIN_DURATION_SEC = 1.0
MAX_DURATION_SEC = 30.0
MIN_FRAME_COUNT = 15
MIN_WIDTH = 320
MIN_HEIGHT = 240
MIN_FPS = 15.0

# Auto-trim swing segment (Tier 1)
TRIM_SCAN_STEP = 4                    # scout every Nth frame
TRIM_PADDING_BEFORE_ADDRESS_SEC = 0.5 # keep half-second before address
TRIM_PADDING_AFTER_IMPACT_SEC = 1.0   # keep 1s follow-through after impact
TRIM_MIN_FRAMES = 45                  # minimum trimmed segment length

# Quality thresholds
MIN_SHARPNESS = 50.0          # Laplacian variance
MIN_POSE_CONFIDENCE = 0.35    # per-keypoint confidence
MIN_VISIBLE_KEYPOINT_RATIO = 0.55
MIN_PERSON_HEIGHT_RATIO = 0.25  # bbox height / frame height
VALIDATION_SAMPLE_FRAMES = 12

# Overlay colors (BGR for OpenCV)
COLOR_SKELETON = (61, 122, 30)       # #1E7A3D
COLOR_JOINT = (161, 227, 166)        # #A6E3A1
COLOR_TRAIL = (200, 200, 232)        # subtle off-white trail
SKELETON_THICKNESS = 2
JOINT_RADIUS = 4

# Annotated output: repeat each frame N times at the same fps (smooth slow motion).
SLOWMO_REPEAT_FACTOR = 4
