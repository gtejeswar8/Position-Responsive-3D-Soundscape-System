import os
import sys
import venv
import subprocess

VENV_DIR = "venv"

def setup_venv():
    if not os.path.exists(VENV_DIR):
        print(f"Creating virtual environment in {VENV_DIR}...")
        venv.create(VENV_DIR, with_pip=True)
        
        # Install requirements
        pip_path = os.path.join(VENV_DIR, "Scripts", "pip") if os.name == "nt" else os.path.join(VENV_DIR, "bin", "pip")
        print("Installing dependencies...")
        subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])

def run_in_venv():
    python_path = os.path.join(VENV_DIR, "Scripts", "python") if os.name == "nt" else os.path.join(VENV_DIR, "bin", "python")
    
    if os.environ.get("VIRTUAL_ENV"):
        # We are already in a venv, just run main.py
        import main
        main.start()
    else:
        # Re-launch script using venv python
        print(f"Restarting in virtual environment...")
        subprocess.check_call([python_path, "main.py"])

if __name__ == "__main__":
    setup_venv()
    run_in_venv()
