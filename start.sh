#!/bin/bash
set -e

# Note: IP addresses should be updated from host before starting containers
# python update_ip.py

# Start backend
echo " Starting backend (FastAPI)..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Wait a moment for backend to start
sleep 2

# Start Expo
echo " Starting Expo..."
expo start --tunnel