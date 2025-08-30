#!/usr/bin/env bash
set -e

# Run collectstatic using whichever python binary exists on the build machine.
PY=python3
command -v "$PY" >/dev/null 2>&1 || PY=python

# Do NOT reinstall requirements here, Vercel already installs them for the Python builder.
$PY manage.py collectstatic --noinput --clear
