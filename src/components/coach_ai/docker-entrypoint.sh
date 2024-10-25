#!/bin/bash

set -e

. ./.venv/bin/activate

alembic upgrade head

exec uvicorn main:app --host "0.0.0.0" --port 8008
