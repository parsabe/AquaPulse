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
    app_dist_dir = os.path.join(install_dir, "app_dist")
    compiled_app_dir = os.path.join(app_dist_dir, "AquaPulseVision")
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

    # 2. STAGE 1: Compile main.py into standalone AquaPulseVision binary distribution
    print("\n[STAGE 1] Compiling main.py into standalone AquaPulseVision.exe binary...")
    model_file = os.path.join(app_src_dir, "fish_model.pt")
    
    app_pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=AquaPulseVision",
        f"--add-data={model_file};.",
        "--hidden-import=ultralytics",
        "--hidden-import=langchain_ollama",
        "--hidden-import=pyttsx3",
        "--hidden-import=pyttsx3.drivers",
        "--hidden-import=pyttsx3.drivers.sapi5",
        f"--distpath={app_dist_dir}",
        f"--workpath={os.path.join(install_dir, 'app_work')}",
        os.path.join(app_src_dir, "main.py")
    ]
    
    print(f"Running command: {' '.join(app_pyinstaller_cmd)}")
    res_app = subprocess.run(app_pyinstaller_cmd, cwd=app_src_dir)
    if res_app.returncode != 0:
        print("\n[ERROR] Failed to compile main.py into AquaPulseVision binary.")
        sys.exit(1)
        
    # Copy extra asset files (like main.mp4) into compiled app folder
    sample_video = os.path.join(app_src_dir, "main.mp4")
    if os.path.exists(sample_video):
        shutil.copy(sample_video, os.path.join(compiled_app_dir, "main.mp4"))
        print("  + Copied sample video main.mp4 into compiled app distribution.")

    # 3. STAGE 2: Package compiled binary folder into payload.zip
    print("\n[STAGE 2] Bundling compiled binary distribution into payload.zip...")
    if os.path.exists(payload_zip):
        os.remove(payload_zip)

    with zipfile.ZipFile(payload_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(compiled_app_dir):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".gradio")]
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, compiled_app_dir)
                zipf.write(file_path, rel_path)

    print(f"[OK] Created payload bundle: {payload_zip} ({os.path.getsize(payload_zip) / (1024*1024):.2f} MB)")

    # 4. STAGE 3: Build setup_wizard_gui.py into single AquaPulse_Setup.exe installer
    print("\n[STAGE 3] Compiling standalone Setup Wizard into AquaPulse_Setup.exe...")
    
    installer_cmd = [
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
    
    print(f"Running command: {' '.join(installer_cmd)}")
    result = subprocess.run(installer_cmd, cwd=install_dir)
    
    if result.returncode == 0:
        exe_path = os.path.join(install_dir, "AquaPulse_Setup.exe")
        print("\n" + "=" * 60)
        print("[SUCCESS] FULL STANDALONE INSTALLER BUILD COMPLETED!")
        print(f"Single Setup File Location: {exe_path}")
        print("This installer works on ANY Windows PC out-of-the-box (no Python needed).")
        print("=" * 60)
    else:
        print("\n[ERROR] PyInstaller build failed with return code:", result.returncode)

if __name__ == "__main__":
    main()
