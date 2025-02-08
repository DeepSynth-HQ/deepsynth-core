#! /bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
export ENV=development
alembic upgrade head
python -m uvicorn app.main:app --reload --port 5000