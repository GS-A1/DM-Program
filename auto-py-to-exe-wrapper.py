#!/usr/bin/env python3

"""Wrapper script to increment version number and run auto-py-to-exe with preloaded settings"""

import subprocess
import sys
import shutil
import os
from pathlib import Path
import zipfile

GREEN_BOLD = "\033[1;32m"
RED_BOLD = "\033[1;31m"
RESET = "\033[0m"

def run(cmd, *, cwd=None):
    """Run a command, stream output to console, and raise on failure."""
    print(f"\n=== Running: {' '.join(cmd)} ===")
    subprocess.run(cmd, cwd=cwd, check=True)

def message(msg = ""):
    print(f"{GREEN_BOLD}{msg}{RESET}")

def error(msg = ""):
    print(f"{RED_BOLD}{msg}{RESET}")

def main():
    #Folders
    last_build_folder = "last_build"
    dm_assistant_folder = "output/DM Assistant"
    settings_folders = ["Settings/Characters", "Settings/Condition_Spell_Effects"]
    
    message("Starting build process...")
    ##########################################Increment Version Number###########################################
    # --- Command 1 ---
    # python -c "from updateVersionNum import incrementVersionNumberPatch; incrementVersionNumberPatch()"
    cmd1 = [
        sys.executable,
        "-c",
        "from updateVersionNum import incrementVersionNumberPatch; incrementVersionNumberPatch()",
    ]
    ##########################################Running auto-py-to-exe for main program##########################################
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
    
    ##########################################Running auto-py-to-exe for installer##########################################
    # --- Command 3 ---
    #use pyinstaller directly to build the installer from installer.py
    pyinstaller_cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--icon",
        "exe_generation/dnd_dm_installer_icon.ico",
        "--add-data", r"Settings\version.txt;Settings",
        "--distpath",
        "installer",
        "installer.py"
    ]
    
    ##########################################Executing Commands##########################################
    try:
        message("\nIncrementing version number...")
        run(cmd1)
        message("\nBuilding main program with auto-py-to-exe...")
        run(cmd2)
        message("\nBuilding installer with PyInstaller...")
        run(pyinstaller_cmd)
        message(f"\nInstaller built successfully. File located at: {os.path.join('installer', 'installer.exe')}")
    except subprocess.CalledProcessError as e:
        error(f"\nCommand failed with exit code {e.returncode}")
        raise
    
    ##########################################Creating Output Zip##########################################
    message("\nZipping and moving the output folder...")
    #make a .zip of the output folder and move it to the last_build folder

    if os.path.exists(dm_assistant_folder):
        os.makedirs(last_build_folder, exist_ok=True)
        
        # Create zip in current directory (use underscore in filename)
        zip_path = shutil.make_archive("DM_Assistant", "zip", "output", "DM Assistant")
        
        # Move it to last_build folder
        shutil.move(zip_path, os.path.join(last_build_folder, os.path.basename(zip_path)))
        message(f"Zip moved to: {os.path.join(last_build_folder, 'DM_Assistant.zip')}")
    else:
        error(f"Output folder not found: {dm_assistant_folder}")
    
    # ##########################################Creatings Settings Zip##########################################
    message("\nZipping and moving the Settings folder...")
    # make a .zip containing only the specified Settings subfolders and move it to the last_build folder
    settings_zip_name = "Settings"
    # ensure all requested folders exist before creating zip
    if all(os.path.exists(folder) for folder in settings_folders):
        os.makedirs(last_build_folder, exist_ok=True)

        settings_root = "Settings"
        zip_file_name = settings_zip_name + ".zip"
        # Create zip in current directory and add only the listed subfolders
        with zipfile.ZipFile(zip_file_name, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for folder in settings_folders:
                if os.path.exists(folder):
                    for root, _, files in os.walk(folder):
                        for f in files:
                            if not f.startswith('.') and not f.__contains__("test"):  # skip hidden files and test files
                                full_path = os.path.join(root, f)
                                # store paths relative to the Settings root (so entries are like Characters/...)
                                arcname = os.path.relpath(full_path, start=settings_root)
                                zf.write(full_path, arcname)
        # Move it to last_build folder
        shutil.move(zip_file_name, os.path.join(last_build_folder, os.path.basename(zip_file_name)))
        message(f"Settings zip moved to: {os.path.join(last_build_folder, settings_zip_name + '.zip')}")
    else:
        error("One or more Settings subfolders missing; skipping settings zip.")

    message("\nOperations Completed.")
    
if __name__ == "__main__":
    main()