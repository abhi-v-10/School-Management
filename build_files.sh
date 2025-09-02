#!/usr/bin/env bash
set -e

echo "[render-build] Running Django build steps"
PY=${PYTHON:-python}
echo "[render-build] Interpreter: $($PY --version 2>&1)"

echo "[render-build] Collecting static files"
$PY manage.py collectstatic --noinput --clear

echo "[render-build] Build complete"
