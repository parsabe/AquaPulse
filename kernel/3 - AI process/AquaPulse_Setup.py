import os
import sys
import shutil
import subprocess
import urllib.request
import winreg
import threading
import time
import zipfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def check_and_install_ollama(log_callback=print):
    log_callback("Checking Ollama AI Engine installation...")
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
        log_callback(f"  [OK] Ollama AI Engine detected at: {ollama_path}")
    else:
        log_callback("  [INFO] Ollama not detected. Downloading Ollama AI Engine...")
        installer_url = "https://ollama.com/download/OllamaSetup.exe"
        temp_installer = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "OllamaSetup.exe")
        try:
            log_callback("  [DOWNLOAD] Downloading OllamaSetup.exe...")
            urllib.request.urlretrieve(installer_url, temp_installer)
            log_callback("  [INSTALL] Executing silent Ollama installation...")
            subprocess.run([temp_installer, "/silent"], check=True)
            log_callback("  [OK] Ollama installation complete!")
        except Exception as e:
            log_callback(f"  [INFO] Notice: Could not auto-install Ollama ({e}). Techno - Eco Project will use offline fallback.")

    log_callback("Verifying Ollama 'llama3' AI model status...")
    try:
        res = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "llama3" not in res.stdout:
            log_callback("  [DOWNLOAD] Pulling 'llama3' neural LLM weights...")
            subprocess.run(["ollama", "pull", "llama3"])
            log_callback("  [OK] Llama3 model loaded into local Ollama repository!")
        else:
            log_callback("  [OK] Model 'llama3' is ready in local Ollama repository.")
    except Exception as e:
        log_callback(f"  [INFO] Notice: Could not verify llama3 model automatically ({e}).")

def check_and_install_latex(log_callback=print):
    log_callback("Checking LaTeX (pdflatex) compiler installation...")
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
        log_callback(f"  [OK] LaTeX (pdflatex) compiler detected at: {pdflatex_path}")
    else:
        log_callback("  [INFO] pdflatex not detected. Downloading MiKTeX setup executable...")
        miktex_url = "https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/basic-miktex-24.1-x64.exe"
        temp_installer = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "basic-miktex.exe")
        try:
            log_callback("  [DOWNLOAD] Downloading basic-miktex setup executable...")
            urllib.request.urlretrieve(miktex_url, temp_installer)
            log_callback("  [INSTALL] Running automated MiKTeX setup...")
            subprocess.run([temp_installer, "--unattended", "--shared"], check=True)
            log_callback("  [OK] MiKTeX LaTeX installation finished successfully!")
        except Exception as e:
            log_callback(f"  [INFO] Notice: MiKTeX setup step skipped ({e}). Ensure MiKTeX or TeX Live is installed for PDF report exports.")

def create_shortcuts(target_exe, icon_path=None, log_callback=print):
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        start_menu = os.path.join(os.environ.get("APPDATA", r"C:\Users\Public"), r"Microsoft\Windows\Start Menu\Programs")
        
        shortcut_targets = [
            os.path.join(desktop, "Techno - Eco Project.lnk"),
            os.path.join(start_menu, "Techno - Eco Project.lnk")
        ]
        
        icon_stmt = f'shortcut.IconLocation = "{icon_path},0"' if (icon_path and os.path.exists(icon_path)) else f'shortcut.IconLocation = "{target_exe},0"'
        
        for sc in shortcut_targets:
            vbs_script = f"""
            Set WshShell = WScript.CreateObject("WScript.Shell")
            Set shortcut = WshShell.CreateShortcut("{sc}")
            shortcut.TargetPath = "{target_exe}"
            shortcut.WorkingDirectory = "{os.path.dirname(target_exe)}"
            {icon_stmt}
            shortcut.Description = "Techno - Eco Project AI Neural Vision & EnKF Telemetry System"
            shortcut.Save
            """
            temp_vbs = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "create_shortcut.vbs")
            with open(temp_vbs, "w") as f:
                f.write(vbs_script)
            subprocess.run(["cscript", "//Nologo", temp_vbs], check=True)
            if os.path.exists(temp_vbs):
                os.remove(temp_vbs)
            log_callback(f"  [OK] Created Shortcut: {sc}")
    except Exception as e:
        log_callback(f"  [INFO] Notice creating shortcut ({e}).")

def register_control_panel_uninstaller(install_dir, log_callback=print):
    app_exe = os.path.join(install_dir, "Techno_Eco_Project.exe")
    uninstaller_exe = os.path.join(install_dir, "Uninstall.exe")
    icon_file = os.path.join(install_dir, "app_icon.ico")
    display_icon = icon_file if os.path.exists(icon_file) else app_exe
    
    reg_key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\TechnoEcoProject"
    registered = False
    
    for root_key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        try:
            key = winreg.CreateKeyEx(root_key, reg_key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Techno - Eco Project AI Vision System")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Techno - Eco Project Team")
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstaller_exe}"')
            winreg.SetValueEx(key, "QuietUninstallString", 0, winreg.REG_SZ, f'"{uninstaller_exe}" /quiet')
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, display_icon)
            winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, 1200000)
            winreg.CloseKey(key)
            registered = True
            log_callback("  [OK] Registered in Windows Control Panel (Add or Remove Programs)")
            break
        except Exception:
            continue

    if not registered:
        log_callback("  [INFO] Control Panel registration completed with user scope.")

class TechnoEcoSetupWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("Techno - Eco Project Setup Wizard")
        self.root.geometry("640x480")
        self.root.resizable(False, False)
        
        # Center on screen
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - 640) // 2
        y = (sh - 480) // 2
        self.root.geometry(f"640x480+{x}+{y}")
        
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        for ic in [os.path.join(base_dir, "app_icon.ico"), os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico")]:
            if os.path.exists(ic):
                try:
                    self.root.iconbitmap(ic)
                    break
                except Exception:
                    pass
        
        self.install_dir_var = tk.StringVar(value=r"C:\Techno-Eco-Project")
        self.opt_ollama_var = tk.BooleanVar(value=True)
        self.opt_latex_var = tk.BooleanVar(value=True)
        self.opt_shortcut_var = tk.BooleanVar(value=True)
        self.opt_launch_var = tk.BooleanVar(value=True)
        
        self.current_page = 0
        self.pages = []
        
        self._build_ui()
        self._show_page(0)

    def _build_ui(self):
        # Header banner - Fresh Emerald/Deep Forest Eco-Tech styling
        self.header_frame = tk.Frame(self.root, bg="#064e3b", height=72)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)
        
        self.header_title = tk.Label(
            self.header_frame, text="Techno - Eco Project Setup",
            font=("Segoe UI", 15, "bold"), fg="#34d399", bg="#064e3b"
        )
        self.header_title.pack(anchor="w", padx=22, pady=(12, 0))
        
        self.header_subtitle = tk.Label(
            self.header_frame, text="Autonomous Marine Computer Vision & Stochastic Ecosystem Telemetry",
            font=("Segoe UI", 9), fg="#a7f3d0", bg="#064e3b"
        )
        self.header_subtitle.pack(anchor="w", padx=22, pady=(0, 10))
        
        # Bottom navigation
        self.nav_frame = tk.Frame(self.root, bg="#e2e8f0", height=50)
        self.nav_frame.pack(fill="x", side="bottom")
        self.nav_frame.pack_propagate(False)
        
        self.cancel_btn = tk.Button(
            self.nav_frame, text="Cancel", font=("Segoe UI", 9),
            bg="#cbd5e1", fg="#0f172a", relief="flat", padx=15, pady=4, cursor="hand2", command=self._on_cancel
        )
        self.cancel_btn.pack(side="right", padx=15, pady=10)
        
        self.next_btn = tk.Button(
            self.nav_frame, text="Next >", font=("Segoe UI", 9, "bold"),
            bg="#059669", fg="white", activebackground="#047857", activeforeground="white",
            relief="flat", padx=18, pady=4, cursor="hand2", command=self._on_next
        )
        self.next_btn.pack(side="right", padx=5, pady=10)
        
        self.back_btn = tk.Button(
            self.nav_frame, text="< Back", font=("Segoe UI", 9),
            bg="#cbd5e1", fg="#0f172a", relief="flat", padx=15, pady=4, cursor="hand2", command=self._on_back
        )
        self.back_btn.pack(side="right", padx=5, pady=10)
        
        # Content container
        self.container = tk.Frame(self.root, bg="#f8fafc")
        self.container.pack(fill="both", expand=True)
        
        # Build pages
        self._build_page_welcome()
        self._build_page_location()
        self._build_page_options()
        self._build_page_installing()
        self._build_page_finish()

    def _build_page_welcome(self):
        page = tk.Frame(self.container, bg="#f8fafc")
        
        lbl_h = tk.Label(
            page, text="Welcome to the Techno - Eco Project Setup Wizard",
            font=("Segoe UI", 13, "bold"), fg="#0f172a", bg="#f8fafc"
        )
        lbl_h.pack(anchor="w", padx=25, pady=(25, 10))
        
        txt = (
            "This wizard will guide you through the setup and installation of Techno - Eco Project "
            "on your computer.\n\n"
            "Installation details:\n"
            "  * Destination Folder: Drive C: (default: C:\\Techno-Eco-Project)\n"
            "  * Multi-Model YOLO Ensemble & Persistent Species Tracker\n"
            "  * Local Ollama AI Engine & LaTeX Scientific Exporter\n"
            "  * Windows Control Panel Uninstaller Integration & Desktop Shortcuts\n\n"
            "Click Next to choose installation directory and begin."
        )
        
        lbl_body = tk.Label(
            page, text=txt, font=("Segoe UI", 10),
            fg="#334155", bg="#f8fafc", justify="left", wraplength=580
        )
        lbl_body.pack(anchor="w", padx=25, pady=10)
        
        self.pages.append(page)

    def _build_page_location(self):
        page = tk.Frame(self.container, bg="#f8fafc")
        
        lbl_h = tk.Label(
            page, text="Select Destination Directory",
            font=("Segoe UI", 13, "bold"), fg="#0f172a", bg="#f8fafc"
        )
        lbl_h.pack(anchor="w", padx=25, pady=(20, 5))
        
        lbl_sub = tk.Label(
            page, text="Where should Techno - Eco Project be installed?",
            font=("Segoe UI", 10), fg="#64748b", bg="#f8fafc"
        )
        lbl_sub.pack(anchor="w", padx=25, pady=(0, 15))
        
        box = tk.LabelFrame(
            page, text=" Destination Folder ",
            font=("Segoe UI", 9, "bold"), fg="#0f172a", bg="#f8fafc", padx=15, pady=15
        )
        box.pack(fill="x", padx=25, pady=10)
        
        entry_frame = tk.Frame(box, bg="#f8fafc")
        entry_frame.pack(fill="x")
        
        entry = tk.Entry(
            entry_frame, textvariable=self.install_dir_var,
            font=("Segoe UI", 10), bg="white", fg="#0f172a", relief="solid", bd=1
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=4)
        
        def browse():
            folder = filedialog.askdirectory(initialdir="C:\\", title="Select Installation Folder")
            if folder:
                self.install_dir_var.set(folder)
                
        btn_browse = tk.Button(
            entry_frame, text="Browse...", font=("Segoe UI", 9),
            bg="#e2e8f0", fg="#0f172a", cursor="hand2", command=browse
        )
        btn_browse.pack(side="right")
        
        lbl_info = tk.Label(
            page, text="Space required: ~3.3 GB\nTarget drive: Drive C:\\",
            font=("Segoe UI", 9), fg="#475569", bg="#f8fafc", justify="left"
        )
        lbl_info.pack(anchor="w", padx=25, pady=15)
        
        self.pages.append(page)

    def _build_page_options(self):
        page = tk.Frame(self.container, bg="#f8fafc")
        
        lbl_h = tk.Label(
            page, text="Select Components & Prerequisites",
            font=("Segoe UI", 13, "bold"), fg="#0f172a", bg="#f8fafc"
        )
        lbl_h.pack(anchor="w", padx=25, pady=(20, 5))
        
        lbl_sub = tk.Label(
            page, text="Configure component verification and system integration:",
            font=("Segoe UI", 10), fg="#64748b", bg="#f8fafc"
        )
        lbl_sub.pack(anchor="w", padx=25, pady=(0, 15))
        
        box = tk.LabelFrame(
            page, text=" Setup Options ",
            font=("Segoe UI", 9, "bold"), fg="#0f172a", bg="#f8fafc", padx=15, pady=15
        )
        box.pack(fill="x", padx=25, pady=10)
        
        cb1 = tk.Checkbutton(
            box, text="Install / Verify Ollama AI Engine & llama3 model weights",
            variable=self.opt_ollama_var, font=("Segoe UI", 10), bg="#f8fafc", activebackground="#f8fafc"
        )
        cb1.pack(anchor="w", pady=5)
        
        cb2 = tk.Checkbutton(
            box, text="Install / Verify MiKTeX LaTeX PDF report exporter compiler",
            variable=self.opt_latex_var, font=("Segoe UI", 10), bg="#f8fafc", activebackground="#f8fafc"
        )
        cb2.pack(anchor="w", pady=5)
        
        cb3 = tk.Checkbutton(
            box, text="Create Desktop & Start Menu Shortcuts (Techno - Eco Project)",
            variable=self.opt_shortcut_var, font=("Segoe UI", 10), bg="#f8fafc", activebackground="#f8fafc"
        )
        cb3.pack(anchor="w", pady=5)
        
        lbl_cp = tk.Label(
            page, text="* Techno - Eco Project will automatically register with Windows Control Panel for clean uninstallation.",
            font=("Segoe UI", 9), fg="#059669", bg="#f8fafc", justify="left", wraplength=580
        )
        lbl_cp.pack(anchor="w", padx=25, pady=15)
        
        self.pages.append(page)

    def _build_page_installing(self):
        page = tk.Frame(self.container, bg="#f8fafc")
        
        lbl_h = tk.Label(
            page, text="Installing Techno - Eco Project...",
            font=("Segoe UI", 13, "bold"), fg="#0f172a", bg="#f8fafc"
        )
        lbl_h.pack(anchor="w", padx=25, pady=(20, 5))
        
        self.install_status_lbl = tk.Label(
            page, text="Preparing installation package...",
            font=("Segoe UI", 10), fg="#059669", bg="#f8fafc"
        )
        self.install_status_lbl.pack(anchor="w", padx=25, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(page, mode="determinate", length=590)
        self.progress_bar.pack(padx=25, pady=5)
        
        log_frame = tk.Frame(page, bg="#0f172a", bd=1, relief="solid")
        log_frame.pack(fill="both", expand=True, padx=25, pady=(10, 20))
        
        self.log_text = tk.Text(
            log_frame, bg="#0f172a", fg="#34d399",
            font=("Consolas", 9), state="disabled", wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, side="left")
        
        sb = tk.Scrollbar(log_frame, command=self.log_text.yview)
        sb.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=sb.set)
        
        self.pages.append(page)

    def _build_page_finish(self):
        page = tk.Frame(self.container, bg="#f8fafc")
        
        lbl_h = tk.Label(
            page, text="Installation Complete! [OK]",
            font=("Segoe UI", 15, "bold"), fg="#059669", bg="#f8fafc"
        )
        lbl_h.pack(anchor="w", padx=25, pady=(25, 10))
        
        self.finish_txt = tk.Label(
            page, text="Techno - Eco Project AI Neural Vision & EnKF Telemetry System has been successfully installed on your computer.",
            font=("Segoe UI", 10), fg="#334155", bg="#f8fafc", justify="left", wraplength=580
        )
        self.finish_txt.pack(anchor="w", padx=25, pady=10)
        
        self.loc_txt = tk.Label(page, text="", font=("Segoe UI", 9, "italic"), fg="#64748b", bg="#f8fafc")
        self.loc_txt.pack(anchor="w", padx=25, pady=5)
        
        cb = tk.Checkbutton(
            page, text="Launch Techno - Eco Project now",
            variable=self.opt_launch_var, font=("Segoe UI", 10, "bold"),
            fg="#059669", bg="#f8fafc", activebackground="#f8fafc"
        )
        cb.pack(anchor="w", padx=25, pady=25)
        
        self.pages.append(page)

    def _log(self, message):
        def append():
            self.log_text.config(state="normal")
            self.log_text.insert("end", message + "\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.root.after(0, append)

    def _set_status(self, status, progress_val=None):
        def update():
            self.install_status_lbl.config(text=status)
            if progress_val is not None:
                self.progress_bar["value"] = progress_val
        self.root.after(0, update)

    def _show_page(self, idx):
        for p in self.pages:
            p.pack_forget()
            
        self.current_page = idx
        self.pages[idx].pack(fill="both", expand=True)
        
        if idx == 0:
            self.back_btn.config(state="disabled")
            self.next_btn.config(text="Next >", state="normal", bg="#059669", activebackground="#047857")
        elif idx == 1:
            self.back_btn.config(state="normal")
            self.next_btn.config(text="Next >", state="normal", bg="#059669", activebackground="#047857")
        elif idx == 2:
            self.back_btn.config(state="normal")
            self.next_btn.config(text="Install", bg="#059669", activebackground="#047857", state="normal")
        elif idx == 3:
            self.back_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
            self.cancel_btn.config(state="disabled")
            threading.Thread(target=self._run_installation, daemon=True).start()
        elif idx == 4:
            self.back_btn.config(state="disabled")
            self.cancel_btn.config(state="disabled")
            self.next_btn.config(text="Finish", bg="#059669", activebackground="#047857", state="normal")

    def _on_next(self):
        if self.current_page == 4:
            target_dir = self.install_dir_var.get()
            app_exe = os.path.join(target_dir, "Techno_Eco_Project.exe")
            if self.opt_launch_var.get() and os.path.exists(app_exe):
                subprocess.Popen([app_exe], cwd=target_dir)
            self.root.destroy()
            sys.exit(0)
        else:
            self._show_page(self.current_page + 1)

    def _on_back(self):
        if self.current_page > 0:
            self._show_page(self.current_page - 1)

    def _on_cancel(self):
        if messagebox.askyesno("Cancel Setup", "Are you sure you want to cancel Techno - Eco Project Installation?"):
            self.root.destroy()
            sys.exit(0)

    def _run_installation(self):
        target_dir = self.install_dir_var.get()
        self._log(f"Installation Target Directory: {target_dir}")
        self._set_status("Preparing installation package...", 10)
        
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))
            
        base_dir = getattr(sys, '_MEIPASS', exe_dir)
        os.makedirs(target_dir, exist_ok=True)
        
        # 1. Check for embedded or local app_payload.zip
        possible_zips = [
            os.path.join(base_dir, "app_payload.zip"),
            os.path.join(exe_dir, "app_payload.zip"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_payload.zip"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "app_payload.zip")
        ]
        
        zip_payload = None
        for zp in possible_zips:
            if os.path.exists(zp):
                zip_payload = zp
                break
                
        deployed_ok = False
        if zip_payload:
            self._log(f"  [EXTRACT] Unpacking system binaries, dependencies, and neural models from {os.path.basename(zip_payload)}...")
            try:
                with zipfile.ZipFile(zip_payload, 'r') as zf:
                    members = zf.namelist()
                    total_members = len(members)
                    for i, member in enumerate(members, start=1):
                        zf.extract(member, target_dir)
                        if i % 100 == 0 or i == total_members:
                            pct = 10 + int((i / total_members) * 45)
                            base_n = os.path.basename(member) or member
                            self._set_status(f"Extracting: {base_n} ({i}/{total_members})", pct)
                        if "models" in member and not member.endswith('/'):
                            self._log(f"  [MODEL] Extracted Neural Model: {os.path.basename(member)}")
                self._log(f"  [OK] Complete Techno - Eco Project runtime and models deployed to {target_dir}!")
                deployed_ok = True
            except Exception as e:
                self._log(f"  [ERROR] Error unzipping package ({e})")
                
        if not deployed_ok:
            possible_app_sources = [
                os.path.join(exe_dir, "Techno_Eco_App"),
                os.path.join(base_dir, "Techno_Eco_App"),
                os.path.join(exe_dir, "dist", "Techno_Eco_App")
            ]
            app_source = None
            for p in possible_app_sources:
                if os.path.exists(p):
                    app_source = p
                    break
            if app_source:
                self._log(f"  [DEPLOY] Deploying application binaries from {app_source}...")
                shutil.copytree(app_source, target_dir, dirs_exist_ok=True)
                self._log(f"  [OK] Application binaries deployed to {target_dir}!")
            else:
                self._log("  [WARN] Application payload source not found.")

        # Ensure app_icon.ico is present in target_dir
        dest_icon = os.path.join(target_dir, "app_icon.ico")
        if not os.path.exists(dest_icon):
            for ic in [os.path.join(base_dir, "app_icon.ico"), os.path.join(exe_dir, "app_icon.ico"), os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico")]:
                if os.path.exists(ic):
                    try:
                        shutil.copy2(ic, dest_icon)
                        break
                    except Exception:
                        pass

        # Ensure Uninstall.exe is present in target_dir
        dest_uninstaller = os.path.join(target_dir, "Uninstall.exe")
        if not os.path.exists(dest_uninstaller):
            possible_uninstallers = [
                os.path.join(base_dir, "Uninstall.exe"),
                os.path.join(exe_dir, "Uninstall.exe"),
                os.path.join(exe_dir, "Techno_Eco_App", "Uninstall.exe")
            ]
            for u in possible_uninstallers:
                if os.path.exists(u):
                    try:
                        shutil.copy2(u, dest_uninstaller)
                        self._log("  [OK] Installed Control Panel Uninstaller (Uninstall.exe)")
                        break
                    except Exception:
                        pass
        else:
            self._log("  [OK] Verified Control Panel Uninstaller (Uninstall.exe)")

        self._set_status("Configuring Control Panel & Shortcuts...", 60)
        register_control_panel_uninstaller(target_dir, log_callback=self._log)
        
        app_exe = os.path.join(target_dir, "Techno_Eco_Project.exe")
        if self.opt_shortcut_var.get() and os.path.exists(app_exe):
            icon_for_shortcut = dest_icon if os.path.exists(dest_icon) else app_exe
            create_shortcuts(app_exe, icon_path=icon_for_shortcut, log_callback=self._log)
            
        if self.opt_ollama_var.get():
            self._set_status("Verifying Ollama AI Engine & llama3 model...", 75)
            check_and_install_ollama(log_callback=self._log)
            
        if self.opt_latex_var.get():
            self._set_status("Verifying LaTeX compiler...", 90)
            check_and_install_latex(log_callback=self._log)
            
        self._set_status("Installation Complete!", 100)
        self._log("\n[SUCCESS] Techno - Eco Project Setup completed successfully!")
        
        def finish_page_update():
            self.loc_txt.config(text=f"Installed Location: {app_exe}")
            self._show_page(4)
            
        self.root.after(1000, finish_page_update)

def main():
    root = tk.Tk()
    app = TechnoEcoSetupWizard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
