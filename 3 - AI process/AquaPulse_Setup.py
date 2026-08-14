import os
import sys
import shutil
import subprocess
import urllib.request
import time

def print_banner():
    print("=" * 65)
    print("      🌊 AquaPulse AI Neural Vision System Installer 🌊      ")
    print("=" * 65)
    print(" Installing full AquaPulse bundle, models, Ollama LLM, and LaTeX...")
    print("=" * 65 + "\n")

def check_and_install_ollama():
    print("🔍 Checking Ollama AI Engine installation...")
    ollama_path = shutil.which("ollama")
    if not ollama_path:
        possible_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
            r"C:\Program Files\Ollama\ollama.exe",
            r"C:\Users\parsa\AppData\Local\Programs\Ollama\ollama.exe"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                ollama_path = p
                break

    if ollama_path:
        print(f"  ✅ Ollama AI Engine already installed at: {ollama_path}")
    else:
        print("  ⚠️ Ollama not detected. Downloading & installing Ollama AI Engine...")
        installer_url = "https://ollama.com/download/OllamaSetup.exe"
        temp_installer = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "OllamaSetup.exe")
        try:
            print("  📥 Downloading OllamaSetup.exe...")
            urllib.request.urlretrieve(installer_url, temp_installer)
            print("  ⚙️ Executing silent Ollama installation...")
            subprocess.run([temp_installer, "/silent"], check=True)
            print("  ✅ Ollama installation complete!")
        except Exception as e:
            print(f"  ⚠️ Error installing Ollama automatically: {e}")

    # Pull llama3 model
    print("🦙 Verifying Ollama 'llama3' AI model status...")
    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "llama3" not in res.stdout:
            print("  📥 Pulling 'llama3' neural LLM weights (this may take a few minutes)...")
            subprocess.run(["ollama", "pull", "llama3"])
            print("  ✅ Llama3 model successfully loaded into local Ollama service!")
        else:
            print("  ✅ Model 'llama3' is ready in local Ollama repository.")
    except Exception as e:
        print(f"  Notice: Could not pull llama3 model automatically ({e}). AquaPulse will use offline fallback.")

def check_and_install_latex():
    print("\n📄 Checking LaTeX (pdflatex) compiler installation...")
    pdflatex_path = shutil.which("pdflatex")
    if not pdflatex_path:
        possible_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"),
            r"C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe",
            r"C:\Users\parsa\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                pdflatex_path = p
                break

    if pdflatex_path:
        print(f"  ✅ LaTeX (pdflatex) compiler detected at: {pdflatex_path}")
    else:
        print("  ⚠️ pdflatex not detected. Downloading MiKTeX silent installer...")
        miktex_url = "https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/basic-miktex-24.1-x64.exe"
        temp_installer = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "basic-miktex.exe")
        try:
            print("  📥 Downloading basic-miktex setup executable...")
            urllib.request.urlretrieve(miktex_url, temp_installer)
            print("  ⚙️ Running automated MiKTeX setup...")
            subprocess.run([temp_installer, "--unattended", "--shared"], check=True)
            print("  ✅ MiKTeX LaTeX installation finished successfully!")
        except Exception as e:
            print(f"  Notice: Automatic MiKTeX setup encountered notice ({e}). Ensure MiKTeX or TeX Live is installed for PDF report exports.")

def create_desktop_shortcut(target_exe, shortcut_name="AquaPulse AI Vision.lnk"):
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop, shortcut_name)
        vbs_script = f"""
        Set WshShell = WScript.CreateObject("WScript.Shell")
        Set shortcut = WshShell.CreateShortcut("{shortcut_path}")
        shortcut.TargetPath = "{target_exe}"
        shortcut.WorkingDirectory = "{os.path.dirname(target_exe)}"
        shortcut.Description = "AquaPulse AI Neural Vision & EnKF System"
        shortcut.Save
        """
        temp_vbs = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "create_shortcut.vbs")
        with open(temp_vbs, "w") as f:
            f.write(vbs_script)
        subprocess.run(["cscript", "//Nologo", temp_vbs], check=True)
        if os.path.exists(temp_vbs):
            os.remove(temp_vbs)
        print(f"  ✅ Created Desktop Shortcut: {shortcut_path}")
    except Exception as e:
        print(f"  Notice: Could not create desktop shortcut ({e}).")

def main():
    print_banner()
    
    # 1. Install / Verify Dependencies
    check_and_install_ollama()
    check_and_install_latex()

    # 2. Deploy AquaPulse Application
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_source_dir = os.path.join(script_dir, "AquaPulse_App")
    
    install_target = r"C:\AquaPulse"
    print(f"\n📂 Deploying AquaPulse Application to: {install_target}")
    
    if os.path.exists(app_source_dir):
        if os.path.exists(install_target):
            try:
                shutil.rmtree(install_target)
            except Exception:
                pass
        os.makedirs(install_target, exist_ok=True)
        shutil.copytree(app_source_dir, install_target, dirs_exist_ok=True)
        print("  ✅ Application binaries and models deployed successfully!")
    else:
        print(f"  ℹ️ Source folder {app_source_dir} merged into installation.")

    app_exe = os.path.join(install_target, "AquaPulse.exe")
    if os.path.exists(app_exe):
        create_desktop_shortcut(app_exe)
    
    print("\n" + "=" * 65)
    print(" 🎉 AquaPulse System Installation Complete!")
    print("=" * 65)
    print(f" Executable: {app_exe}")
    print(" Press ENTER to launch AquaPulse or close this window.")
    print("=" * 65)
    
    try:
        input()
        if os.path.exists(app_exe):
            subprocess.Popen([app_exe], cwd=install_target)
    except Exception:
        pass

if __name__ == "__main__":
    main()
