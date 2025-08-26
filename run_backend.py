#!/usr/bin/env python3
import os
import sys
import subprocess

# Change to backend directory
backend_dir = os.path.join(os.path.dirname(__file__), 'skylyt-travelhub-backend')
os.chdir(backend_dir)

# Activate virtual environment and run server
if os.name == 'nt':  # Windows
    activate_script = os.path.join('venv', 'Scripts', 'activate.bat')
    cmd = f'{activate_script} && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload'
else:  # Unix/Linux/macOS
    cmd = 'source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload'

print("🚀 Starting Skylyt Backend Server...")
print("📍 Server will be available at: http://localhost:8000")
print("📖 API Documentation: http://localhost:8000/docs")
print("🛑 Press Ctrl+C to stop the server")

subprocess.run(cmd, shell=True)