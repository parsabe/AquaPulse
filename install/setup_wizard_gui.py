import os
import sys
import time
import shutil
import zipfile
import subprocess
import urllib.request
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class AquaPulseSetupWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AquaPulse Cyberpunk Vision Setup Wizard")
        self.geometry("640x480")
        self.resizable(False, False)
        
        # Windows styling
        self.configure(bg="#0f172a")
        
        default_dir = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\"), "AquaPulse")
        self.dest_dir = tk.StringVar(value=default_dir)
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.launch_app_on_finish = tk.BooleanVar(value=True)
        
        self.current_step = 0
        self.frames = []
        
        self.setup_ui_styles()
        self.init_frames()
        self.show_step(0)

    def setup_ui_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background='#0f172a')
        style.configure('TLabel', background='#0f172a', foreground='#f8fafc', font=('Segoe UI', 10))
        style.configure('Header.TLabel', background='#0f172a', foreground='#38bdf8', font=('Segoe UI', 16, 'bold'))
        style.configure('SubHeader.TLabel', background='#0f172a', foreground='#94a3b8', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), background='#0284c7', foreground='#ffffff', padding=6)
        style.map('TButton', background=[('active', '#0369a1')])
        style.configure('TCheckbutton', background='#0f172a', foreground='#f8fafc', font=('Segoe UI', 10))

    def init_frames(self):
        # Navigation container
        self.nav_frame = ttk.Frame(self)
        self.nav_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=15)
        
        self.btn_back = ttk.Button(self.nav_frame, text="< Back", command=self.prev_step)
        self.btn_back.pack(side=tk.LEFT)
        
        self.btn_next = ttk.Button(self.nav_frame, text="Next >", command=self.next_step)
        self.btn_next.pack(side=tk.RIGHT)
        
        self.btn_cancel = ttk.Button(self.nav_frame, text="Cancel", command=self.destroy)
        self.btn_cancel.pack(side=tk.RIGHT, padx=10)

        # Step 0: Welcome Frame
        f0 = ttk.Frame(self)
        ttk.Label(f0, text="Welcome to AquaPulse Vision Telemetry", style='Header.TLabel').pack(anchor='w', pady=(20, 5))
        ttk.Label(f0, text="AI Marine Object Tracking & Neural Vision Suite", style='SubHeader.TLabel').pack(anchor='w', pady=(0, 20))
        
        desc = (
            "This setup wizard will install AquaPulse Vision Telemetry on your computer.\n\n"
            "Features included in this package:\n"
            " • PyTorch & Ultralytics YOLO Neural Vision Engine\n"
            " • Real-time Underwater Marine Tracking & HUD\n"
            " • Ollama LLM Interactive Persona System (Llama3 Model)\n"
            " • Multilingual Voice Telemetry & Dynamic Screen Adapter\n\n"
            "Click Next to choose the installation folder and install prerequisites automatically."
        )
        ttk.Label(f0, text=desc, wraplength=580, justify='left').pack(anchor='w', pady=10)
        self.frames.append(f0)

        # Step 1: Destination Selection
        f1 = ttk.Frame(self)
        ttk.Label(f1, text="Select Installation Folder", style='Header.TLabel').pack(anchor='w', pady=(20, 5))
        ttk.Label(f1, text="Choose where you would like to install AquaPulse Vision.", style='SubHeader.TLabel').pack(anchor='w', pady=(0, 20))
        
        dir_box = ttk.Frame(f1)
        dir_box.pack(fill=tk.X, pady=10)
        
        self.entry_dir = ttk.Entry(dir_box, textvariable=self.dest_dir, font=('Segoe UI', 10))
        self.entry_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        btn_browse = ttk.Button(dir_box, text="Browse...", command=self.browse_folder)
        btn_browse.pack(side=tk.RIGHT)
        
        cb_desk = ttk.Checkbutton(f1, text="Create Desktop Shortcut", variable=self.create_desktop_shortcut)
        cb_desk.pack(anchor='w', pady=15)
        
        self.frames.append(f1)

        # Step 2: Installation Progress
        f2 = ttk.Frame(self)
        ttk.Label(f2, text="Installing AquaPulse Vision & Prerequisites...", style='Header.TLabel').pack(anchor='w', pady=(20, 5))
        ttk.Label(f2, text="Please wait while files and AI models are configured.", style='SubHeader.TLabel').pack(anchor='w', pady=(0, 15))
        
        self.lbl_status = ttk.Label(f2, text="Preparing setup...", font=('Segoe UI', 10, 'italic'))
        self.lbl_status.pack(anchor='w', pady=(10, 5))
        
        self.progress = ttk.Progressbar(f2, mode='determinate', length=580)
        self.progress.pack(fill=tk.X, pady=10)
        
        self.txt_log = tk.Text(f2, height=10, bg="#020617", fg="#38bdf8", font=('Consolas', 9), insertbackground="#ffffff")
        self.txt_log.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.frames.append(f2)

        # Step 3: Finish Screen
        f3 = ttk.Frame(self)
        ttk.Label(f3, text="Installation Complete!", style='Header.TLabel').pack(anchor='w', pady=(20, 5))
        ttk.Label(f3, text="AquaPulse Vision Telemetry has been successfully installed.", style='SubHeader.TLabel').pack(anchor='w', pady=(0, 20))
        
        cb_launch = ttk.Checkbutton(f3, text="Launch AquaPulse Vision Telemetry now", variable=self.launch_app_on_finish)
        cb_launch.pack(anchor='w', pady=20)
        
        self.frames.append(f3)

    def log(self, text):
        def _update():
            self.txt_log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {text}\n")
            self.txt_log.see(tk.END)
        self.after(0, _update)

    def set_status(self, text, percent=None):
        def _update():
            self.lbl_status.config(text=text)
            if percent is not None:
                self.progress['value'] = percent
        self.after(0, _update)

    def browse_folder(self):
        chosen = filedialog.askdirectory(initialdir=self.dest_dir.get())
        if chosen:
            self.dest_dir.set(os.path.abspath(chosen))

    def show_step(self, step_idx):
        for f in self.frames:
            f.pack_forget()
            
        self.current_step = step_idx
        self.frames[step_idx].pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.btn_back.config(state=tk.NORMAL if step_idx in (1, 3) else tk.DISABLED)
        
        if step_idx == 2:
            self.btn_back.config(state=tk.DISABLED)
            self.btn_next.config(state=tk.DISABLED)
            self.btn_cancel.config(state=tk.DISABLED)
            threading.Thread(target=self.run_installation, daemon=True).start()
        elif step_idx == 3:
            self.btn_next.config(text="Finish", command=self.finish_installation)
            self.btn_cancel.pack_forget()
        else:
            self.btn_next.config(text="Next >", command=self.next_step)

    def next_step(self):
        if self.current_step < len(self.frames) - 1:
            self.show_step(self.current_step + 1)

    def prev_step(self):
        if self.current_step > 0 and self.current_step != 2:
            self.show_step(self.current_step - 1)

    def check_and_setup_ollama(self):
        self.set_status("Checking Ollama installation...", 50)
        self.log("Searching for Ollama engine on system...")
        
        ollama_found = shutil.which("ollama") is not None
        if not ollama_found:
            local_ollama = os.path.expandvars("%LOCALAPPDATA%\\Programs\\Ollama\\ollama.exe")
            if os.path.exists(local_ollama):
                ollama_found = True
                
        if not ollama_found:
            self.log("Ollama engine not detected. Downloading official OllamaSetup.exe...")
            setup_url = "https://ollama.com/download/OllamaSetup.exe"
            temp_installer = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "OllamaSetup.exe")
            try:
                urllib.request.urlretrieve(setup_url, temp_installer)
                self.log("Downloaded OllamaSetup.exe. Launching installer...")
                proc = subprocess.Popen([temp_installer, "/silent"])
                proc.wait()
                self.log("Ollama installation completed.")
            except Exception as e:
                self.log(f"⚠️ Automatic Ollama download warning: {e}")
        else:
            self.log("✅ Ollama engine is already installed.")

        self.set_status("Verifying Llama3 LLM model...", 75)
        self.log("Pulling required 'llama3' model for AI Persona...")
        try:
            p = subprocess.run(["ollama", "pull", "llama3"], capture_output=True, text=True, timeout=300)
            if p.returncode == 0:
                self.log("✅ Llama3 AI model verified and ready.")
            else:
                self.log(f"Notice: Ollama pull output: {p.stdout or p.stderr}")
        except Exception as e:
            self.log(f"⚠️ Ollama model pull notice: {e}")

    def create_shortcut(self, target_path, shortcut_path):
        try:
            ps_script = f'$s=(New-Object -COM WScript.Shell).CreateShortcut("{shortcut_path}"); $s.TargetPath="{target_path}"; $s.Save()'
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
            self.log(f"Created shortcut: {shortcut_path}")
        except Exception as e:
            self.log(f"Shortcut creation notice: {e}")

    def run_installation(self):
        target = os.path.abspath(self.dest_dir.get())
        self.set_status("Creating target installation folder...", 10)
        self.log(f"Target directory: {target}")
        os.makedirs(target, exist_ok=True)

        # Base path for bundle assets
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        payload_zip = os.path.join(base_path, "payload.zip")

        if os.path.exists(payload_zip):
            self.set_status("Extracting AquaPulse application files...", 30)
            self.log("Unpacking core binaries, neural weights, and OpenCV runtime...")
            with zipfile.ZipFile(payload_zip, 'r') as zip_ref:
                zip_ref.extractall(target)
            self.log("✅ Application files extracted successfully.")
        else:
            self.log("Copying development files to target...")
            # Fallback for dev mode
            src_dir = r"C:\Users\parsa\Desktop\Code\3 - AI process\Vision transfromers"
            for item in os.listdir(src_dir):
                if item not in ("__pycache__", ".gradio", "ollama.log"):
                    s = os.path.join(src_dir, item)
                    d = os.path.join(target, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy(s, d)

        # Check and install Ollama prerequisites
        self.check_and_setup_ollama()

        # Create Shortcuts
        if self.create_desktop_shortcut.get():
            self.set_status("Creating Desktop shortcut...", 90)
            desk_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")
            exe_path = os.path.join(target, "AquaPulseVision.exe")
            if not os.path.exists(exe_path):
                # Fallback to python runner batch if exe not compiled standalone
                exe_path = os.path.join(target, "run_app.bat")
                with open(exe_path, "w") as f:
                    f.write('@echo off\ncd /d "%~dp0"\nstart "" python main.py %*\n')
            self.create_shortcut(exe_path, os.path.join(desk_dir, "AquaPulse Vision Telemetry.lnk"))

        self.set_status("Installation complete!", 100)
        self.log("🎉 All setup tasks completed successfully.")
        
        self.after(1000, lambda: self.show_step(3))

    def finish_installation(self):
        if self.launch_app_on_finish.get():
            target = os.path.abspath(self.dest_dir.get())
            exe_path = os.path.join(target, "AquaPulseVision.exe")
            if not os.path.exists(exe_path):
                exe_path = os.path.join(target, "run_app.bat")
            if os.path.exists(exe_path):
                subprocess.Popen([exe_path], cwd=target)
        self.destroy()

if __name__ == "__main__":
    app = AquaPulseSetupWizard()
    app.mainloop()
