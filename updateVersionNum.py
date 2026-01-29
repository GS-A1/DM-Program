"This python file is used to read and updated the version number of the application from the version.txt file."""

import os

def readVersionNumber():
    """Read the version number from the version.txt file."""
    version_file_path = os.path.join(os.path.dirname(__file__), "Settings", "version.txt") #need to do it this way to get the system to work when compiled to an exe
    try:
        with open(version_file_path, "r") as version_file:
            version = version_file.read().strip()
            return version
    except FileNotFoundError:
        return "Unknown Version"

def updateVersionNumber(new_version):
    version_file_path = os.path.join(os.path.dirname(__file__), "Settings", "version.txt")
    with open(version_file_path, "w") as version_file:
        version_file.write(new_version)

def incrementVersionNumberPatch():
    """Increment the patch version number by 0.1"""
    current_version = readVersionNumber()
    major, minor, patch = map(int, current_version.split('.'))
    patch += 1
    new_version = f"{major}.{minor}.{patch}"
    updateVersionNumber(new_version)
    return new_version

def incrementVersionNumberMinor():
    """Increment the minor version number by 1"""
    current_version = readVersionNumber()
    major, minor, patch = map(int, current_version.split('.'))
    minor += 1
    new_version = f"{major}.{minor}.{patch}"
    updateVersionNumber(new_version)
    return new_version

def incrementVersionNumberMajor():
    """Increment the major version number by 1"""
    current_version = readVersionNumber()
    major, minor, patch = map(int, current_version.split('.'))
    major += 1
    new_version = f"{major}.{minor}.{patch}"
    updateVersionNumber(new_version)
    return new_version