import os
import cv2
import numpy as np
from ultralytics import YOLO
from mod_00_config_and_assets import script_dir, find_asset

def load_ensemble_models(target_device):
    """
    Scans models/ directory for all available YOLO weights and sorts them strictly by user priority:
    1. fish_model.pt
    2. best.pt
    3. The rest (meduim.pt, small.pt, etc.)
    Loads ALL available models into an ensemble list.
    """
    models_dir = os.path.join(script_dir, "models")
    discovered_files = []
    
    if os.path.exists(models_dir):
        for f in os.listdir(models_dir):
            if f.endswith(".pt"):
                discovered_files.append(os.path.join(models_dir, f))

    for candidate in ["fish_model.pt", "best.pt", "meduim.pt", "small.pt"]:
        cp = find_asset(candidate)
        if os.path.exists(cp) and cp not in discovered_files:
            discovered_files.append(cp)

    def get_priority_key(filepath):
        name = os.path.basename(filepath).lower()
        if name == "fish_model.pt":
            return 0
        elif name == "best.pt":
            return 1
        elif "meduim" in name:
            return 2
        elif "small" in name:
            return 3
        else:
            return 4 + len(name)

    sorted_paths = sorted(list(set(discovered_files)), key=get_priority_key)
    print(f"📦 Loading All Neural Models from models/ folder ({len(sorted_paths)} models in priority order): {[os.path.basename(p) for p in sorted_paths]}")

    ensemble_models = []
    for p in sorted_paths:
        try:
            m = YOLO(p)
            if str(target_device) != "cpu":
                try:
                    m.to(target_device)
                except Exception:
                    m.to("cpu")
            ensemble_models.append((os.path.basename(p), m))
            print(f"  ✅ Priority #{len(ensemble_models)}: Loaded '{os.path.basename(p)}' on {target_device}")
        except Exception as e:
            print(f"  ⚠️ Error loading model '{p}': {e}")

    if not ensemble_models:
        fallback_m = YOLO(find_asset("best.pt"))
        ensemble_models.append(("best.pt", fallback_m))

    primary_model = ensemble_models[0][1]
    return ensemble_models, primary_model

def adaptive_underwater_enhance(img):
    """Applies CLAHE contrast limited histogram equalization for turbid underwater frames."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

def generate_water_gif_frame(h, w, t_sec):
    """Generates synthetic water surface layer animation frame."""
    fx = np.linspace(0, 4*np.pi, w)
    fy = np.linspace(0, 4*np.pi, h)
    grid_x, grid_y = np.meshgrid(fx, fy)
    wave = np.sin(grid_x + t_sec*3) * np.cos(grid_y - t_sec*2)
    norm = np.uint8((wave + 1.0) * 127.5)
    return cv2.applyColorMap(norm, cv2.COLORMAP_OCEAN)

def fit_text_to_width(text, max_pixel_width=340, font_scale=0.38, thickness=1):
    font = cv2.FONT_HERSHEY_SIMPLEX
    curr_text = text
    while len(curr_text) > 3:
        w = cv2.getTextSize(curr_text, font, font_scale, thickness)[0][0]
        if w <= max_pixel_width:
            return curr_text
        curr_text = curr_text[:-4] + "..."
    return curr_text

def draw_target_box(img, box, track_id, species_name, conf, custom_color=None, is_selected=False):
    """Renders target bounding box reticle and label badge."""
    x1, y1, x2, y2 = map(int, box)
    w, h = x2 - x1, y2 - y1
    
    color = custom_color if custom_color is not None else (255, 122, 0)
    if is_selected:
        color = (0, 149, 255)
    
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2 if is_selected else 1)
    
    line_len = min(18, max(4, w // 4), max(4, h // 4))
    cv2.line(img, (x1, y1), (x1 + line_len, y1), color, 2)
    cv2.line(img, (x1, y1), (x1, y1 + line_len), color, 2)
    cv2.line(img, (x2, y1), (x2 - line_len, y1), color, 2)
    cv2.line(img, (x2, y1), (x2, y1 + line_len), color, 2)
    cv2.line(img, (x1, y2), (x1 + line_len, y2), color, 2)
    cv2.line(img, (x1, y2), (x1, y2 - line_len), color, 2)
    cv2.line(img, (x2, y2), (x2 - line_len, y2), color, 2)
    cv2.line(img, (x2, y2), (x2, y2 - line_len), color, 2)

    badge_text = f"#{track_id} {species_name} {conf*100:.0f}%"
    badge_text = fit_text_to_width(badge_text, max_pixel_width=max(w, 140), font_scale=0.38)
    t_size = cv2.getTextSize(badge_text, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)[0]
    
    cv2.rectangle(img, (x1, y1 - t_size[1] - 8), (x1 + t_size[0] + 10, y1), (255, 255, 255), -1)
    cv2.rectangle(img, (x1, y1 - t_size[1] - 8), (x1 + t_size[0] + 10, y1), color, 1)
    cv2.putText(img, badge_text, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1, cv2.LINE_AA)
