import os
import sys
import time
import argparse
import threading
import re
import cv2
import torch
import numpy as np
from collections import deque, defaultdict

# --- IMPORT DISCIPLINED NUMBERED MODULES ---
import mod_00_config_and_assets as cfg
import mod_01_eco_census as census
import mod_02_stochastic_enkf as enkf
import mod_03_chart_renderer as chart
import mod_04_vision_engine as vision
import mod_05_dialogue_and_ollama as comm
import mod_06_ui_dashboard as ui
import manual_botsort as botsort

# --- VIDEO FILE PICKER DIALOG ---
def select_video_file_dialog():
    """Opens a native modal dialog window allowing the user to pick a video file or launch default sample."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        result_path = {"path": None}
        
        root = tk.Tk()
        root.title("AquaPulse AI Vision - Select Video Source")
        root.geometry("540x260")
        root.resizable(False, False)
        root.attributes('-topmost', True)
        
        # Center window on screen
        root.update_idletasks()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = (screen_w - 540) // 2
        y = (screen_h - 260) // 2
        root.geometry(f"540x260+{x}+{y}")
        root.lift()
        root.focus_force()
        root.attributes('-topmost', True)
        root.after(100, lambda: root.attributes('-topmost', False))
        
        bg_color = "#1e222d"
        card_bg = "#2a2e3d"
        
        root.configure(bg=bg_color)
        
        header_frame = tk.Frame(root, bg=bg_color)
        header_frame.pack(fill="x", padx=20, pady=(15, 5))
        
        title_label = tk.Label(header_frame, text="🌊 AquaPulse AI Neural Vision", font=("Segoe UI", 16, "bold"), fg="#38bdf8", bg=bg_color)
        title_label.pack(anchor="w")
        
        sub_label = tk.Label(header_frame, text="Select an underwater video file for real-time tracking & data assimilation", font=("Segoe UI", 9), fg="#94a3b8", bg=bg_color)
        sub_label.pack(anchor="w", pady=(2, 0))
        
        card = tk.Frame(root, bg=card_bg, highlightbackground="#3b4252", highlightthickness=1)
        card.pack(fill="both", expand=True, padx=20, pady=10)
        
        selected_lbl = tk.Label(card, text="Please select a video file to begin telemetry analysis", font=("Segoe UI", 10), fg="#cbd5e1", bg=card_bg)
        selected_lbl.pack(pady=12)
        
        def browse_file():
            filepath = filedialog.askopenfilename(
                parent=root,
                title="Select Video File for AquaPulse Neural Tracking",
                filetypes=[
                    ("Video Files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
                    ("All Files", "*.*")
                ]
            )
            if filepath and os.path.exists(filepath):
                result_path["path"] = filepath
                selected_lbl.config(text=f"Selected: {os.path.basename(filepath)}", font=("Segoe UI", 10, "bold"), fg="#4ade80")
                root.after(300, root.destroy)

        def use_default():
            result_path["path"] = "DEFAULT"
            root.destroy()

        btn_frame = tk.Frame(card, bg=card_bg)
        btn_frame.pack(pady=5)
        
        browse_btn = tk.Button(
            btn_frame, text="📁 Browse Video File...", font=("Segoe UI", 10, "bold"),
            bg="#0284c7", fg="white", activebackground="#0369a1", activeforeground="white",
            relief="flat", padx=15, pady=6, cursor="hand2", command=browse_file
        )
        browse_btn.pack(side="left", padx=10)
        
        default_btn = tk.Button(
            btn_frame, text="🌊 Use Sample Video", font=("Segoe UI", 10),
            bg="#334155", fg="white", activebackground="#475569", activeforeground="white",
            relief="flat", padx=15, pady=6, cursor="hand2", command=use_default
        )
        default_btn.pack(side="left", padx=10)
        
        root.mainloop()
        
        if result_path["path"] and result_path["path"] != "DEFAULT" and os.path.exists(result_path["path"]):
            return result_path["path"]
    except Exception as e:
        print(f"Notice: Video selection dialog notice ({e}).")
    return None

# --- PARSE INPUT VIDEO & RUNTIME OPTIONS ---
parser = argparse.ArgumentParser(description="AquaPulse Neural Vision & EnKF Data Assimilation")
parser.add_argument("video_pos", nargs="?", default=None, help="Path to input video file")
parser.add_argument("--video", "-v", type=str, default=None, help="Path to input video file")
parser.add_argument("--headless", action="store_true", help="Run without opening OpenCV GUI window (ideal for Docker / headless servers)")
args, _ = parser.parse_known_args()

# Determine headless runtime mode (only check DISPLAY on non-Windows platforms)
if sys.platform == "win32":
    is_headless = args.headless or os.environ.get("HEADLESS", "0") == "1"
else:
    is_headless = args.headless or os.environ.get("HEADLESS", "0") == "1" or not os.environ.get("DISPLAY")

video_path = args.video or args.video_pos

if video_path:
    cleaned_arg = video_path.strip("'\"")
    if not os.path.isabs(cleaned_arg):
        cleaned_arg = os.path.abspath(os.path.join(os.getcwd(), cleaned_arg))
    if os.path.exists(cleaned_arg):
        video_path = cleaned_arg

if not video_path and not is_headless:
    video_path = select_video_file_dialog()

if not video_path:
    for f in os.listdir(cfg.script_dir):
        if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            video_path = os.path.join(cfg.script_dir, f)
            break

if not video_path:
    video_path = cfg.find_asset("main.mp4")

print(f"🎬 Active video source: {video_path}")

# --- INITIALIZE HARDWARE & MULTI-MODEL YOLO ENSEMBLE ---
device_target, device_desc = cfg.detect_device_hardware()
print(f"⚡ System Hardware Acceleration: {device_desc}")

ensemble_models, model = vision.load_ensemble_models(device_target)
hw_telemetry_status = cfg.get_hardware_status_summary(device_target, device_desc)

# --- VIDEO CAPTURE & CANVASES ---
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"❌ Error: Cannot open video source: {video_path}")
    sys.exit(1)

fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0 or np.isnan(fps):
    fps = 30.0

total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
repeat_infinitely = False  # Disabled auto-repeat for short videos

# Fixed Initial 4-Pane Dimensions
left_panel_w = 380
right_panel_w = 380
tools_panel_h = 340

video_w = 840
video_h = 580

canvas_w = left_panel_w + video_w + right_panel_w  # 1600
canvas_h = video_h + tools_panel_h                 # 920

window_name = "AquaPulse Vision Dashboard - San Francisco Light Mode"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, canvas_w, canvas_h)

# --- PROMPT USER ON THE SCREEN FOR DATA ASSIMILATION & SESSION SAVING ---
save_analysis_enabled = ui.display_on_screen_data_assimilation_prompt(window_name, canvas_w, canvas_h, video_path)

if save_analysis_enabled:
    session_info = cfg.create_unique_video_session_dir(video_path)
    output_path = session_info["output_video_path"]
    print(f"📁 Unique Session Folder Created: {session_info['session_dir']}")
else:
    session_info = None
    output_dir = os.path.join(cfg.script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "tracked_output.mp4")

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (canvas_w, canvas_h))

# Initialize EnKF Filter & RealTime Chart Renderer
enkf_filter = enkf.EnsembleKalmanFilter(num_members=50, R_noise=4.0)
chart_renderer = chart.RealTimeChartRenderer(width=360, height=230, update_interval=15)

# --- INTERACTIVE PANEL RESIZING SPLITTER DIVIDERS STATE ---
dragging_divider = None  # None, 'v1', 'v2', 'h1'
hovered_divider = None   # None, 'v1', 'v2', 'h1'

locked_target = None
locked_target_id = None
mouse_pos = (0, 0)
action_trigger = None

def on_mouse_event(event, x, y, flags, param):
    global locked_target, locked_target_id, mouse_pos, action_trigger
    global left_panel_w, right_panel_w, video_w, video_h, tools_panel_h
    global dragging_divider, hovered_divider

    mouse_pos = (x, y)
    divider_tol = 8

    v1_x = left_panel_w
    v2_x = left_panel_w + video_w
    h1_y = video_h

    # 1. Hover Detection
    if abs(x - v1_x) <= divider_tol:
        hovered_divider = 'v1'
    elif abs(x - v2_x) <= divider_tol:
        hovered_divider = 'v2'
    elif v1_x <= x <= v2_x and abs(y - h1_y) <= divider_tol:
        hovered_divider = 'h1'
    else:
        hovered_divider = None

    # 2. Mouse Press (Start Dragging Divider or Click Button/Fish)
    if event == cv2.EVENT_LBUTTONDOWN:
        if hovered_divider is not None:
            dragging_divider = hovered_divider
            return

        buttons = param.get('buttons', [])
        for btn in buttons:
            if btn.contains(x, y):
                action_trigger = btn.callback_id
                comm.play_sound_async(1000, 100)
                return

        left_offset = left_panel_w
        if left_offset <= x <= left_offset + video_w and y <= video_h:
            vid_x = x - left_offset
            current_targets = param.get('current_targets', [])
            clicked_any = False
            for target in current_targets:
                bx1, by1, bx2, by2 = map(int, target['box'])
                if bx1 <= vid_x <= bx2 and by1 <= y <= by2:
                    locked_target = target
                    locked_target_id = target['id']
                    clicked_any = True
                    ui.hud_notifs.add(f"🔒 TARGET LOCKED #{target['id']}: {target['species']}", (255, 122, 0), 3.0)
                    threading.Thread(target=comm.fetch_gbif_species_image, args=(target['species'],), daemon=True).start()
                    break
            if not clicked_any:
                locked_target = None
                locked_target_id = None
                ui.hud_notifs.add("🔓 TARGET UNLOCKED", (142, 142, 147), 2.0)

    # 3. Mouse Dragging (Resize Panel Dividers)
    elif event == cv2.EVENT_MOUSEMOVE:
        if dragging_divider == 'v1':
            left_panel_w = max(240, min(550, x))
            video_w = max(400, canvas_w - left_panel_w - right_panel_w)
        elif dragging_divider == 'v2':
            right_panel_w = max(240, min(550, canvas_w - x))
            video_w = max(400, canvas_w - left_panel_w - right_panel_w)
        elif dragging_divider == 'h1':
            video_h = max(300, min(canvas_h - 150, y))
            tools_panel_h = canvas_h - video_h

    # 4. Mouse Release (Stop Dragging Divider)
    elif event == cv2.EVENT_LBUTTONUP:
        dragging_divider = None

# Display 5-second dynamic loading screen
ui.display_dynamic_loading_screen(window_name, canvas_w, canvas_h, model_name=os.path.basename(ensemble_models[0][0]), duration=5.0)

# Filter Controls & Vision Options
current_fx_idx = 0
vision_fx_names = ["NORMAL", "THERMAL", "NIGHT VISION", "SONAR EDGE", "CLAHE"]

selectable_filters = ["ALL TARGETS", "FISH ONLY", "DIVERS & OCTOPUS"]
model_classes = getattr(model, 'names', {})
if isinstance(model_classes, dict):
    for cls_name in sorted(model_classes.values()):
        if cls_name not in selectable_filters:
            selectable_filters.append(cls_name)

current_filter_idx = 0
show_motion_vectors = True
show_pip_zoom = True
use_adaptive_clahe = True
show_stats_analyzer = False
conf_threshold = 0.35
active_tracker_cfg = "botsort.yaml"
iou_threshold = 0.5

is_paused = False
is_stopped = False
seek_request = 0
loop_counter = 0

processed_frames = set()
registered_session_track_ids = set()
species_unique_ids = defaultdict(set)
smoothed_boxes = {}
saved_specimen_ids = set()
saved_species_crops = set()
saved_species_conf = {}

chat_mode_active = False
user_chat_buffer = ""

species_color_map = {
    "Salmo trutta": (255, 122, 0),
    "Gadus morhua": (89, 199, 52),
    "Oncorhynchus mykiss": (0, 149, 255),
    "Thunnus thynnus": (222, 82, 175)
}

recent_gbif_species = deque(maxlen=4)
track_history = defaultdict(lambda: deque(maxlen=30))

mouse_cb_param = {'buttons': [], 'hud_notifs': ui.hud_notifs, 'video_w': video_w, 'current_targets': []}
cv2.setMouseCallback(window_name, on_mouse_event, param=mouse_cb_param)

show_water_gif = False
prev_time = time.time()
fps_smooth = 0.0
frame_counter = 0

# --- MAIN TRACKING & RENDER LOOP ---
while cap.isOpened():
    if is_paused or is_stopped:
        if 'raw_frame_full' not in locals() or raw_frame_full is None:
            success, raw_frame_full = cap.read()
        else:
            success = True
    else:
        if seek_request != 0:
            curr_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            target_pos = max(0, min(max(0, total_video_frames - 1), curr_pos + seek_request))
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_pos)
            seek_request = 0

        success, raw_frame_full = cap.read()

        if not success:
            if repeat_infinitely and not is_stopped:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                loop_counter += 1
                ui.hud_notifs.add(f"🔄 REPEAT MODE (Pass #{loop_counter + 1})", (255, 122, 0), 2.5)
                success, raw_frame_full = cap.read()
            else:
                is_stopped = True
                success = ('raw_frame_full' in locals() and raw_frame_full is not None)

    if not success or raw_frame_full is None:
        break

    curr_frame_idx = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    is_first_frame_visit = (curr_frame_idx not in processed_frames)
    if is_first_frame_visit:
        processed_frames.add(curr_frame_idx)

    frame_counter += 1
    t_curr = time.time()
    dt = t_curr - prev_time
    prev_time = t_curr
    if dt > 0:
        fps_smooth = 0.9 * fps_smooth + 0.1 * (1.0 / dt)

    frame = cv2.resize(raw_frame_full, (video_w, video_h))

    if show_water_gif:
        water_bg = vision.generate_water_gif_frame(video_h, video_w, time.time())
        frame = cv2.addWeighted(frame, 0.85, water_bg, 0.15, 0)

    inference_input = vision.adaptive_underwater_enhance(frame) if use_adaptive_clahe else frame

    # YOLO Multi-Algorithm Persistent Tracking (BoT-SORT / ByteTrack @ 640x640)
    if not (is_paused or is_stopped) or 'results' not in locals():
        try:
            results = model.track(
                inference_input,
                persist=True,
                tracker=active_tracker_cfg,
                iou=iou_threshold,
                device=device_target,
                conf=conf_threshold,
                imgsz=640,
                verbose=False
            )
        except Exception:
            results = model.track(
                inference_input,
                persist=True,
                tracker=active_tracker_cfg,
                iou=iou_threshold,
                device="cpu",
                conf=conf_threshold,
                imgsz=640,
                verbose=False
            )

    current_targets = []
    best_target_crop = None
    best_target_info = None

    if results and len(results) > 0 and results[0].boxes is not None and results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        track_ids = results[0].boxes.id.cpu().numpy().astype(int)
        clss = results[0].boxes.cls.cpu().numpy().astype(int)
        confs = results[0].boxes.conf.cpu().numpy()

        for box, tid, cls_idx, conf_val in zip(boxes, track_ids, clss, confs):
            sp_name = model.names.get(cls_idx, f"Specimen_{cls_idx}")
            
            active_filter = selectable_filters[current_filter_idx]
            if active_filter == "FISH ONLY" and "fish" not in sp_name.lower():
                continue
            elif active_filter == "DIVERS & OCTOPUS" and not any(k in sp_name.lower() for k in ["diver", "octopus", "squid"]):
                continue
            elif active_filter not in ["ALL TARGETS", "FISH ONLY", "DIVERS & OCTOPUS"] and sp_name != active_filter:
                continue

            if tid in smoothed_boxes:
                smoothed_boxes[tid] = 0.65 * smoothed_boxes[tid] + 0.35 * box
            else:
                smoothed_boxes[tid] = box
            smooth_b = smoothed_boxes[tid]

            bx1, by1, bx2, by2 = map(int, smooth_b)
            center_x, center_y = (bx1 + bx2) // 2, (by1 + by2) // 2
            track_history[tid].append((center_x, center_y))

            if is_first_frame_visit and tid not in registered_session_track_ids:
                registered_session_track_ids.add(tid)
                species_unique_ids[sp_name].add(tid)
                census.update_species_census(sp_name, tid)

            if session_info is not None and "fish_images_dir" in session_info:
                clean_sp = re.sub(r'[^\w\s-]', '', sp_name).strip().replace(' ', '_')
                if not clean_sp:
                    clean_sp = "Fish"
                if clean_sp not in saved_species_crops or conf_val > saved_species_conf.get(clean_sp, 0.0):
                    cx1, cy1 = max(0, bx1), max(0, by1)
                    cx2, cy2 = min(video_w, bx2), min(video_h, by2)
                    if cx2 > cx1 and cy2 > cy1:
                        crop_img = frame[cy1:cy2, cx1:cx2]
                        img_fname = f"{clean_sp}.png"
                        img_fpath = os.path.join(session_info["fish_images_dir"], img_fname)
                        cv2.imwrite(img_fpath, crop_img)
                        saved_species_crops.add(clean_sp)
                        saved_species_conf[clean_sp] = conf_val

            if sp_name not in recent_gbif_species:
                recent_gbif_species.append(sp_name)
                threading.Thread(target=comm.fetch_gbif_species_image, args=(sp_name,), daemon=True).start()

            sp_color = species_color_map.get(sp_name, (255, 122, 0))
            is_this_locked = (locked_target_id == tid)
            
            target_obj = {
                'id': tid,
                'box': smooth_b,
                'species': sp_name,
                'conf': conf_val,
                'color': sp_color
            }
            current_targets.append(target_obj)
            if is_this_locked:
                locked_target = target_obj

            if best_target_info is None or conf_val > best_target_info[1]:
                best_target_info = (tid, conf_val, sp_name)
                crop_x1, crop_y1 = max(0, bx1), max(0, by1)
                crop_x2, crop_y2 = min(video_w, bx2), min(video_h, by2)
                if crop_x2 > crop_x1 and crop_y2 > crop_y1:
                    best_target_crop = frame[crop_y1:crop_y2, crop_x1:crop_x2]

            vision.draw_target_box(frame, smooth_b, tid, sp_name, conf_val, custom_color=sp_color, is_selected=is_this_locked)

            if show_motion_vectors and len(track_history[tid]) > 1:
                pts = np.array(track_history[tid], np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], False, sp_color, 1, cv2.LINE_AA)

    if is_first_frame_visit:
        prey_cnt = len(current_targets)
        enkf_filter.step(live_yolo_prey_count=prey_cnt)

    current_fx = vision_fx_names[current_fx_idx]
    if current_fx == "THERMAL":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    elif current_fx == "NIGHT VISION":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        green = np.zeros_like(frame)
        green[:, :, 1] = gray
        frame = cv2.addWeighted(frame, 0.2, green, 0.8, 0)
    elif current_fx == "SONAR EDGE":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    if show_pip_zoom:
        zoom_target_box = locked_target['box'] if locked_target else (current_targets[0]['box'] if current_targets else None)
        if zoom_target_box is not None:
            zx1, zy1, zx2, zy2 = map(int, zoom_target_box)
            zx1, zy1 = max(0, zx1), max(0, zy1)
            zx2, zy2 = min(video_w, zx2), min(video_h, zy2)
            if zx2 > zx1 and zy2 > zy1:
                crop = frame[zy1:zy2, zx1:zx2]
                pip_size = 130
                res_crop = cv2.resize(crop, (pip_size, pip_size))
                
                px, py = video_w - pip_size - 15, 15
                frame[py:py+pip_size, px:px+pip_size] = res_crop
                cv2.rectangle(frame, (px, py), (px+pip_size, py+pip_size), (255, 122, 0), 2)
                cv2.putText(frame, "MAGNIFIER PiP", (px + 5, py + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (255, 122, 0), 1)

    ui.hud_notifs.draw(frame)

    # MASTER 4-PANE CANVAS TILING
    canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
    canvas[:] = (247, 245, 245)

    # PANE 2: MAIN VIEWPORT
    pane2_x = left_panel_w
    canvas[0:video_h, pane2_x:pane2_x+video_w] = frame
    cv2.rectangle(canvas, (pane2_x, 0), (pane2_x + video_w, video_h), (229, 235, 234), 2)

    # PANE 1: ECOLOGICAL ANALYSIS
    pane1 = canvas[0:canvas_h, 0:left_panel_w]
    pane1[:] = (255, 255, 255)
    cv2.rectangle(pane1, (2, 2), (left_panel_w - 2, canvas_h - 2), (229, 235, 234), 1)

    p1_y = 12
    cv2.rectangle(pane1, (10, p1_y), (left_panel_w - 10, p1_y + 36), (242, 242, 247), -1)
    cv2.rectangle(pane1, (10, p1_y), (left_panel_w - 10, p1_y + 36), (255, 122, 0), 1)
    cv2.putText(pane1, "PANE 1: ECOLOGICAL ANALYSIS", (16, p1_y + 23),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 122, 0), 1, cv2.LINE_AA)
    p1_y += 46

    cv2.rectangle(pane1, (10, p1_y), (left_panel_w - 10, p1_y + 110), (250, 250, 252), -1)
    cv2.rectangle(pane1, (10, p1_y), (left_panel_w - 10, p1_y + 110), (204, 199, 199), 1)
    
    cv2.putText(pane1, "EULER-MARUYAMA EnKF ESTIMATIONS", (18, p1_y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 122, 0), 1, cv2.LINE_AA)
    
    est_prey = enkf_filter.x[0, 0]
    est_pred = enkf_filter.x[1, 0]
    risk_pct = enkf_filter.risk_history[-1] if enkf_filter.risk_history else 0.0
    
    cv2.putText(pane1, f"Prey Pop (X): {est_prey:.2f} | Pred (Y): {est_pred:.2f}",
                (18, p1_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (31, 29, 29), 1)
    
    risk_color = (48, 59, 255) if risk_pct > 35 else ((0, 149, 255) if risk_pct >= 15 else (89, 199, 52))
    cv2.putText(pane1, f"Extinction Risk: {risk_pct:.1f}%", (18, p1_y + 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, risk_color, 1, cv2.LINE_AA)
    
    risk_bar_w = int((left_panel_w - 36) * (min(100.0, risk_pct) / 100.0))
    cv2.rectangle(pane1, (18, p1_y + 75), (left_panel_w - 18, p1_y + 88), (235, 233, 233), -1)
    cv2.rectangle(pane1, (18, p1_y + 75), (left_panel_w - 18, p1_y + 88), (204, 199, 199), 1)
    if risk_bar_w > 0:
        cv2.rectangle(pane1, (18, p1_y + 75), (18 + risk_bar_w, p1_y + 88), risk_color, -1)
    p1_y += 122

    cv2.rectangle(pane1, (10, p1_y), (left_panel_w - 10, p1_y + 115), (250, 250, 252), -1)
    cv2.rectangle(pane1, (10, p1_y), (left_panel_w - 10, p1_y + 115), (204, 199, 199), 1)
    
    census_summary = census.get_census_summary()
    cv2.putText(pane1, "TOP 4 SPECIES CENSUS COUNTS", (18, p1_y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 122, 0), 1, cv2.LINE_AA)
    
    top_4_species = census_summary.get("top_4", [])
    if top_4_species:
        for idx, (sp_name, count) in enumerate(top_4_species[:4]):
            sp_line = vision.fit_text_to_width(f"{idx+1}. {sp_name}: {count} unique", max_pixel_width=left_panel_w - 40)
            cv2.putText(pane1, sp_line, (18, p1_y + 42 + idx*18), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (31, 29, 29), 1)
    else:
        cv2.putText(pane1, "Scanning for species census data...", (18, p1_y + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (142, 142, 147), 1)
    p1_y += 128

    cv2.rectangle(pane1, (10, p1_y), (left_panel_w - 10, canvas_h - 10), (250, 250, 252), -1)
    cv2.rectangle(pane1, (10, p1_y), (left_panel_w - 10, canvas_h - 10), (204, 199, 199), 1)
    
    chart_h = canvas_h - p1_y - 20
    chart_renderer.height = chart_h
    chart_renderer.width = left_panel_w - 24
    
    chart_img = chart_renderer.render(enkf_filter, mode=1 if show_stats_analyzer else 0, census_summary=census_summary)
    if chart_img is not None and chart_img.shape[0] == chart_h and chart_img.shape[1] == (left_panel_w - 24):
        pane1[p1_y+10:p1_y+10+chart_h, 12:left_panel_w-12] = chart_img

    # PANE 3: CONTROLS DOCK
    pane3_x = left_panel_w
    pane3_y = video_h
    pane3_w = video_w
    pane3_h = tools_panel_h

    pane3 = canvas[pane3_y:pane3_y+pane3_h, pane3_x:pane3_x+pane3_w]
    pane3[:] = (255, 255, 255)
    cv2.rectangle(pane3, (2, 2), (pane3_w - 2, pane3_h - 2), (229, 235, 234), 1)

    cv2.putText(pane3, "PANE 3: CONTROL PANEL & TOOLS", (15, 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 122, 0), 1, cv2.LINE_AA)

    btn_start_y = pane3_y + 35
    btn_w = max(90, (video_w - 50) // 3)

    play_btn_lbl = "[SPACE] PLAY / PAUSE"
    repeat_btn_lbl = "[R] LOOP: ON" if repeat_infinitely else "[R] LOOP: OFF"

    buttons = [
        ui.ControlButton(pane3_x + 15, btn_start_y, btn_w, 30, f"[S] FILTER: {selectable_filters[current_filter_idx]}", "toggle_filter", (255, 122, 0)),
        ui.ControlButton(pane3_x + 25 + btn_w, btn_start_y, btn_w, 30, f"[F] FX: {vision_fx_names[current_fx_idx]}", "toggle_fx", (222, 82, 175)),
        ui.ControlButton(pane3_x + 35 + 2*btn_w, btn_start_y, btn_w, 30, f"[V] VECTORS: {'ON' if show_motion_vectors else 'OFF'}", "toggle_vec", (89, 199, 52)),

        ui.ControlButton(pane3_x + 15, btn_start_y + 38, btn_w, 30, play_btn_lbl, "toggle_pause", (255, 122, 0)),
        ui.ControlButton(pane3_x + 25 + btn_w, btn_start_y + 38, btn_w, 30, "[<-] -10s SEEK", "seek_back", (89, 199, 52)),
        ui.ControlButton(pane3_x + 35 + 2*btn_w, btn_start_y + 38, btn_w, 30, "[->] +10s SEEK", "seek_fwd", (89, 199, 52)),

        ui.ControlButton(pane3_x + 15, btn_start_y + 76, btn_w, 30, repeat_btn_lbl, "toggle_repeat", (0, 149, 255)),
        ui.ControlButton(pane3_x + 25 + btn_w, btn_start_y + 76, btn_w, 30, "[X] STOP", "stop_video", (48, 59, 255)),
        ui.ControlButton(pane3_x + 35 + 2*btn_w, btn_start_y + 76, btn_w, 30, f"[L] LANG: {comm.language_mode}", "toggle_lang", (255, 122, 0)),

        ui.ControlButton(pane3_x + 15, btn_start_y + 114, btn_w, 30, f"[A] CLAHE: {'ON' if use_adaptive_clahe else 'OFF'}", "toggle_clahe", (89, 199, 52)),
        ui.ControlButton(pane3_x + 25 + btn_w, btn_start_y + 114, btn_w, 30, f"[W] WATER LAYER: {'ON' if show_water_gif else 'OFF'}", "toggle_gif", (255, 122, 0)),
        ui.ControlButton(pane3_x + 35 + 2*btn_w, btn_start_y + 114, btn_w, 30, f"[M] STATS: {'ON' if show_stats_analyzer else 'OFF'}", "toggle_stats", (222, 82, 175)),

        ui.ControlButton(pane3_x + 15, btn_start_y + 152, btn_w, 32, f"[T] TRACKER: {'BOTSORT' if 'botsort' in active_tracker_cfg else 'BYTETRACK'}", "toggle_tracker", (0, 149, 255)),
        ui.ControlButton(pane3_x + 25 + btn_w, btn_start_y + 152, btn_w, 32, "[C] DR. PAULY", "call_pauly", (89, 199, 52)),
        ui.ControlButton(pane3_x + 35 + 2*btn_w, btn_start_y + 152, btn_w, 32, "[J] JOHNNY RELIC", "trigger_johnny", (222, 82, 175)),
        ui.ControlButton(pane3_x + 15, btn_start_y + 190, video_w - 30, 32, "💬 [TAB / CTRL+T / CTRL+C] OPEN LIVE CHAT PORTAL", "trigger_chat", (255, 122, 0))
    ]

    mouse_cb_param['buttons'] = buttons
    mouse_cb_param['current_targets'] = current_targets
    for btn in buttons:
        btn.draw(canvas, is_hovered=btn.contains(mouse_pos[0], mouse_pos[1]))

    # PANE 4: COMM & CHAT
    pane4_x = left_panel_w + video_w
    pane4 = canvas[0:canvas_h, pane4_x:canvas_w]
    pane4[:] = (255, 255, 255)

    cv2.rectangle(pane4, (2, 2), (right_panel_w - 2, canvas_h - 2), (229, 235, 234), 1)

    p4_y = 12
    cv2.rectangle(pane4, (10, p4_y), (right_panel_w - 10, p4_y + 36), (242, 242, 247), -1)
    cv2.rectangle(pane4, (10, p4_y), (right_panel_w - 10, p4_y + 36), (255, 122, 0), 1)
    cv2.putText(pane4, "PANE 4: AI RESEARCH & FIELD NOTES", (16, p4_y + 23),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 122, 0), 1, cv2.LINE_AA)
    p4_y += 46

    cv2.rectangle(pane4, (10, p4_y), (right_panel_w - 10, p4_y + 90), (250, 250, 252), -1)
    cv2.rectangle(pane4, (10, p4_y), (right_panel_w - 10, p4_y + 90), (204, 199, 199), 1)

    c_s_val = int(cap.get(cv2.CAP_PROP_POS_FRAMES) / float(fps)) if fps > 0 else 0
    tot_s_val = int(total_video_frames / float(fps)) if fps > 0 else 0
    c_m, c_s = divmod(c_s_val, 60)
    t_m, t_s = divmod(tot_s_val, 60)
    time_display_str = f"{c_m:02d}:{c_s:02d} / {t_m:02d}:{t_s:02d}"

    play_st = "STOPPED" if is_stopped else ("PAUSED" if is_paused else "PLAYING")
    play_st_color = (48, 59, 255) if is_stopped else ((0, 149, 255) if is_paused else (89, 199, 52))

    comm_lbl = f"COMM: {comm.ACTIVE_COMM}" if comm.ACTIVE_COMM else "COMM: IDLE"
    cv2.putText(pane4, f"VLC [{play_st}] | {time_display_str}", (18, p4_y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, play_st_color, 1, cv2.LINE_AA)

    cv2.putText(pane4, f"FPS: {fps_smooth:.1f} | SCALE: {video_w}x{video_h}", (18, p4_y + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (31, 29, 29), 1, cv2.LINE_AA)

    hw_str = vision.fit_text_to_width(hw_telemetry_status, max_pixel_width=340)
    cv2.putText(pane4, f"{hw_str} | {comm_lbl}", (18, p4_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (60, 58, 58), 1)
    p4_y += 102

    cv2.rectangle(pane4, (10, p4_y), (right_panel_w - 10, p4_y + 115), (250, 250, 252), -1)
    cv2.rectangle(pane4, (10, p4_y), (right_panel_w - 10, p4_y + 115), (255, 122, 0) if locked_target else (204, 199, 199), 1)

    target_sp_name = locked_target["species"] if locked_target else (best_target_info[2] if best_target_info else "Salmo trutta")

    cached_img_obj = comm.GLOBAL_SPECIES_IMAGES.get(target_sp_name)
    if isinstance(cached_img_obj, np.ndarray):
        thumb_res = cv2.resize(cached_img_obj, (80, 80))
        pane4[p4_y+20:p4_y+100, 18:98] = thumb_res
        cv2.rectangle(pane4, (18, p4_y+20), (98, p4_y+100), (255, 122, 0), 1)
        cv2.putText(pane4, "GBIF CACHE", (20, p4_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (255, 122, 0), 1)
    elif best_target_crop is not None:
        t_crop_res = cv2.resize(best_target_crop, (80, 80))
        pane4[p4_y+20:p4_y+100, 18:98] = t_crop_res
        cv2.rectangle(pane4, (18, p4_y+20), (98, p4_y+100), (0, 149, 255), 1)
        cv2.putText(pane4, "YOLO CROP", (22, p4_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (0, 149, 255), 1)

    cv2.putText(pane4, "TARGET SPECIMEN DETAILS", (108, p4_y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 122, 0), 1, cv2.LINE_AA)

    if locked_target is not None:
        cv2.putText(pane4, f"ID: #{locked_target['id']} | CONF: {locked_target['conf']*100:.0f}%",
                    (108, p4_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 122, 0), 1)
        sp_line = vision.fit_text_to_width(f"Species: {locked_target['species']}", max_pixel_width=250)
        cv2.putText(pane4, sp_line, (108, p4_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (31, 29, 29), 1)
    elif best_target_info is not None:
        cv2.putText(pane4, f"Best ID: #{best_target_info[0]} ({best_target_info[1]*100:.0f}%)",
                    (108, p4_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (60, 58, 58), 1)
        sp_line = vision.fit_text_to_width(f"Species: {best_target_info[2]}", max_pixel_width=250)
        cv2.putText(pane4, sp_line, (108, p4_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (31, 29, 29), 1)
    else:
        cv2.putText(pane4, "Click target fish to lock", (108, p4_y + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (142, 142, 147), 1)
    p4_y += 128

    comm.update_pauly_fade_state_machine()
    
    if comm.pauly_active_dialogue:
        text_lines = ui.get_wrapped_text_lines(comm.pauly_active_dialogue, max_w=right_panel_w - 36, font_scale=0.35)
        pauly_card_h = max(140, len(text_lines) * 18 + 48)
    else:
        pauly_card_h = 90

    cv2.rectangle(pane4, (10, p4_y), (right_panel_w - 10, p4_y + pauly_card_h), (250, 250, 252), -1)
    cv2.rectangle(pane4, (10, p4_y), (right_panel_w - 10, p4_y + pauly_card_h), (89, 199, 52) if comm.is_pauly_speaking() else (204, 199, 199), 1)

    cv2.putText(pane4, "DR. PAULY NEURAL VOICE TELEMETRY", (18, p4_y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (89, 199, 52), 1, cv2.LINE_AA)

    if comm.pauly_active_dialogue:
        ui.draw_wrapped_text(pane4, comm.pauly_active_dialogue, 18, p4_y + 40, max_w=right_panel_w - 36, max_lines=12, font_scale=0.35, text_color=(31, 29, 29))
    else:
        cv2.putText(pane4, "Press [C] or click fish to trigger Dr. Pauly audio", (18, p4_y + 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.34, (142, 142, 147), 1)
    p4_y += pauly_card_h + 10

    comm.johnny_relic.update_and_render(canvas, pane4_x, right_panel_w, start_y=p4_y, draw_text_fn=ui.draw_wrapped_text)

    # RENDER MOUSE RESIZABLE SPLITTER DIVIDERS
    v1_color = (0, 149, 255) if (hovered_divider == 'v1' or dragging_divider == 'v1') else (204, 199, 199)
    v1_thick = 4 if (hovered_divider == 'v1' or dragging_divider == 'v1') else 2
    cv2.line(canvas, (left_panel_w, 0), (left_panel_w, canvas_h), v1_color, v1_thick)
    h_cy = canvas_h // 2
    cv2.rectangle(canvas, (left_panel_w - 6, h_cy - 18), (left_panel_w + 6, h_cy + 18), v1_color, -1)
    cv2.putText(canvas, "||", (left_panel_w - 4, h_cy + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (255, 255, 255), 1)

    v2_x = left_panel_w + video_w
    v2_color = (0, 149, 255) if (hovered_divider == 'v2' or dragging_divider == 'v2') else (204, 199, 199)
    v2_thick = 4 if (hovered_divider == 'v2' or dragging_divider == 'v2') else 2
    cv2.line(canvas, (v2_x, 0), (v2_x, canvas_h), v2_color, v2_thick)
    cv2.rectangle(canvas, (v2_x - 6, h_cy - 18), (v2_x + 6, h_cy + 18), v2_color, -1)
    cv2.putText(canvas, "||", (v2_x - 4, h_cy + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (255, 255, 255), 1)

    h1_color = (0, 149, 255) if (hovered_divider == 'h1' or dragging_divider == 'h1') else (204, 199, 199)
    h1_thick = 4 if (hovered_divider == 'h1' or dragging_divider == 'h1') else 2
    cv2.line(canvas, (left_panel_w, video_h), (v2_x, video_h), h1_color, h1_thick)
    h_cx = left_panel_w + video_w // 2
    cv2.rectangle(canvas, (h_cx - 18, video_h - 6), (h_cx + 18, video_h + 6), h1_color, -1)
    cv2.putText(canvas, "=", (h_cx - 4, video_h + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 255, 255), 1)

    # ACTION DISPATCHER
    if action_trigger:
        if action_trigger == "toggle_filter":
            current_filter_idx = (current_filter_idx + 1) % len(selectable_filters)
            active_f = selectable_filters[current_filter_idx]
            ui.hud_notifs.add(f"🎯 TARGET FILTER: {active_f.upper()}", (255, 122, 0), 2.5)
        elif action_trigger == "toggle_fx":
            current_fx_idx = (current_fx_idx + 1) % len(vision_fx_names)
            fx_name = vision_fx_names[current_fx_idx]
            ui.hud_notifs.add(f"👁️ VISION FX MODE: {fx_name}", (222, 82, 175), 2.5)
        elif action_trigger == "toggle_vec":
            show_motion_vectors = not show_motion_vectors
            ui.hud_notifs.add(f"🚀 MOTION VECTORS: {'ENABLED' if show_motion_vectors else 'DISABLED'}", (89, 199, 52), 2.5)
        elif action_trigger == "toggle_pause":
            if is_stopped:
                is_stopped = False
                is_paused = False
                ui.hud_notifs.add("🎬 VIDEO PLAYBACK RESUMED", (255, 122, 0), 2.5)
            else:
                is_paused = not is_paused
                ui.hud_notifs.add(f"🎬 VIDEO {'PAUSED' if is_paused else 'PLAYING'}", (255, 122, 0), 2.5)
        elif action_trigger == "seek_back":
            seek_request = -int(10 * fps)
            ui.hud_notifs.add("⏪ SEEK BACKWARD 10s", (89, 199, 52), 2.5)
        elif action_trigger == "seek_fwd":
            seek_request = int(10 * fps)
            ui.hud_notifs.add("⏩ SEEK FORWARD 10s", (89, 199, 52), 2.5)
        elif action_trigger == "toggle_repeat":
            repeat_infinitely = not repeat_infinitely
            ui.hud_notifs.add(f"🔄 INFINITE REPEAT: {'ENABLED' if repeat_infinitely else 'DISABLED'}", (0, 149, 255), 2.5)
        elif action_trigger == "stop_video":
            is_stopped = True
            ui.hud_notifs.add("⏹ VIDEO STOPPED (INSPECTION MODE)", (48, 59, 255), 2.5)
        elif action_trigger == "toggle_lang":
            comm.language_mode = "DE" if comm.language_mode == "EN" else "EN"
            ui.hud_notifs.add(f"🌐 LANGUAGE MODE: {comm.language_mode}", (255, 122, 0), 2.5)
        elif action_trigger == "toggle_clahe":
            use_adaptive_clahe = not use_adaptive_clahe
            ui.hud_notifs.add(f"🧪 ADAPTIVE CLAHE BOOST: {'ACTIVE' if use_adaptive_clahe else 'DISABLED'}", (89, 199, 52), 2.5)
        elif action_trigger == "toggle_gif":
            show_water_gif = not show_water_gif
            ui.hud_notifs.add(f"🌊 WATER LAYER: {'ACTIVE' if show_water_gif else 'INACTIVE'}", (255, 122, 0), 2.5)
        elif action_trigger == "toggle_stats":
            show_stats_analyzer = not show_stats_analyzer
            ui.hud_notifs.add(f"📊 STATS & PREDICTOR: {'ACTIVE' if show_stats_analyzer else 'DISABLED'}", (222, 82, 175), 2.5)
        elif action_trigger == "toggle_tracker":
            if "botsort" in active_tracker_cfg:
                active_tracker_cfg = "bytetrack.yaml"
            else:
                active_tracker_cfg = "botsort.yaml"
            ui.hud_notifs.add(f"🤖 TRACKER ALGORITHM: {active_tracker_cfg.upper()}", (0, 149, 255), 2.5)
        elif action_trigger == "call_pauly":
            if comm.ACTIVE_COMM == "JOHNNY":
                ui.hud_notifs.add("⛔ COMM LINK LOCKED: JOHNNY RELIC ACTIVE", (48, 59, 255), 2.5)
            elif comm.is_pauly_speaking() or comm.pauly_fade_state != "IDLE":
                comm.stop_pauly_audio()
                comm.pauly_fade_state = "FADE_OUT"
                ui.hud_notifs.add("🛑 DR. PAULY CALL TERMINATED", (48, 59, 255), 2.5)
            else:
                target_species = locked_target["species"] if locked_target is not None else ("Salmo trutta" if len(recent_gbif_species)==0 else recent_gbif_species[-1])
                target_spec_info = f"Specimen ID #{locked_target['id']} ({locked_target['species']}, Conf: {locked_target['conf']*100:.0f}%)" if locked_target is not None else None
                comm.trigger_pauly_call(target_species, target_specimen_info=target_spec_info, hud_notifs=ui.hud_notifs)
        elif action_trigger == "trigger_johnny":
            if comm.ACTIVE_COMM == "PAULY":
                ui.hud_notifs.add("⛔ COMM LINK LOCKED: DR. PAULY CALL ACTIVE", (48, 59, 255), 2.5)
            elif comm.johnny_relic.is_active:
                comm.johnny_relic.cancel(ui.hud_notifs)
            else:
                comm.johnny_relic.trigger(ui.hud_notifs)
        elif action_trigger == "trigger_chat":
            chat_mode_active = not chat_mode_active
            user_chat_buffer = ""
            if chat_mode_active:
                ui.hud_notifs.add("💬 LIVE CHAT PORTAL ACTIVE (TYPE & PRESS ENTER / ESC TO CLOSE)", (255, 122, 0), 3.5)
            else:
                ui.hud_notifs.add("💬 CHAT MODE CLOSED", (142, 142, 147), 2.0)
        action_trigger = None

    if chat_mode_active:
        ui.hud_notifs.add("💬 LIVE CHAT MODE: TYPE & PRESS ENTER (TAB / ESC TO CLOSE)", (255, 122, 0), 2.0)
        while chat_mode_active:
            sidebar = canvas[:, pane4_x:]
            chat_y = canvas_h - 105
            cv2.rectangle(sidebar, (15, chat_y), (right_panel_w - 15, chat_y + 35), (242, 242, 247), -1)
            cv2.rectangle(sidebar, (15, chat_y), (right_panel_w - 15, chat_y + 35), (255, 122, 0), 1)
            
            cursor_str = "_" if int(time.time()*3)%2==0 else ""
            chat_lbl = f"USER CHAT [EN/DE]: {user_chat_buffer}{cursor_str}"
            chat_lbl = vision.fit_text_to_width(chat_lbl, max_pixel_width=340, font_scale=0.36)
            cv2.putText(sidebar, chat_lbl, (25, chat_y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 122, 0), 1)
            
            cv2.imshow(window_name, canvas)
            try:
                c_key = cv2.waitKey(20) & 0xFF
            except KeyboardInterrupt:
                c_key = 3
            
            if c_key in [3, 9, 20, 27]:
                chat_mode_active = False
                ui.hud_notifs.add("💬 CHAT MODE CLOSED", (142, 142, 147), 2.0)
            elif c_key == 13:
                if user_chat_buffer.strip():
                    if comm.ACTIVE_COMM == "JOHNNY":
                        comm.johnny_relic.cancel(ui.hud_notifs)
                    target_species = locked_target["species"] if locked_target is not None else ("Salmo trutta" if len(recent_gbif_species)==0 else recent_gbif_species[-1])
                    target_spec_info = f"Specimen ID #{locked_target['id']} ({locked_target['species']}, Conf: {locked_target['conf']*100:.0f}%)" if locked_target is not None else None
                    comm.trigger_pauly_call(target_species, user_question=user_chat_buffer, target_specimen_info=target_spec_info, hud_notifs=ui.hud_notifs, force=True)
                chat_mode_active = False
            elif c_key == 27:
                chat_mode_active = False
            elif c_key in [8, 127]:
                user_chat_buffer = user_chat_buffer[:-1]
            elif 32 <= c_key <= 126:
                if len(user_chat_buffer) < 42:
                    user_chat_buffer += chr(c_key)

    try:
        key_raw = cv2.waitKeyEx(1)
        key = key_raw & 0xFF if key_raw != -1 else -1
    except KeyboardInterrupt:
        key_raw = 3
        key = 3

    if key_raw in [2424832, 65361, 37] or key in [81, ord(','), ord('b'), ord('B')]:
        seek_request = -int(10 * fps)
        ui.hud_notifs.add("⏪ SEEK BACKWARD 10s (Left Arrow)", (89, 199, 52), 2.5)
    elif key_raw in [2555904, 65363, 39] or key in [83, ord('.'), ord('n'), ord('N')]:
        seek_request = int(10 * fps)
        ui.hud_notifs.add("⏩ SEEK FORWARD 10s (Right Arrow)", (89, 199, 52), 2.5)
    elif key == 32:
        if is_stopped:
            is_stopped = False
            is_paused = False
            ui.hud_notifs.add("🎬 VIDEO PLAYBACK RESUMED", (255, 122, 0), 2.5)
        else:
            is_paused = not is_paused
            ui.hud_notifs.add(f"🎬 VIDEO {'PAUSED' if is_paused else 'PLAYING'}", (255, 122, 0), 2.5)
    elif key == ord('r') or key == ord('R'):
        repeat_infinitely = not repeat_infinitely
        ui.hud_notifs.add(f"🔄 INFINITE REPEAT: {'ENABLED' if repeat_infinitely else 'DISABLED'}", (0, 149, 255), 2.5)
    elif key == ord('x') or key == ord('X'):
        is_stopped = True
        ui.hud_notifs.add("⏹ VIDEO STOPPED (INSPECTION MODE)", (48, 59, 255), 2.5)
    elif key in [3, 9, 20]:
        chat_mode_active = not chat_mode_active
        user_chat_buffer = ""
        if chat_mode_active:
            ui.hud_notifs.add("💬 CHAT MODE ACTIVE (TYPE & PRESS ENTER / TAB / ESC TO CLOSE)", (255, 122, 0), 3.5)
        else:
            ui.hud_notifs.add("💬 CHAT MODE CLOSED", (142, 142, 147), 2.0)
    elif key == ord('q') or key == ord('Q'):  
        break
    elif key == ord('o') or key == ord('O'):
        new_vid = select_video_file_dialog()
        if new_vid and os.path.exists(new_vid):
            new_cap = cv2.VideoCapture(new_vid)
            if new_cap.isOpened():
                cap.release()
                cap = new_cap
                video_path = new_vid
                ui.hud_notifs.add(f"🎬 SWITCHED VIDEO: {os.path.basename(video_path)}", (89, 199, 52), 3.0)
            else:
                ui.hud_notifs.add("⚠️ FAILED TO OPEN SELECTED VIDEO", (48, 59, 255), 2.5)
    elif key == ord('c') or key == ord('C'):
        if comm.ACTIVE_COMM == "JOHNNY":
            ui.hud_notifs.add("⛔ COMM LINK LOCKED: JOHNNY RELIC ACTIVE", (48, 59, 255), 2.5)
        elif comm.is_pauly_speaking() or comm.pauly_fade_state != "IDLE":
            comm.stop_pauly_audio()
            comm.pauly_fade_state = "FADE_OUT"
            ui.hud_notifs.add("🛑 DR. PAULY CALL TERMINATED", (48, 59, 255), 2.5)
        else:
            target_species = locked_target["species"] if locked_target is not None else ("Salmo trutta" if len(recent_gbif_species)==0 else recent_gbif_species[-1])
            target_spec_info = f"Specimen ID #{locked_target['id']} ({locked_target['species']}, Conf: {locked_target['conf']*100:.0f}%)" if locked_target is not None else None
            comm.trigger_pauly_call(target_species, target_specimen_info=target_spec_info, hud_notifs=ui.hud_notifs)
    elif key == ord('j') or key == ord('J'):
        if comm.ACTIVE_COMM == "PAULY":
            ui.hud_notifs.add("⛔ COMM LINK LOCKED: DR. PAULY CALL ACTIVE", (48, 59, 255), 2.5)
        elif comm.johnny_relic.is_active:
            comm.johnny_relic.cancel(ui.hud_notifs)
        else:
            comm.johnny_relic.trigger(ui.hud_notifs)
    elif key == ord('l') or key == ord('L'):
        comm.language_mode = "DE" if comm.language_mode == "EN" else "EN"
        ui.hud_notifs.add(f"🌐 LANGUAGE MODE SET TO: {comm.language_mode}", (255, 122, 0), 2.5)
    elif key == ord('w') or key == ord('W'):
        show_water_gif = not show_water_gif
        ui.hud_notifs.add(f"🌊 WATER LAYER: {'ACTIVE' if show_water_gif else 'INACTIVE'}", (255, 122, 0), 2.5)
    elif key == ord('a') or key == ord('A'):
        use_adaptive_clahe = not use_adaptive_clahe
        ui.hud_notifs.add(f"🧪 ADAPTIVE CLAHE BOOST: {'ACTIVE' if use_adaptive_clahe else 'DISABLED'}", (89, 199, 52), 2.5)
    elif key == ord('s') or key == ord('S'):
        current_filter_idx = (current_filter_idx + 1) % len(selectable_filters)
        active_f = selectable_filters[current_filter_idx]
        ui.hud_notifs.add(f"🎯 TARGET FILTER: {active_f.upper()}", (255, 122, 0), 2.5)
    elif key == ord('f') or key == ord('F'):
        current_fx_idx = (current_fx_idx + 1) % len(vision_fx_names)
        fx_name = vision_fx_names[current_fx_idx]
        ui.hud_notifs.add(f"👁️ VISION FX MODE: {fx_name}", (222, 82, 175), 2.5)
    elif key == ord('v') or key == ord('V'):
        show_motion_vectors = not show_motion_vectors
        ui.hud_notifs.add(f"🚀 MOTION VECTORS: {'ENABLED' if show_motion_vectors else 'DISABLED'}", (89, 199, 52), 2.5)
    elif key == ord('z') or key == ord('Z'):
        show_pip_zoom = not show_pip_zoom
        ui.hud_notifs.add(f"🔍 MAGNIFIER PiP ZOOM: {'ENABLED' if show_pip_zoom else 'DISABLED'}", (222, 82, 175), 2.5)
    elif key == ord('t') or key == ord('T'):
        if "botsort" in active_tracker_cfg:
            active_tracker_cfg = "bytetrack.yaml"
        else:
            active_tracker_cfg = "botsort.yaml"
        ui.hud_notifs.add(f"🤖 TRACKER ENGINE: {active_tracker_cfg.upper()}", (0, 149, 255), 2.5)

    if not is_headless:
        try:
            cv2.imshow(window_name, canvas)
        except Exception:
            is_headless = True
    out.write(canvas)

cap.release()
out.release()
print(f"✅ Video processing complete. Tracked video saved to: {output_path}")

# --- EXPORT PER-VIDEO UNIQUE SESSION ARTIFACTS WITH END-OF-SESSION LOADING SCREEN ---
if save_analysis_enabled and session_info is not None:
    def _do_full_export():
        print("\n" + "="*70)
        print(f"📦 EXPORTING PER-VIDEO SESSION ARTIFACTS: {session_info['session_name']}")
        print("="*70)
        census.generate_csv_report(output_dir=session_info["csv_dir"], output_filename="fish_counts.csv")
        chart.save_all_20_session_plots(enkf_filter, census.get_census_summary(), session_info["plots_dir"])
        comm.generate_executive_ollama_report(session_info, census.get_census_summary(), enkf_filter, session_info["analysis_dir"])
        try:
            import docx_report_generator as docx_gen
            docx_gen.generate_docx_report(enkf_filter, census.get_census_summary(), analysis_dir=session_info["analysis_dir"], plots_dir=session_info["plots_dir"], script_dir=cfg.script_dir)
        except Exception as _de:
            print(f"[DOCX Exporter Notice]: {_de}")
        print("="*70)
        print(f"✨ All session outputs successfully generated in: {session_info['session_dir']}")
        print("="*70 + "\n")

    if is_headless:
        print("📦 Headless mode active: Exporting all session artifacts directly...")
        _do_full_export()
    else:
        try:
            ui.display_analysis_export_loading_screen(window_name, canvas_w, canvas_h, session_info, _do_full_export)
        except Exception:
            _do_full_export()

if not is_headless:
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass
sys.exit(0)
