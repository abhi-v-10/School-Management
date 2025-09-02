#!/usr/bin/env bash
set -euo pipefail

echo "[render-build] === Build Start ==="
start_ts=$(date +%s)

PY=${PYTHON:-python}
echo "[render-build] Python: $($PY --version 2>&1)"

echo "[render-build] Installing dependencies (using pip cache)"
export PIP_DISABLE_PIP_VERSION_CHECK=1
# Rely on cached wheels; only install what's missing/changed
$PY -m pip install -r requirements.txt

echo "[render-build] Collecting static files"
$PY manage.py collectstatic --noinput --clear

end_ts=$(date +%s)
echo "[render-build] Done in $(( end_ts - start_ts ))s"
echo "[render-build] === Build Complete ==="
