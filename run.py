import subprocess
import sys
import time
import os

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print("=" * 60)
    print("🌴 Starting CocoCare AI — Coconut Tree Disease Detection System")
    print("=" * 60)

    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    frontend_cmd = [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501"]

    print("🚀 Launching FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_process = subprocess.Popen(backend_cmd)
    
    time.sleep(2) # Give backend time to initialize SQLite & API endpoints

    print("🚀 Launching Streamlit Frontend on http://127.0.0.1:8501 ...")
    frontend_process = subprocess.Popen(frontend_cmd)

    print("\n✅ CocoCare AI Application is running!")
    print("   • Frontend UI:  http://127.0.0.1:8501")
    print("   • Backend API:   http://127.0.0.1:8000")
    print("   • Swagger Docs:  http://127.0.0.1:8000/docs\n")
    print("Press Ctrl+C in this terminal to stop both servers.\n")

    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nStopping CocoCare AI servers...")
        backend_process.terminate()
        frontend_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
