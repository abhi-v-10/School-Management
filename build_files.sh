#!/usr/bin/env bash
set -e

#!/usr/bin/env bash
set -euo pipefail

echo "[render-build] Installing Python dependencies"
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -r requirements.txt

PY=${PYTHON:-python}
echo "[render-build] Interpreter after install: $($PY --version 2>&1)"

echo "[render-build] Collecting static files"
$PY manage.py collectstatic --noinput --clear

echo "[render-build] Build complete"
