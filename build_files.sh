#!/usr/bin/env bash
set -e

# install python deps (safety)
pip install -r requirements.txt

# collect static into `staticfiles` directory
python manage.py collectstatic --noinput --clear
