#!/usr/bin/env bash
set -e

# Do NOT reinstall requirements here, Vercel already does that
python3 manage.py collectstatic --noinput --clear
