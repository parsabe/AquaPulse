import os
import sys
import shutil
import subprocess

def main():
    script_dir = os.path.abspath(r"C:\Users\parsa\Desktop\Code\3 - AI process")
    target_output_dir = r"C:\Users\parsa\Desktop\New folder"
    os.makedirs(target_output_dir, exist_ok=True)

    dist_app = os.path.join(script_dir, "dist", "AquaPulse_App")
    dest_app = os.path.join(target_output_dir, "AquaPulse_App")

    print(f"[Build] Copying compiled AquaPulse_App bundle to: {dest_app}")
    if os.path.exists(dist_app):
        if os.path.exists(dest_app):
            shutil.rmtree(dest_app, ignore_errors=True)
        shutil.copytree(dist_app, dest_app)
        print("  [OK] AquaPulse_App copied successfully!")
    else:
        print(f"  [ERROR] {dist_app} does not exist.")
        sys.exit(1)

    print("\n[Build] Building standalone Windows Installer executable (AquaPulse_Setup.exe)...")
    spec_setup = os.path.join(script_dir, "AquaPulse_Setup.spec")
    pyinstaller_exe = r"C:\Users\parsa\Desktop\Code\venv\Scripts\pyinstaller.exe"
    
    res = subprocess.run([pyinstaller_exe, spec_setup, "--noconfirm", "--distpath", target_output_dir], cwd=script_dir)
    
    setup_exe = os.path.join(target_output_dir, "AquaPulse_Setup.exe")
    if os.path.exists(setup_exe):
        print(f"\n=======================================================")
        print(f"SUCCESS! Installer and app package created in:")
        print(f"   Destination: {target_output_dir}")
        print(f"   • Installer: {setup_exe}")
        print(f"   • App Folder: {dest_app}")
        print(f"=======================================================")
    else:
        print(f"\n[WARNING] Setup installer return code: {res.returncode}")

if __name__ == "__main__":
    main()
