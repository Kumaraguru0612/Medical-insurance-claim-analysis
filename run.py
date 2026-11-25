import os
import sys
import subprocess
import webbrowser
import time

def main():
    print("=" * 70)
    print("  MEDICLAIM AI: MEDICAL INSURANCE CLAIM DATA MINING & PREDICTION")
    print("=" * 70)
    
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(workspace_dir, "backend")
    frontend_dir = os.path.join(workspace_dir, "frontend")
    dist_dir = os.path.join(frontend_dir, "dist")
    
    # Check if frontend is built
    if not os.path.exists(os.path.join(dist_dir, "index.html")):
        print("\n[INFO] Building frontend production assets with Vite...")
        subprocess.run(["cmd.exe", "/c", "npm", "run", "build"], cwd=frontend_dir, check=True)
    
    print("\n[INFO] Starting Flask Backend & Web Application Server...")
    print("       URL: http://127.0.0.1:5000")
    print("       API Health: http://127.0.0.1:5000/api/health")
    print("\n[INFO] Press Ctrl+C to terminate the server.\n")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(1.5)
        try:
            webbrowser.open("http://127.0.0.1:5000")
        except Exception:
            pass

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Launch app.py
    sys.path.insert(0, backend_dir)
    from app import app
    app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    main()
