
#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def run_command(cmd, cwd=None, env=None):
    """Run command in a separate thread"""
    def target():
        try:
            subprocess.run(cmd, shell=True, cwd=cwd, env=env, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {cmd}")
            print(f"Exit code: {e.returncode}")
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    return thread

def main():
    print("🚀 Starting AI Manus Development Environment...")
    
    # Set up environment
    env = os.environ.copy()
    
    # Install backend dependencies
    print("📦 Installing backend dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], check=True)
    
    # Install frontend dependencies
    print("📦 Installing frontend dependencies...")
    subprocess.run(["npm", "install"], cwd="frontend", check=True)
    
    # Install mockserver dependencies
    print("📦 Installing mockserver dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "mockserver/requirements.txt"], check=True)
    
    # Install sandbox dependencies
    print("📦 Installing sandbox dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "sandbox/requirements.txt"], check=True)
    
    print("\n🎯 Starting services...")
    
    # Start mockserver (mock LLM API)
    print("Starting MockServer on port 8090...")
    mockserver_thread = run_command(
        f"{sys.executable} mockserver/main.py",
        env=env
    )
    time.sleep(2)
    
    # Start sandbox
    print("Starting Sandbox on port 8080...")
    sandbox_thread = run_command(
        f"{sys.executable} -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload",
        cwd="sandbox",
        env=env
    )
    time.sleep(2)
    
    # Start backend
    print("Starting Backend on port 8000...")
    backend_thread = run_command(
        f"{sys.executable} -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload",
        cwd="backend",
        env=env
    )
    time.sleep(3)
    
    # Start frontend
    print("Starting Frontend on port 5173...")
    frontend_thread = run_command(
        "npm run dev -- --host 0.0.0.0 --port 5173",
        cwd="frontend",
        env=env
    )
    
    print("\n✅ All services started!")
    print("🌐 Frontend: http://localhost:5173")
    print("🔧 Backend API: http://localhost:8000")
    print("🏗️ Sandbox API: http://localhost:8080")
    print("🎭 MockServer: http://localhost:8090")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        sys.exit(0)

if __name__ == "__main__":
    main()
