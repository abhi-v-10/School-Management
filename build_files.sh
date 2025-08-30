#!/usr/bin/env bash
set -e

echo "[build] Starting Django static collection"
PY=python3
command -v "$PY" >/dev/null 2>&1 || PY=python
echo "[build] Using Python interpreter: $PY ($($PY --version 2>&1))"

echo "[build] Installing (already installed by builder if using @vercel/python)"
# requirements installed by Vercel; skip reinstall to save time

echo "[build] Running collectstatic"
$PY manage.py collectstatic --noinput --clear

echo "[build] Listing staticfiles root (first 20 entries)"
ls -1 staticfiles | head -20 || true

echo "[build] Done"
