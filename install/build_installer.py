import os
import sys
import shutil
import zipfile
import subprocess

# Set stdout/stderr encoding to utf-8 if possible
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    install_dir = os.path.dirname(os.path.abspath(__file__))
    app_src_dir = r"C:\Users\parsa\Desktop\Code\3 - AI process\Vision transfromers"
    payload_zip = os.path.join(install_dir, "payload.zip")
    
    print("=" * 60)
    print("[BUILD] AquaPulse Standalone Windows Installer Builder")
    print("=" * 60)
    print(f"Install workspace: {install_dir}")
    print(f"Application source: {app_src_dir}")
    
    # 1. Install PyInstaller if missing
    try:
        import PyInstaller
        print(f"[OK] PyInstaller is available (version: {PyInstaller.__version__})")
    except ImportError:
        print("[INFO] Installing PyInstaller into virtual environment...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        import PyInstaller
        print("[OK] PyInstaller installed successfully.")

    # 2. Package application files into payload.zip
    print("\n[PACKAGING] Bundling application files & model weights into payload.zip...")
    if os.path.exists(payload_zip):
        os.remove(payload_zip)

    with zipfile.ZipFile(payload_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(app_src_dir):
            # Skip cache and unwanted folders
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".gradio", "tracked_output.mp4", "tracked_output2.mp4")]
            for file in files:
                if file.endswith(".log"):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, app_src_dir)
                zipf.write(file_path, rel_path)
                print(f"  + Added to payload: {rel_path}")

    print(f"[OK] Created payload bundle: {payload_zip} ({os.path.getsize(payload_zip) / (1024*1024):.2f} MB)")

    # 3. Build setup_wizard_gui.py into single AquaPulse_Setup.exe
    print("\n[COMPILING] Compiling standalone Setup Wizard executable into a single .exe file with PyInstaller...")
    
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=AquaPulse_Setup",
        f"--add-data={payload_zip};.",
        f"--distpath={install_dir}",
        f"--workpath={os.path.join(install_dir, 'build')}",
        os.path.join(install_dir, "setup_wizard_gui.py")
    ]
    
    print(f"Running command: {' '.join(pyinstaller_cmd)}")
    result = subprocess.run(pyinstaller_cmd, cwd=install_dir)
    
    if result.returncode == 0:
        exe_path = os.path.join(install_dir, "AquaPulse_Setup.exe")
        print("\n" + "=" * 60)
        print("[SUCCESS] SINGLE FILE INSTALLER BUILD COMPLETED!")
        print(f"Standalone Installer Executable Location: {exe_path}")
        print("=" * 60)
    else:
        print("\n[ERROR] PyInstaller build failed with return code:", result.returncode)

if __name__ == "__main__":
    main()
