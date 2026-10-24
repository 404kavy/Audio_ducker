import sys
import subprocess
import os
import importlib

def check_and_install_dependencies():
    required_packages = ["pycaw", "comtypes", "psutil"]
    missing = []
    
    for pkg in required_packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
            
    if missing:
        print(f"Missing required packages: {missing}. Installing standard dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            importlib.invalidate_caches()
            print("Dependencies installed successfully!")
        except Exception as e:
            print(f"Could not automatically install packages: {e}")

if __name__ == "__main__":
    check_and_install_dependencies()
    
    from gui import main
    main()
