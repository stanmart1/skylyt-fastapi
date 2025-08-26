#!/usr/bin/env python3
import os
import subprocess

# Change to frontend directory
frontend_dir = os.path.join(os.path.dirname(__file__), 'skylyt-frontend')
os.chdir(frontend_dir)

print("🚀 Starting Skylyt Frontend Server...")
print("📍 Frontend will be available at: http://localhost:8080")
print("🔗 Backend API: http://localhost:8000")
print("🛑 Press Ctrl+C to stop the server")

# Run the frontend development server
subprocess.run(['npm', 'run', 'dev'], check=True)