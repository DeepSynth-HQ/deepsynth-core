#! /bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
export ENV=development
alembic upgrade head 
uvicorn app.main:app --host 0.0.0.0 --port 5000