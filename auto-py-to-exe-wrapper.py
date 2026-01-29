#!/usr/bin/env python3

"""Wrapper script to increment version number and run auto-py-to-exe with preloaded settings"""

import subprocess
import sys
import shutil
import os
from pathlib import Path


def run(cmd, *, cwd=None):
    """Run a command, stream output to console, and raise on failure."""
    print(f"\n=== Running: {' '.join(cmd)} ===")
    subprocess.run(cmd, cwd=cwd, check=True)


def main():
    # # --- Command 1 ---
    # # python -c "from updateVersionNum import incrementVersionNumberPatch; incrementVersionNumberPatch()"
    # cmd1 = [
    #     sys.executable,
    #     "-c",
    #     "from updateVersionNum import incrementVersionNumberPatch; incrementVersionNumberPatch()",
    # ]

    # # --- Command 2 ---
    # # auto-py-to-exe -c "exe_generation/auto_py_settings.json"
    # config_path = Path("exe_generation") / "auto_py_settings.json"
    # if not config_path.exists():
    #     raise FileNotFoundError(f"Config file not found: {config_path.resolve()}")

    # # Use -m to ensure we run the auto-py-to-exe module from this environment
    # cmd2 = [
    #     sys.executable,
    #     "-m",
    #     "auto_py_to_exe",
    #     "-c",
    #     str(config_path),
    # ]

    # try:
    #     run(cmd1)
    #     run(cmd2)
    # except subprocess.CalledProcessError as e:
    #     print(f"\nCommand failed with exit code {e.returncode}")
    #     raise
    
    print("\nZipping and moving the output folder...")
    #make a .zip of the output folder and move it to the last_build folder
    dm_assistant_folder = "output/DM Assistant"
    last_build_folder = "last_build"

    if os.path.exists(dm_assistant_folder):
        os.makedirs(last_build_folder, exist_ok=True)
        
        # Create zip in current directory
        zip_path = shutil.make_archive("DM Assistant", "zip", "output", "DM Assistant")
        
        # Move it to last_build folder
        shutil.move(zip_path, os.path.join(last_build_folder, os.path.basename(zip_path)))
        print(f"Zip moved to: {os.path.join(last_build_folder, 'DM Assistant.zip')}")
    else:
        print(f"Output folder not found: {dm_assistant_folder}")

    print("\nOperations Completed.")

if __name__ == "__main__":
    main()