import os
import sys
import shutil
import tempfile
import platform
import winreg

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def cleanup_temp():
    """Clean up PyInstaller temp folder"""
    try:
        temp_dir = tempfile._get_default_tempdir()
        for filename in os.listdir(temp_dir):
            if filename.startswith('_MEI'):
                try:
                    filepath = os.path.join(temp_dir, filename)
                    if os.path.isdir(filepath):
                        shutil.rmtree(filepath, ignore_errors=True)
                except:
                    pass
    except:
        pass

def get_windows_version():
    """Get Windows version as a tuple (major, minor, build)"""
    ver = platform.version().split('.')
    return (int(ver[0]), int(ver[1]), int(ver[2])) 