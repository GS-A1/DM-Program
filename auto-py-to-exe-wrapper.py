#!/usr/bin/env python3

"""Wrapper script to increment version number and run auto-py-to-exe with preloaded settings"""

import subprocess
import sys
from pathlib import Path


def run(cmd, *, cwd=None):
    """Run a command, stream output to console, and raise on failure."""
    print(f"\n=== Running: {' '.join(cmd)} ===")
    subprocess.run(cmd, cwd=cwd, check=True)


def main():
    # --- Command 1 ---
    # python -c "from updateVersionNum import incrementVersionNumberPatch; incrementVersionNumberPatch()"
    cmd1 = [
        sys.executable,
        "-c",
        "from updateVersionNum import incrementVersionNumberPatch; incrementVersionNumberPatch()",
    ]

    # --- Command 2 ---
    # auto-py-to-exe -c "exe_generation/auto_py_settings.json"
    config_path = Path("exe_generation") / "auto_py_settings.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path.resolve()}")

    # Use -m to ensure we run the auto-py-to-exe module from this environment
    cmd2 = [
        sys.executable,
        "-m",
        "auto_py_to_exe",
        "-c",
        str(config_path),
    ]

    try:
        run(cmd1)
        run(cmd2)
        print("\nDone.")
    except subprocess.CalledProcessError as e:
        print(f"\nCommand failed with exit code {e.returncode}")
        raise


if __name__ == "__main__":
    main()