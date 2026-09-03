#!/usr/bin/env bash
# Start Label Studio preconfigured for datasets/clubhead/to_label
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${ROOT}/venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="$(command -v python3)"
fi

"$PYTHON" scripts/prepare_label_studio_tasks.py --skip-labeled

export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
export LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT="${ROOT}/datasets/clubhead"

echo ""
echo "=== Clubhead Label Studio ==="
echo "1) Install once (separate env recommended — Label Studio is heavy):"
echo "     pipx install label-studio"
echo "   or: python3 -m pip install --user label-studio"
echo ""
echo "2) Start:"
echo "     label-studio start --host 127.0.0.1 --port 8080"
echo ""
echo "3) Create project → Settings → Labeling Interface → Code → paste:"
echo "     ${ROOT}/datasets/clubhead/label_studio_config.xml"
echo ""
echo "4) Import tasks:"
echo "     ${ROOT}/datasets/clubhead/label_studio_tasks.json"
echo ""
echo "5) After labeling: Export → JSON, then:"
echo "     cd ${ROOT}"
echo "     ./venv/bin/python scripts/import_label_studio_export.py ~/Downloads/project-*.json"
echo "     ./venv/bin/python scripts/split_club_labels.py"
echo "     ./venv/bin/python scripts/train_clubhead.py --epochs 100"
echo ""
echo "DOCUMENT_ROOT=${LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT}"
echo "LOCAL_FILES_SERVING=${LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED}"
echo ""

if command -v label-studio >/dev/null 2>&1; then
  exec label-studio start --host 127.0.0.1 --port 8080
fi

echo "label-studio not on PATH — install it, then re-run this script or start manually."
exit 0
