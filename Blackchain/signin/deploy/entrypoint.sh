#!/bin/bash

python3 -u init.py &

uvicorn proxy:app --host 0.0.0.0 --port 8888