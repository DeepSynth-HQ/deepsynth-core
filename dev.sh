#! /bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
alembic upgrade head
python -m uvicorn app.main:app --reload --port 5000