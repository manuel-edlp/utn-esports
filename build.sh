#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python src/manage.py collectstatic --no-input
python src/manage.py migrate
python src/manage.py sync_initial_staff