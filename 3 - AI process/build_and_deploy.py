import os
import sys
import shutil
import subprocess

def main():
    script_dir = os.path.abspath(r"C:\Users\parsa\Desktop\Code\3 - AI process")
    install_win_dir = r"C:\Users\parsa\Desktop\Install\WIN"
    os.makedirs(install_win_dir, exist_ok=True)
    
    pyinstaller_exe = r"C:\Users\parsa\Desktop\Code\venv\Scripts\pyinstaller.exe"
    if not os.path.exists(pyinstaller_exe):
        pyinstaller_exe = shutil.which("pyinstaller") or "pyinstaller"

    print("==========================================================")
    print(" [Build] AquaPulse Windows Setup & Bundle Build Pipeline")
    print("==========================================================")

    # 1. Build AquaPulse_App
    print("\n[Step 1/3] Building AquaPulse Application package (AquaPulse_App)...")
    spec_app = os.path.join(script_dir, "AquaPulse.spec")
    subprocess.run([pyinstaller_exe, spec_app, "--noconfirm"], cwd=script_dir, check=True)

    dist_app = os.path.join(script_dir, "dist", "AquaPulse_App")
    if not os.path.exists(dist_app):
        print(f"[ERROR] Compiled application bundle not found at {dist_app}")
        sys.exit(1)

    # 2. Build Uninstall.exe
    print("\n[Step 2/3] Building Control Panel Uninstaller (Uninstall.exe)...")
    spec_uninstall = os.path.join(script_dir, "AquaPulse_Uninstaller.spec")
    subprocess.run([pyinstaller_exe, spec_uninstall, "--noconfirm"], cwd=script_dir, check=True)
    
    dist_uninstall = os.path.join(script_dir, "dist", "Uninstall.exe")
    if os.path.exists(dist_uninstall):
        shutil.copy2(dist_uninstall, os.path.join(script_dir, "Uninstall.exe"))
        shutil.copy2(dist_uninstall, os.path.join(dist_app, "Uninstall.exe"))
        print("  [OK] Uninstall.exe bundled into AquaPulse_App")

    # Copy AquaPulse_App into C:\Users\parsa\Desktop\Install\WIN\AquaPulse_App and script_dir
    dest_win_app = os.path.join(install_win_dir, "AquaPulse_App")
    if os.path.exists(dest_win_app):
        shutil.rmtree(dest_win_app, ignore_errors=True)
    shutil.copytree(dist_app, dest_win_app)

    setup_app_src = os.path.join(script_dir, "AquaPulse_App")
    if os.path.exists(setup_app_src):
        shutil.rmtree(setup_app_src, ignore_errors=True)
    shutil.copytree(dist_app, setup_app_src)

    # 3. Build AquaPulse_Setup.exe directly into C:\Users\parsa\Desktop\Install\WIN
    print("\n[Step 3/3] Building multi-page Setup Wizard GUI (AquaPulse_Setup.exe)...")
    spec_setup = os.path.join(script_dir, "AquaPulse_Setup.spec")
    subprocess.run([pyinstaller_exe, spec_setup, "--noconfirm", "--distpath", install_win_dir], cwd=script_dir, check=True)

    setup_exe = os.path.join(install_win_dir, "AquaPulse_Setup.exe")
    
    # Remove any old legacy installer files outside WIN
    legacy_setup = r"C:\Users\parsa\Desktop\Install\AquaPulse_Setup.exe"
    if os.path.exists(legacy_setup):
        try:
            os.remove(legacy_setup)
            print(f"  [Clean] Removed legacy installer file outside WIN: {legacy_setup}")
        except Exception:
            pass

    if os.path.exists(setup_exe):
        print(f"\n=======================================================")
        print(f" SUCCESS! Windows Setup Suite generated ONLY in:")
        print(f"    Target Directory: {install_win_dir}")
        print(f"    • Setup Wizard Executable: {setup_exe}")
        print(f"    • App Package Directory:   {dest_win_app}")
        print(f"=======================================================")
    else:
        print(f"\n[ERROR] Build Failed: Could not produce {setup_exe}")

if __name__ == "__main__":
    main()
