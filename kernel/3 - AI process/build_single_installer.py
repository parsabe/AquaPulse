import os
import sys
import shutil
import subprocess
import zipfile
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def force_remove(path):
    if not os.path.exists(path):
        return
    def _onerror(func, p, exc_info):
        try:
            os.chmod(p, 0o777)
            func(p)
        except Exception:
            pass
    if os.path.isdir(path):
        shutil.rmtree(path, onerror=_onerror)
    else:
        try:
            os.remove(path)
        except Exception:
            pass

def main():
    start_time = time.time()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop_new_folder = r"C:\Users\parsa\Desktop\New folder"
    
    print("=" * 70)
    print("  Techno - Eco Project Single-File Installer Build Pipeline")
    print("=" * 70)
    print(f"Working Directory : {script_dir}")
    print(f"Target Output Dir : {desktop_new_folder}")
    
    # 1. Audit Prerequisites
    print("\n[Step 1/6] Auditing all neural models and core assets...")
    expected_models = [
        "JohnnySilverhand.index",
        "JohnnySilverhand_365e_12410s.pth",
        "best.pt",
        "fish_model.pt",
        "meduim.pt",
        "small.pt"
    ]
    models_dir = os.path.join(script_dir, "models")
    for m in expected_models:
        mp = os.path.join(models_dir, m)
        if not os.path.exists(mp):
            print(f"[ERROR] Required model missing: {mp}")
            sys.exit(1)
        size_mb = os.path.getsize(mp) / (1024 * 1024)
        print(f"  [OK] Verified model: {m:<35} ({size_mb:6.1f} MB)")

    expected_assets = [
        "johnny.gif",
        "report_template.tex",
        "aquapulse_system_architecture_documentation.tex",
        "app_icon.ico"
    ]
    for a in expected_assets:
        ap = os.path.join(script_dir, a)
        if not os.path.exists(ap):
            print(f"[ERROR] Required asset missing: {ap}")
            sys.exit(1)
        print(f"  [OK] Verified asset: {a}")

    pyinstaller_exe = r"c:\Users\parsa\Desktop\Code\venv\Scripts\pyinstaller.exe"
    if not os.path.exists(pyinstaller_exe):
        pyinstaller_exe = shutil.which("pyinstaller") or "pyinstaller"
    print(f"  [OK] Using PyInstaller: {pyinstaller_exe}")

    dist_dir = os.path.join(script_dir, "dist")
    build_dir = os.path.join(script_dir, "build")
    dist_app = os.path.join(dist_dir, "Techno_Eco_App")
    dist_uninstall = os.path.join(dist_dir, "Uninstall.exe")
    dist_setup = os.path.join(dist_dir, "Techno_Eco_Project_Setup.exe")
    payload_zip = os.path.join(script_dir, "app_payload.zip")

    # Clean previous builds
    force_remove(dist_app)
    force_remove(dist_uninstall)
    force_remove(dist_setup)
    force_remove(payload_zip)

    # 2. Compile Techno_Eco_App package (onedir)
    print("\n[Step 2/6] Compiling Techno - Eco Project core application bundle via AquaPulse.spec...")
    spec_app = os.path.join(script_dir, "AquaPulse.spec")
    subprocess.run([pyinstaller_exe, spec_app, "--noconfirm"], cwd=script_dir, check=True)

    app_exe = os.path.join(dist_app, "Techno_Eco_Project.exe")
    if not os.path.exists(app_exe):
        print(f"[ERROR] Application executable failed to build: {app_exe}")
        sys.exit(1)
    print(f"  [OK] Successfully compiled application bundle at: {dist_app}")

    # 3. Compile Uninstall.exe
    print("\n[Step 3/6] Compiling Control Panel Uninstaller via AquaPulse_Uninstaller.spec...")
    spec_uninstall = os.path.join(script_dir, "AquaPulse_Uninstaller.spec")
    subprocess.run([pyinstaller_exe, spec_uninstall, "--noconfirm"], cwd=script_dir, check=True)

    if not os.path.exists(dist_uninstall):
        print(f"[ERROR] Uninstaller failed to build: {dist_uninstall}")
        sys.exit(1)
    
    # Copy Uninstall.exe and app_icon.ico into the bundle
    shutil.copy2(dist_uninstall, os.path.join(dist_app, "Uninstall.exe"))
    shutil.copy2(os.path.join(script_dir, "app_icon.ico"), os.path.join(dist_app, "app_icon.ico"))
    print("  [OK] Bundled Uninstall.exe and app_icon.ico into Techno_Eco_App")

    # 4. Pack Techno_Eco_App into app_payload.zip
    print("\n[Step 4/6] Compressing application runtime, models, and assets into payload archive...")
    zip_count = 0
    with zipfile.ZipFile(payload_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
        for root, dirs, files in os.walk(dist_app):
            for file in files:
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, dist_app)
                zf.write(full_p, rel_p)
                zip_count += 1
                if zip_count % 500 == 0:
                    print(f"    Archived {zip_count} files...")
    
    payload_size_mb = os.path.getsize(payload_zip) / (1024 * 1024)
    print(f"  [OK] Created app_payload.zip ({payload_size_mb:.1f} MB, {zip_count} files)")

    # 5. Compile Techno_Eco_Project_Setup.exe (Single-file with embedded payload)
    print("\n[Step 5/6] Compiling single-file Setup Wizard (Techno_Eco_Project_Setup.exe) with embedded payload...")
    spec_setup = os.path.join(script_dir, "AquaPulse_Setup.spec")
    subprocess.run([pyinstaller_exe, spec_setup, "--noconfirm"], cwd=script_dir, check=True)

    if not os.path.exists(dist_setup):
        print(f"[ERROR] Setup executable failed to build: {dist_setup}")
        sys.exit(1)
        
    setup_size_mb = os.path.getsize(dist_setup) / (1024 * 1024)
    print(f"  [OK] Built standalone single-file installer: {dist_setup} ({setup_size_mb:.1f} MB)")

    # 6. Deploy ONLY AND ONLY the single .exe file to target directory
    print(f"\n[Step 6/6] Deploying standalone installer strictly to '{desktop_new_folder}'...")
    os.makedirs(desktop_new_folder, exist_ok=True)

    # Wipe all contents in target directory (including old AquaPulse_Setup.exe) to guarantee ONLY AND ONLY the single new .exe exists
    for item in os.listdir(desktop_new_folder):
        item_path = os.path.join(desktop_new_folder, item)
        force_remove(item_path)

    final_exe_dest = os.path.join(desktop_new_folder, "Techno_Eco_Project_Setup.exe")
    shutil.copy2(dist_setup, final_exe_dest)

    # Verify target directory strictly contains only that one .exe
    final_contents = os.listdir(desktop_new_folder)
    print(f"  Target directory item count: {len(final_contents)}")
    for f in final_contents:
        f_size = os.path.getsize(os.path.join(desktop_new_folder, f)) / (1024 * 1024)
        print(f"    * {f} ({f_size:.1f} MB)")

    if len(final_contents) == 1 and final_contents[0] == "Techno_Eco_Project_Setup.exe":
        print("\n" + "=" * 70)
        print("  [SUCCESS] ONLY AND ONLY ONE .EXE FILE CREATED!")
        print(f"  Installer Path: {final_exe_dest}")
        print(f"  Total Size    : {setup_size_mb:.1f} MB (Embedded with all 6 models & runtime)")
        print(f"  Time Elapsed  : {(time.time() - start_time) / 60:.1f} minutes")
        print("=" * 70)
    else:
        print(f"[WARNING] Target directory contains unexpected items: {final_contents}")

if __name__ == "__main__":
    main()
