import os
import shutil
import sys
import subprocess
import urllib.request
import tkinter as tk
from tkinter import messagebox, ttk

# Internal PyInstaller path helper
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def check_python():
    try:
        # We check for 'py' launcher or 'python'
        subprocess.check_output(["python", "--version"], stderr=subprocess.STDOUT)
        return True
    except:
        return False

def download_and_install_python():
    # Official Python 3.12.2 64-bit installer URL
    url = "https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe"
    installer_path = os.path.join(os.environ["TEMP"], "python_installer.exe")
    
    try:
        messagebox.showinfo("Python Required", "Python was not found. We will now download the official installer.\n\nIMPORTANT: When the installer opens, you MUST check 'Add Python to PATH'!")
        
        # Download with a simple progress hint (or just wait)
        urllib.request.urlretrieve(url, installer_path)
        
        # Launch the installer and wait for it to finish
        # /passive = background but visible progress, PrependPath=1 = auto-check the PATH box!
        subprocess.call([installer_path, "/passive", "PrependPath=1"])
        
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to install Python: {e}")
        return False

def install_plugin():
    script_name = "7TV_Paint_Applier.py"
    try:
        # 1. Check for Python, install if missing
        if not check_python():
            if not download_and_install_python():
                return # User cancelled or failed

        # 2. Pathing logic for Resolve
        appdata = os.environ.get('APPDATA')
        target_dir = os.path.join(appdata, "Blackmagic Design", "DaVinci Resolve", "Support", "Fusion", "Scripts", "Comp")

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # 3. Move the bundled script
        source_path = get_resource_path(script_name)
        shutil.copy2(source_path, os.path.join(target_dir, script_name))
        
        messagebox.showinfo("Success", "Everything is set up!\n\n1. Python Installed\n2. Script Copied\n\nPlease RESTART DaVinci Resolve.")
        sys.exit()

    except Exception as e:
        messagebox.showerror("Installation Failed", f"Error: {str(e)}")

# UI
root = tk.Tk()
root.withdraw()
if messagebox.askyesno("7TV Plugin Installer", "Ready to install the 7TV Paint Applier and check for Python dependencies?"):
    install_plugin()