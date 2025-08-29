#!/usr/bin/env python3
import os
import subprocess

def initialize_project():
    """Initialize the project after generation"""
    print("🚀 Initializing your multi-agent system project...")
    
    # Create gitkeep files for empty directories
    empty_dirs = [
        "../backend/data/external",
        "../backend/data/interim", 
        "../backend/data/processed",
        "../backend/artifacts",
        "../backend/notebooks",

    ]
    
    for dir_path in empty_dirs:
        gitkeep_path = os.path.join(dir_path, ".gitkeep")
        os.makedirs(os.path.dirname(gitkeep_path), exist_ok=True)
        with open(gitkeep_path, 'w') as f:
            f.write("# This file ensures the directory is tracked by git\n")
    
    print("✅ Project structure created successfully!")
    print(f"📁 Your project is located at: {os.getcwd()}")
    print("\nNext steps:")
    print("1. pip install -r requirements.txt")
    print("2. Configure system_config.yaml")
    print("3. Start developing your multi-agent system!")

def show_welcome_banner():
    banner = """
    ╔══════════════════════════════════════════════════╗
    ║                  🚀 AGENTFORGE                   ║
    ║           Multi-Agent System Template            ║
    ║                                                  ║ 
    ║           Crafted with ❤️ by goldirana           ║
    ╚══════════════════════════════════════════════════╝
    """
    print(banner)
    
def export_env_variables():
    """Export environment variables from .env file"""
    if os.path.exists(".env"):
        print("🔄 Exporting environment variables from .env file...")
        command = "set -a && source .env && set +a"
        subprocess.run(command, shell=True, check=True, executable='/bin/bash')
        print("✅ Environment variables exported successfully!")
    else:
        print("⚠️ .env file not found. Please create one to set environment variables.")


import os
import sys
import subprocess
from pathlib import Path
import shutil

ctx = {
    "python_version": "{{ cookiecutter.python_version }}",
    "create_virtualenv": "{{ cookiecutter.create_virtualenv }}",
    "venv_name": "{{ cookiecutter.venv_name }}",
    "project_slug": "{{ cookiecutter.project_slug }}"
}

def which(cmd):
    return shutil.which(cmd)

def pick_python_interpreter(target_py):
    """
    Try to find a Python executable matching major.minor (e.g., '3.12').
    We try 'python3.12', then 'python3', then 'python', and check version.
    """
    candidates = [f"python{target_py}", "python3", "python"]
    for cand in candidates:
        exe = which(cand)
        if not exe:
            continue
        try:
            out = subprocess.check_output([exe, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"])
            ver = out.decode().strip()
            if ver == target_py:
                return exe
        except Exception:
            pass
    # Fall back to current if version differs; the user can manage it later
    return sys.executable

def create_venv(python_exe, venv_name):
    venv_path = Path(venv_name).expanduser().resolve()
    try:
        subprocess.check_call([python_exe, "-m", "venv", str(venv_path)])
        return venv_path
    except subprocess.CalledProcessError as e:
        print(f"[cookiecutter] ERROR: Failed to create venv with {python_exe}: {e}")
        return None

def print_activation_help(venv_path):
    if os.name == "nt":
        activate = venv_path / "Scripts" / "activate"
        pip = venv_path / "Scripts" / "pip"
        python = venv_path / "Scripts" / "python"
    else:
        activate = venv_path / "bin" / "activate"
        pip = venv_path / "bin" / "pip"
        python = venv_path / "bin" / "python"

    print("\n[cookiecutter] Virtual environment created.")
    print(f"Activate:\n  source {activate}" if os.name != "nt" else f"  {activate}")
    print(f"Pip:      {pip}")
    print(f"Python:   {python}\n")


if __name__ == "__main__":
    initialize_project()
    if ctx["create_virtualenv"].lower() == "y":
        py = pick_python_interpreter(ctx["python_version"])
        if not py:
            print("[cookiecutter] WARNING: Could not find a Python interpreter; skipping venv creation.")
            sys.exit(0)

        venv_path = create_venv(py, ctx["venv_name"])
        if venv_path:
            print_activation_help(venv_path)
        else:
            print("[cookiecutter] WARNING: venv creation failed; please set it up manually.")
    
    show_welcome_banner()