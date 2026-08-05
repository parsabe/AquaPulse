import os
import sys
import argparse
import time
import cv2
import requests
import pyttsx3
import threading
import torch
import random
import numpy as np
from collections import deque, defaultdict
from ultralytics import YOLO
from langchain_ollama import OllamaLLM

# --- 1. CROSS-PLATFORM HARDWARE ACCELERATION ENGINE ---
def detect_device_hardware():
    """Detects available hardware acceleration across NVIDIA CUDA, Apple MPS, AMD GPU, or CPU."""
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        return "cuda", f"CUDA ({device_name})"
    
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps", "Apple Metal GPU (MPS)"
    
    try:
        import torch_directml
        if torch_directml.is_available():
            dml_device = torch_directml.device()
            dml_name = torch_directml.device_name(0) if hasattr(torch_directml, "device_name") else "AMD DirectML GPU"
            return dml_device, f"AMD DirectML ({dml_name})"
    except ImportError:
        pass
    
    return "cpu", "CPU Engine (Fallback)"

def load_model_on_device(model_path, device_target):
    """Safely loads YOLO neural model onto detected hardware with fallback safety."""
    print(f"📦 Initializing model on hardware target: {device_target}...")
    try:
        model = YOLO(model_path)
        if str(device_target) != "cpu":
            try:
                model.to(device_target)
            except Exception as e:
                print(f"⚠️ Hardware transfer failed ({e}). Falling back to CPU.")
                model.to("cpu")
                return model, "cpu", "CPU Engine (Fallback)"
        return model, device_target, None
    except Exception as e:
        print(f"⚠️ Model load error ({e}). Falling back to CPU.")
        model = YOLO(model_path).to("cpu")
        return model, "cpu", "CPU Engine (Fallback)"

def get_hardware_status_summary(device_target, device_desc):
    """Generates Cyberpunk Telemetry status string for HUD."""
    return f"HW: {device_desc}"

# --- 2. LOCAL AI & PATHS SETUP ---
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "fish_model.pt")

parser = argparse.ArgumentParser(description="AquaPulse Vision Transformer Tracking")
parser.add_argument("video_pos", nargs="?", default=None, help="Path to input video file")
parser.add_argument("--video", "-v", type=str, default=None, help="Path to input video file")
args, _ = parser.parse_known_args()

input_video_arg = args.video or args.video_pos

if input_video_arg:
    video_path = input_video_arg.strip('"\'')
    if not os.path.isabs(video_path):
        video_path = os.path.abspath(os.path.join(os.getcwd(), video_path))
    print(f"🎬 Video source provided: {video_path}")
else:
    default_candidates = ["dehazed_main2.mp4", "main2.mp4", "main.mp4"]
    video_path = None
    for cand in default_candidates:
        cand_path = os.path.join(script_dir, cand)
        if os.path.exists(cand_path):
            video_path = cand_path
            break
    if not video_path:
        video_path = os.path.join(script_dir, "main2.mp4")
    print(f"🎬 Using default video source: {video_path}")

output_path = os.path.join(script_dir, "tracked_output2.mp4")

# Hardware detection and neural model loading
target_dev, hw_desc = detect_device_hardware()
print(f"✅ Hardware Detected: {hw_desc}")

llm = OllamaLLM(model="llama3")
model, active_device, fallback_desc = load_model_on_device(model_path, target_dev)
if fallback_desc:
    hw_desc = fallback_desc

hw_telemetry_status = get_hardware_status_summary(active_device, hw_desc)

# --- 2B. LOCAL ASSETS LOADERS (JOHNNY, SCUBA PAULY, WATER GIF) ---
johnny_img_rgba = None
for fname in ["johnny.png", "johnny.jpg", "johnny.jpeg", "Johnny.png", "Johnny.jpg"]:
    ipath = os.path.join(script_dir, fname)
    if os.path.exists(ipath):
        loaded_img = cv2.imread(ipath, cv2.IMREAD_UNCHANGED)
        if loaded_img is not None:
            johnny_img_rgba = loaded_img
            print(f"🎸 Loaded local Johnny Silverhand image asset ({fname}).")
            break

scuba_pauly_img = None
for fname in ["scuba_pauly.png", "scuba_pauly.jpg", "scuba_pauly.jpeg", "scuba.png"]:
    spath = os.path.join(script_dir, fname)
    if os.path.exists(spath):
        simg = cv2.imread(spath, cv2.IMREAD_UNCHANGED)
        if simg is not None:
            scuba_pauly_img = simg
            print(f"🤿 Loaded Dr. Pauly Scuba image asset ({fname}).")
            break

water_gif_cap = None
gif_path = os.path.join(script_dir, "water_effect.gif")
if os.path.exists(gif_path):
    try:
        water_gif_cap = cv2.VideoCapture(gif_path)
        print("🌊 Loaded local water_effect.gif overlay.")
    except Exception:
        water_gif_cap = None

show_water_gif = False

johnny_audio_files = []
for fname in os.listdir(script_dir):
    if (fname.lower().startswith("johnny") or "johnny_quote" in fname.lower()) and fname.lower().endswith((".wav", ".mp3")):
        johnny_audio_files.append(os.path.join(script_dir, fname))

if len(johnny_audio_files) > 0:
    print(f"🎵 Discovered {len(johnny_audio_files)} local Johnny Silverhand audio quote file(s).")

# --- 2C. DUAL GBIF & WIKIMEDIA SPECIES IMAGE FETCHER WITH PERSISTENT MEMORY CACHE ---
wiki_disk_cache_dir = os.path.join(script_dir, "species_snapshots", "wiki_cache")
os.makedirs(wiki_disk_cache_dir, exist_ok=True)
GLOBAL_SPECIES_IMAGES = {}

def fetch_gbif_image(species_name):
    """Primary fetcher: Queries GBIF Occurrence API for high-res species photos with Wikimedia fallback."""
    search_term = species_name.replace(" ", "%20")
    gbif_url = f"https://api.gbif.org/v1/occurrence/search?scientificName={search_term}&mediaType=StillImage&limit=5"
    
    # 1. Query GBIF Occurrence API
    try:
        res = requests.get(gbif_url, headers={"User-Agent": "SpreewaldCyberdeck/1.0"}, timeout=4)
        if res.status_code == 200:
            data = res.json()
            results = data.get("results", [])
            for occ in results:
                media_list = occ.get("media", [])
                for media in media_list:
                    img_url = media.get("identifier")
                    if img_url:
                        try:
                            img_res = requests.get(img_url, timeout=4)
                            if img_res.status_code == 200:
                                img_arr = np.frombuffer(img_res.content, np.uint8)
                                decoded = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
                                if decoded is not None and decoded.size > 0:
                                    if decoded.ndim == 3 and decoded.shape[2] == 4:
                                        decoded = cv2.cvtColor(decoded, cv2.COLOR_BGRA2BGR)
                                    elif decoded.ndim == 2:
                                        decoded = cv2.cvtColor(decoded, cv2.COLOR_GRAY2BGR)
                                    resized = cv2.resize(decoded, (380, 220))
                                    return resized
                        except Exception:
                            continue
    except Exception:
        pass
        
    # 2. Fallback: Wikimedia Commons / Wikipedia API
    wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&pithumbsize=500&titles={search_term}"
    try:
        res = requests.get(wiki_url, headers={"User-Agent": "SpreewaldCyberdeck/1.0"}, timeout=4)
        if res.status_code == 200:
            data = res.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if "thumbnail" in page_data:
                    img_url = page_data["thumbnail"]["source"]
                    img_res = requests.get(img_url, timeout=4)
                    if img_res.status_code == 200:
                        img_arr = np.frombuffer(img_res.content, np.uint8)
                        decoded = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
                        if decoded is not None and decoded.size > 0:
                            if decoded.ndim == 3 and decoded.shape[2] == 4:
                                decoded = cv2.cvtColor(decoded, cv2.COLOR_BGRA2BGR)
                            elif decoded.ndim == 2:
                                decoded = cv2.cvtColor(decoded, cv2.COLOR_GRAY2BGR)
                            resized = cv2.resize(decoded, (380, 220))
                            return resized
    except Exception:
        pass

    return None

def async_preload_species_image(species_name):
    """Background worker to download and cache species images into GLOBAL_SPECIES_IMAGES without freezing UI."""
    if species_name in GLOBAL_SPECIES_IMAGES:
        return
    img = fetch_gbif_image(species_name)
    if img is not None:
        GLOBAL_SPECIES_IMAGES[species_name] = img
    else:
        GLOBAL_SPECIES_IMAGES[species_name] = "FAILED"

# --- 3. SPEAKER MUTUAL EXCLUSION LOCK & AUDIO ENGINES ---
ACTIVE_COMM = None  # Global Mutual Exclusion Lock: None, "PAULY", or "JOHNNY"
language_mode = "EN"  # Global Language Toggle: "EN" or "DE"

class CancellableAudioEngine:
    """Audio engine supporting language selection and instant cancellation."""
    def __init__(self, speech_rate=160, lang="EN"):
        self.is_speaking = False
        self.engine = None
        self.speech_rate = speech_rate
        self.lang = lang
        self.lock = threading.Lock()

    def speak(self, text):
        with self.lock:
            self.is_speaking = True
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.speech_rate)
            
            voices = self.engine.getProperty('voices')
            for voice in voices:
                v_name = voice.name.lower()
                v_id = voice.id.lower()
                if self.lang == "DE" and ("german" in v_name or "deutsch" in v_name or "de_" in v_id or "de-" in v_id):
                    self.engine.setProperty('voice', voice.id)
                    break
                elif self.lang == "EN" and ("english" in v_name or "en_" in v_id or "en-" in v_id or "david" in v_name or "zira" in v_name):
                    self.engine.setProperty('voice', voice.id)
                    break
                    
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception:
            pass
        finally:
            with self.lock:
                self.is_speaking = False
                self.engine = None

    def cancel(self):
        with self.lock:
            if self.is_speaking and self.engine is not None:
                try:
                    self.engine.stop()
                except Exception:
                    pass
                self.is_speaking = False
                self.engine = None
                return True
        return False

pauly_audio_en = CancellableAudioEngine(speech_rate=160, lang="EN")
pauly_audio_de = CancellableAudioEngine(speech_rate=155, lang="DE")
johnny_audio = CancellableAudioEngine(speech_rate=150, lang="EN")

def speak_pauly_with_lang(text, lang="EN"):
    if lang == "DE":
        pauly_audio_de.speak(text)
    else:
        pauly_audio_en.speak(text)

def play_johnny_audio(quote_text):
    if len(johnny_audio_files) > 0:
        chosen_audio = random.choice(johnny_audio_files)
        try:
            if chosen_audio.endswith(".wav"):
                import winsound
                winsound.PlaySound(chosen_audio, winsound.SND_FILENAME | winsound.SND_ASYNC)
                return
        except Exception:
            pass
    johnny_audio.speak(quote_text)

def stop_johnny_audio():
    try:
        import winsound
        winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass
    johnny_audio.cancel()

def stop_pauly_audio():
    pauly_audio_en.cancel()
    pauly_audio_de.cancel()

def is_pauly_speaking():
    return pauly_audio_en.is_speaking or pauly_audio_de.is_speaking

def fetch_gbif_data(species_name):
    """Queries live GBIF API for scientific taxonomy."""
    search_term = species_name.replace(" ", "%20")
    url = f"https://api.gbif.org/v1/species/match?name={search_term}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "Scientific Name": data.get("scientificName", species_name),
                "Kingdom": data.get("kingdom", "Unknown"),
                "Phylum": data.get("phylum", "Unknown"),
                "Class": data.get("class", "Unknown"),
                "Order": data.get("order", "Unknown"),
                "Family": data.get("family", "Unknown"),
                "Confidence Match": f"{data.get('confidence', 0)}%"
            }
    except Exception:
        pass
    
    return {
        "Scientific Name": species_name,
        "Family": "Aquatic species",
        "Note": "Taxonomy fetched via local fallback."
    }

def ask_dr_pauly(species_name, biology_data, user_question=None, lang="EN"):
    """Uses Ollama to format GBIF taxonomy data into Dr. Pauly persona with strict brevity limit (max 40 words)."""
    if lang == "DE":
        if user_question:
            template = f"""
            Sie sind Dr. Daniel Pauly, der weltberühmte Meeresbiologe.
            Ein Forscher stellt Ihnen folgende Frage zu dem Fisch '{species_name}': "{user_question}".
            
            Antworten Sie vollständig auf Deutsch in akademischer, präziser Sprache. 
            Halten Sie Ihre Antwort extrem kurz (maximal 2 kurze Sätze, unter 40 Wörtern). Beginnen Sie mit "Ah, hallo! Dr. Pauly hier."
            """
        else:
            template = f"""
            Sie sind Dr. Daniel Pauly, der weltberühmte Meeresbiologe. 
            Sie sprechen mit einem Forschungsteam, das gerade einen {species_name} mittels Computervision erfasst hat.
            
            Verwenden Sie NUR die folgenden Taxonomiedaten von GBIF und geben Sie eine faszinierende Erklärung zu diesem Fisch. 
            Antworten Sie vollständig auf Deutsch in akademischer Sprache (maximal 2 kurze Sätze, unter 40 Wörtern). Beginnen Sie mit "Ah, hallo! Dr. Pauly hier."
            
            GBIF-Taxonomiedaten: {biology_data}
            """
    else: # EN
        if user_question:
            template = f"""
            You are Dr. Daniel Pauly, world-renowned marine biologist.
            A researcher asks you this question about '{species_name}': "{user_question}".
            
            Reply entirely in English with wise scientific insights.
            Limit your response to an absolute maximum of 2 short sentences (under 40 words). Start with "Ah, hello! Dr. Pauly here."
            """
        else:
            template = f"""
            You are Dr. Daniel Pauly, world-renowned marine biologist.
            You are speaking with a research team who just tracked a {species_name} using computer vision.
            
            Using ONLY the following GBIF taxonomy data, give a fascinating explanation of this fish in English.
            Limit your response to an absolute maximum of 2 short sentences (under 40 words). Start with "Ah, hello! Dr. Pauly here."
            
            GBIF Taxonomy Data: {biology_data}
            """
    try:
        return llm.invoke(template)
    except Exception:
        if lang == "DE":
            return f"Ah, hallo! Dr. Pauly hier. Wir haben einen faszinierenden {species_name} entdeckt."
        else:
            return f"Ah, hello! Dr. Pauly here. We have spotted a fascinating {species_name} specimen."

def trigger_pauly_call(target_species, user_question=None):
    """Triggers Dr. Pauly holo-call, preloads GBIF species snapshot in background thread, and starts voice synthesis."""
    global pauly_active_dialogue, pauly_fade_state, ACTIVE_COMM
    
    hud_notifs.add(f"📞 DR. PAULY HOLO-CALL ({language_mode}) FOR {target_species.upper()}...", (0, 255, 0), 4.0)
    
    # Fire asynchronous image preload if not already in cache
    if target_species not in GLOBAL_SPECIES_IMAGES:
        threading.Thread(target=async_preload_species_image, args=(target_species,), daemon=True).start()

    fish_data = fetch_gbif_data(target_species)
    pauly_dialogue = ask_dr_pauly(target_species, biology_data=fish_data, user_question=user_question, lang=language_mode)
    pauly_active_dialogue = pauly_dialogue
    pauly_fade_state = "FADE_IN"
    ACTIVE_COMM = "PAULY"
    threading.Thread(target=speak_pauly_with_lang, args=(pauly_dialogue, language_mode), daemon=True).start()

# --- STICKY TARGET LOCKING HELPER ---
def update_sticky_target_lock(locked_target, current_detections, max_dist=100, max_lost_frames=30):
    if locked_target is None:
        return None

    target_id = locked_target["id"]
    last_cx, last_cy = locked_target["last_center"]

    found_det = None
    for box, tid, sp_n, conf, (cx, cy) in current_detections:
        if tid == target_id:
            found_det = (box, tid, sp_n, conf, (cx, cy))
            break

    if found_det is None and len(current_detections) > 0:
        min_dist = float('inf')
        for box, tid, sp_n, conf, (cx, cy) in current_detections:
            dist = np.hypot(cx - last_cx, cy - last_cy)
            if dist < max_dist and dist < min_dist:
                min_dist = dist
                found_det = (box, tid, sp_n, conf, (cx, cy))

    if found_det is not None:
        box, tid, sp_n, conf, (cx, cy) = found_det
        return {
            "id": tid,
            "species": sp_n,
            "last_center": (cx, cy),
            "lost_frames": 0,
            "box": box,
            "conf": conf
        }
    else:
        locked_target["lost_frames"] += 1
        if locked_target["lost_frames"] > max_lost_frames:
            return None
        return locked_target

# --- TEXT TRUNCATION & DYNAMIC WRAPPED TEXT BOX WITH SOLID OPAQUE FILL ---
def fit_text_to_width(text, max_pixel_width, font_face=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.4, thickness=1):
    t_w = cv2.getTextSize(text, font_face, font_scale, thickness)[0][0]
    if t_w <= max_pixel_width:
        return text
    
    truncated = text
    while len(truncated) > 3:
        truncated = truncated[:-1]
        test_str = truncated + "..."
        if cv2.getTextSize(test_str, font_face, font_scale, thickness)[0][0] <= max_pixel_width:
            return test_str
    return "..."

def draw_wrapped_text(panel, text, start_x, start_y, max_w=380, max_lines=3, font_scale=0.36, text_color=(0, 255, 150), bg_alpha=1.0):
    """Word-wraps text, caps max_lines, draws solid filled dark panel, and returns end Y position."""
    words = text.split()
    lines = []
    curr_line = ""
    for word in words:
        test_line = curr_line + (" " if curr_line else "") + word
        tw = cv2.getTextSize(test_line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)[0][0]
        if tw <= max_w:
            curr_line = test_line
        else:
            if curr_line:
                lines.append(curr_line)
            curr_line = word
    if curr_line:
        lines.append(curr_line)
        
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = fit_text_to_width(lines[-1] + "...", max_pixel_width=max_w, font_scale=font_scale)

    line_h = 18
    pad = 10
    total_h = len(lines) * line_h + pad * 2
    
    # Solid background fill to eliminate under-layer bleeding
    overlay = panel.copy()
    cv2.rectangle(overlay, (start_x, start_y), (start_x + max_w, start_y + total_h), (15, 20, 30), -1)
    cv2.rectangle(overlay, (start_x, start_y), (start_x + max_w, start_y + total_h), (0, 255, 255), 1)
    
    blended = cv2.addWeighted(panel, 1.0 - bg_alpha, overlay, bg_alpha, 0)
    panel[:] = blended
    
    line_y = start_y + pad + 13
    for line in lines:
        cv2.putText(panel, line, (start_x + pad, line_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, 1)
        line_y += line_h
        
    return start_y + total_h + 10

# --- ON-SCREEN HUD NOTIFICATION MANAGER ---
class HUDNotificationManager:
    def __init__(self):
        self.notifications = []

    def add(self, text, color=(0, 255, 255), duration=2.5):
        expire_time = time.time() + duration
        self.notifications.append((text, color, expire_time))

    def draw(self, img):
        now = time.time()
        self.notifications = [n for n in self.notifications if n[2] > now]
        
        start_y = 20
        for text, color, expire_t in self.notifications:
            t_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)[0]
            box_w = t_size[0] + 20
            box_h = 30
            x = img.shape[1] - box_w - 15
            y = start_y
            
            if y + box_h < img.shape[0]:
                roi = img[y:y+box_h, x:x+box_w]
                if roi.shape[0] == box_h and roi.shape[1] == box_w:
                    bg = np.zeros_like(roi, dtype=np.uint8)
                    bg[:] = (15, 20, 30)
                    blended = cv2.addWeighted(roi, 0.25, bg, 0.75, 0)
                    img[y:y+box_h, x:x+box_w] = blended
                    
                    cv2.rectangle(img, (x, y), (x+box_w, y+box_h), color, 1)
                    cv2.putText(img, text, (x + 10, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
                    
            start_y += box_h + 8

# --- CYBERPUNK BACKGROUND VISUAL EFFECTS ---
def draw_cyberpunk_background_vfx(img, frame_count):
    h, w = img.shape[:2]
    scan_offset = (frame_count * 2) % 12
    for y in range(scan_offset, h, 12):
        img[y:y+1, :] = (img[y:y+1, :] * 0.92).astype(np.uint8)
        
    corner_len = 35
    cv2.line(img, (10, 10), (10 + corner_len, 10), (0, 255, 255), 2)
    cv2.line(img, (10, 10), (10, 10 + corner_len), (0, 255, 255), 2)
    
    cv2.line(img, (w - 10, 10), (w - 10 - corner_len, 10), (255, 0, 255), 2)
    cv2.line(img, (w - 10, 10), (w - 10, 10 + corner_len), (255, 0, 255), 2)
    
    cv2.line(img, (10, h - 10), (10 + corner_len, h - 10), (255, 255, 0), 2)
    cv2.line(img, (10, h - 10), (10, h - 10 - corner_len), (255, 255, 0), 2)
    
    cv2.line(img, (w - 10, h - 10), (w - 10 - corner_len, h - 10), (0, 255, 150), 2)
    cv2.line(img, (w - 10, h - 10), (w - 10, h - 10 - corner_len), (0, 255, 150), 2)
    
    timestamp_str = time.strftime("2077.%m.%d - %H:%M:%S", time.localtime())
    cv2.putText(img, f"KIROSHI OPTICS // NIGHT CITY // {timestamp_str}", (w - 360, h - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 255, 255), 1)

# --- JOHNNY SILVERHAND RELIC CONSTRUCT STATE MACHINE [J] ---
class JohnnySilverhandRelicConstruct:
    def __init__(self, fps=30):
        self.quotes = [
            "Wake up, Samurai. We've got fish to track.",
            "Corpo-tech monitoring the river? Classic.",
            "System's glitching, kid. Look alive.",
            "A fish in a cage is still a fish, but out here in Spreewald... it's pure freedom.",
            "Burn bright, Samurai. The city will remember what you tracked today."
        ]
        self.fps = fps
        self.total_duration = 120
        self.current_frame = 0
        self.is_active = False
        self.active_quote = ""

    def trigger(self, hud_notifs=None):
        global ACTIVE_COMM
        ACTIVE_COMM = "JOHNNY"
        self.is_active = True
        self.current_frame = self.total_duration
        self.active_quote = random.choice(self.quotes)
        if hud_notifs:
            hud_notifs.add("⚠️ RELIC MALFUNCTION DETECTED // BIOPORT OVERHEAT", (0, 0, 255), 4.0)
        threading.Thread(target=play_johnny_audio, args=(self.active_quote,), daemon=True).start()

    def cancel(self, hud_notifs=None):
        global ACTIVE_COMM
        if self.is_active:
            self.is_active = False
            self.current_frame = 0
            stop_johnny_audio()
            if ACTIVE_COMM == "JOHNNY":
                ACTIVE_COMM = None
            if hud_notifs:
                hud_notifs.add("🛑 JOHNNY RELIC CONSTRUCT TERMINATED", (0, 0, 255), 2.5)
            return True
        return False

    def check_auto_trigger(self, frame_count, hud_notifs=None):
        global ACTIVE_COMM
        if not self.is_active and ACTIVE_COMM is None and frame_count % 300 == 0:
            if frame_count == 300 or random.random() < 0.15:
                self.trigger(hud_notifs)

    def draw(self, frame, hud_notifs=None):
        global ACTIVE_COMM
        if not self.is_active or self.current_frame <= 0:
            if self.is_active:
                self.is_active = False
                if ACTIVE_COMM == "JOHNNY":
                    ACTIVE_COMM = None
            return
            
        self.current_frame -= 1
        h, w = frame.shape[:2]
        progress_elapsed = self.total_duration - self.current_frame
        
        is_glitch_in = progress_elapsed <= 15
        is_glitch_out = self.current_frame <= 15
        
        ov_w, ov_h = 280, 330
        ov_x = w - ov_w - 20
        ov_y = h - ov_h - 45
        
        if is_glitch_in or is_glitch_out:
            ov_x += random.randint(-12, 12)
            ov_y += random.randint(-8, 8)
            ov_x = max(10, min(w - ov_w - 10, ov_x))
            ov_y = max(10, min(h - ov_h - 10, ov_y))

        if is_glitch_in or is_glitch_out:
            shift = random.randint(8, 18)
            b, g, r = cv2.split(frame)
            b_shifted = np.roll(b, shift, axis=1)
            r_shifted = np.roll(r, -shift, axis=1)
            cv2.merge((b_shifted, g, r_shifted), dst=frame)
            
            if random.random() < 0.6:
                noise_y = random.randint(20, h - 40)
                frame[noise_y:noise_y+15, :] = cv2.bitwise_xor(frame[noise_y:noise_y+15, :], (0, 255, 255))

        if johnny_img_rgba is not None:
            has_alpha = (johnny_img_rgba.shape[2] == 4)
            if has_alpha:
                bgr_img = johnny_img_rgba[:, :, :3]
                alpha_img = johnny_img_rgba[:, :, 3] / 255.0
            else:
                bgr_img = johnny_img_rgba
                alpha_img = np.ones(bgr_img.shape[:2], dtype=np.float32)
                
            resized_bgr = cv2.resize(bgr_img, (ov_w, ov_h))
            resized_alpha = cv2.resize(alpha_img, (ov_w, ov_h))
            
            roi = frame[ov_y:ov_y+ov_h, ov_x:ov_x+ov_w]
            if roi.shape[0] == ov_h and roi.shape[1] == ov_w:
                base_opacity = 0.70
                if is_glitch_in:
                    base_opacity *= (progress_elapsed / 15.0)
                elif is_glitch_out:
                    base_opacity *= (self.current_frame / 15.0)
                    
                if is_glitch_in or is_glitch_out:
                    base_opacity *= random.uniform(0.2, 0.9)
                    
                j_tint = resized_bgr.copy()
                jb, jg, jr = cv2.split(j_tint)
                j_tint = cv2.merge((jb, (jg * 0.75).astype(np.uint8), np.clip(jr * 1.3, 0, 255).astype(np.uint8)))
                
                for c in range(3):
                    roi[:, :, c] = (roi[:, :, c] * (1.0 - resized_alpha * base_opacity) + 
                                    j_tint[:, :, c] * (resized_alpha * base_opacity)).astype(np.uint8)
                frame[ov_y:ov_y+ov_h, ov_x:ov_x+ov_w] = roi
                
                for sy in range(ov_y, ov_y + ov_h, 6):
                    frame[sy:sy+1, ov_x:ov_x+ov_w] = (frame[sy:sy+1, ov_x:ov_x+ov_w] * 0.85).astype(np.uint8)
                    
                cv2.rectangle(frame, (ov_x, ov_y), (ov_x+ov_w, ov_y+ov_h), (255, 0, 255), 2)
                cv2.putText(frame, "🎸 JOHNNY SILVERHAND // HOLOGRAM", (ov_x + 10, ov_y - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 255), 1)
        else:
            box_w, box_h = 470, 115
            box_x = w - box_w - 20
            box_y = h - box_h - 50
            
            roi = frame[box_y:box_y+box_h, box_x:box_x+box_w]
            if roi.shape[0] == box_h and roi.shape[1] == box_w:
                flicker_alpha = 0.65
                if is_glitch_in:
                    flicker_alpha *= (progress_elapsed / 15.0)
                elif is_glitch_out:
                    flicker_alpha *= (self.current_frame / 15.0)
                flicker_alpha = max(0.15, min(0.85, flicker_alpha))
                
                bg = np.zeros_like(roi, dtype=np.uint8)
                bg[:, :, 0] = 60
                bg[:, :, 2] = 85
                blended = cv2.addWeighted(roi, 1.0 - flicker_alpha, bg, flicker_alpha, 0)
                frame[box_y:box_y+box_h, box_x:box_x+box_w] = blended
                
                border_c = (0, 0, 255) if (is_glitch_in or is_glitch_out or random.random() < 0.15) else (0, 255, 255)
                cv2.rectangle(frame, (box_x, box_y), (box_x+box_w, box_y+box_h), border_c, 2)
                
                av_w = 70
                cv2.rectangle(frame, (box_x + 10, box_y + 10), (box_x + 10 + av_w, box_y + 10 + av_w), (255, 0, 255), 1)
                cv2.putText(frame, "J.S.", (box_x + 24, box_y + 52), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)
                
                av_scan_y = box_y + 10 + ((self.total_duration - self.current_frame) * 4 % av_w)
                cv2.line(frame, (box_x + 10, av_scan_y), (box_x + 10 + av_w, av_scan_y), (0, 255, 255), 2)
                
                cv2.putText(frame, "🎸 [JOHNNY_SILVERHAND_HOLOGRAM]", (box_x + 90, box_y + 26),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 255), 2)
                
                words = self.active_quote.split()
                line1 = " ".join(words[:6])
                line2 = " ".join(words[6:])
                
                cv2.putText(frame, f'"{line1}', (box_x + 90, box_y + 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1)
                if line2:
                    cv2.putText(frame, f' {line2}"', (box_x + 90, box_y + 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 150), 1)
                    
                cv2.putText(frame, "[RELIC_CONSTRUCT // JOHNNY_SILVERHAND // AUDIO_LINK_ESTABLISHED]", 
                            (box_x + 90, box_y + 95), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (0, 0, 255), 1)

        banner_w, banner_h = 490, 28
        banner_x = (w - banner_w) // 2
        banner_y = 10
        cv2.rectangle(frame, (banner_x, banner_y), (banner_x + banner_w, banner_y + banner_h), (0, 0, 180), -1)
        cv2.rectangle(frame, (banner_x, banner_y), (banner_x + banner_w, banner_y + banner_h), (0, 255, 255), 1)
        cv2.putText(frame, "⚠️ RELIC MALFUNCTION DETECTED // BIOPORT OVERHEAT", (banner_x + 12, banner_y + 19),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

# --- CYBER VISION FX FILTERS ---
def apply_vision_filter(img, mode_idx):
    if mode_idx == 1: # THERMAL
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thermal = cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)
        return cv2.addWeighted(img, 0.25, thermal, 0.75, 0)
    elif mode_idx == 2: # NIGHT VISION GREEN
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        boosted = cv2.equalizeHist(gray)
        nv = np.zeros_like(img)
        nv[:, :, 1] = boosted 
        nv[:, :, 0] = (boosted * 0.15).astype(np.uint8)
        nv[:, :, 2] = (boosted * 0.05).astype(np.uint8)
        return nv
    elif mode_idx == 3: # SONAR EDGE SCAN
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_img = np.zeros_like(img)
        edge_img[:, :, 0] = edges
        edge_img[:, :, 1] = edges
        dark_base = (img * 0.25).astype(np.uint8)
        return cv2.addWeighted(dark_base, 0.8, edge_img, 1.0, 0)
    elif mode_idx == 4: # UNDERWATER CLAHE CONTRAST BOOST
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return img

# --- CYBERPUNK TARGET DRAWING HELPER ---
def draw_cyberpunk_target(img, box, track_id, species_name, conf, is_selected=False, is_active=True):
    x1, y1, x2, y2 = map(int, box)
    w = x2 - x1
    h = y2 - y1
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    
    if is_selected:
        color = (255, 255, 0)
        line_w = 3
    else:
        color = (0, 255, 255) if is_active else (150, 150, 150)
        line_w = 2
        
    cl = max(10, min(w, h) // 4)
    
    cv2.line(img, (x1, y1), (x1 + cl, y1), color, line_w)
    cv2.line(img, (x1, y1), (x1, y1 + cl), color, line_w)
    cv2.line(img, (x2, y1), (x2 - cl, y1), color, line_w)
    cv2.line(img, (x2, y1), (x2, y1 + cl), color, line_w)
    cv2.line(img, (x1, y2), (x1 + cl, y2), color, line_w)
    cv2.line(img, (x1, y2), (x1, y2 - cl), color, line_w)
    cv2.line(img, (x2, y2), (x2 - cl, y2), color, line_w)
    cv2.line(img, (x2, y2), (x2, y2 - cl), color, line_w)
    
    cv2.line(img, (cx - 8, cy), (cx + 8, cy), color, 1)
    cv2.line(img, (cx, cy - 8), (cx, cy + 8), color, 1)
    if is_selected:
        cv2.circle(img, (cx, cy), 18, (255, 255, 0), 2)
    
    lock_tag = "[LOCKED TARGET] " if is_selected else ""
    badge_text = f"{lock_tag}ID #{track_id} | {species_name.upper()} | {conf*100:.0f}%"
    badge_text = fit_text_to_width(badge_text, max_pixel_width=w + 80, font_scale=0.42)
    
    t_size = cv2.getTextSize(badge_text, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)[0]
    badge_w = t_size[0] + 10
    
    cv2.rectangle(img, (x1, y1 - 22), (x1 + badge_w, y1 - 2), (10, 15, 25), -1)
    cv2.rectangle(img, (x1, y1 - 22), (x1 + badge_w, y1 - 2), color, 1)
    cv2.putText(img, badge_text, (x1 + 5, y1 - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1)
    
    coord_text = f"X:{cx} Y:{cy}"
    cv2.putText(img, coord_text, (x1, y2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 255), 1)

# --- TACTICAL SONAR GRID OVERLAY ---
def draw_sonar_grid(img):
    h, w = img.shape[:2]
    color = (0, 180, 255)
    
    for x in range(0, w, 160):
        cv2.line(img, (x, 0), (x, h), (40, 40, 50), 1)
        cv2.putText(img, f"{x}px", (x + 3, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (120, 120, 140), 1)
    for y in range(0, h, 120):
        cv2.line(img, (0, y), (w, y), (40, 40, 50), 1)
        cv2.putText(img, f"{y}px", (5, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (120, 120, 140), 1)
        
    cx, cy = w // 2, h // 2
    cv2.drawMarker(img, (cx, cy), color, cv2.MARKER_CROSS, 40, 1)
    cv2.circle(img, (cx, cy), 120, color, 1)
    cv2.circle(img, (cx, cy), 240, color, 1)

# --- INTERACTIVE BUTTON CLASS FOR MOUSE CLICKING ---
class CyberButton:
    def __init__(self, x, y, w, h, label, callback_id, color=(0, 255, 255)):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        self.callback_id = callback_id
        self.color = color

    def contains(self, mx, my):
        return self.x <= mx <= self.x + self.w and self.y <= my <= self.y + self.h

    def draw(self, img, is_hovered=False):
        roi = img[self.y:self.y+self.h, self.x:self.x+self.w]
        if roi.shape[0] == self.h and roi.shape[1] == self.w:
            bg = np.zeros_like(roi, dtype=np.uint8)
            bg[:] = (35, 45, 65) if is_hovered else (18, 24, 38)
            blended = cv2.addWeighted(roi, 0.15, bg, 0.85, 0)
            img[self.y:self.y+self.h, self.x:self.x+self.w] = blended
            
            border_color = (255, 0, 255) if is_hovered else self.color
            cv2.rectangle(img, (self.x, self.y), (self.x+self.w, self.y+self.h), border_color, 1)
            
            lbl_text = fit_text_to_width(self.label, max_pixel_width=self.w - 10, font_scale=0.36)
            t_size = cv2.getTextSize(lbl_text, cv2.FONT_HERSHEY_SIMPLEX, 0.36, 1)[0]
            tx = self.x + (self.w - t_size[0]) // 2
            ty = self.y + (self.h + t_size[1]) // 2
            cv2.putText(img, lbl_text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.36, border_color, 1)

# --- GLOBAL INTERACTIVE STATE & MOUSE CALLBACK ---
current_fx_idx = 0
vision_fx_names = ["NORMAL", "THERMAL", "NIGHT VISION", "SONAR EDGE", "CLAHE"]
selectable_filters = ["ALL OBJECTS", "Salmo trutta", "FISH ONLY"]
current_filter_idx = 0

show_heatmap = True
show_motion_vectors = True
show_sonar_grid = False
show_pip_zoom = True
hud_mode = 0
conf_threshold = 0.40

# Chat Input & Dr. Pauly Visual Dialogue State
chat_mode_active = False
user_chat_buffer = ""
pauly_active_dialogue = ""

# --- 4. PAULY ALPHA FADE STATE MACHINE ---
pauly_ui_alpha = 0.0          # 0.0 to 1.0 smooth alpha blend factor
pauly_fade_state = "IDLE"     # "IDLE", "FADE_IN", "ACTIVE", "READING_GRACE", "FADE_OUT"
pauly_reading_timer = 0       # 90 frames (~3.0 sec) reading grace timer

def update_pauly_fade_state_machine():
    global pauly_ui_alpha, pauly_fade_state, pauly_reading_timer, ACTIVE_COMM, pauly_active_dialogue
    
    if pauly_fade_state == "FADE_IN":
        pauly_ui_alpha = min(1.0, pauly_ui_alpha + 1.0 / 30.0)
        if pauly_ui_alpha >= 1.0:
            pauly_fade_state = "ACTIVE"
            
    elif pauly_fade_state == "ACTIVE":
        if not is_pauly_speaking():
            pauly_fade_state = "READING_GRACE"
            pauly_reading_timer = 90  # 3 seconds grace period to read dialogue
            
    elif pauly_fade_state == "READING_GRACE":
        pauly_reading_timer -= 1
        if pauly_reading_timer <= 0:
            pauly_fade_state = "FADE_OUT"
            
    elif pauly_fade_state == "FADE_OUT":
        pauly_ui_alpha = max(0.0, pauly_ui_alpha - 1.0 / 30.0)
        if pauly_ui_alpha <= 0.0:
            pauly_fade_state = "IDLE"
            pauly_active_dialogue = ""
            if ACTIVE_COMM == "PAULY":
                ACTIVE_COMM = None

locked_target = None
active_boxes = []

mouse_pos = (0, 0)
action_trigger = None

def on_mouse_event(event, x, y, flags, param):
    global mouse_pos, action_trigger, locked_target
    mouse_pos = (x, y)
    
    if event == cv2.EVENT_LBUTTONDOWN:
        for btn in param['buttons']:
            if btn.contains(x, y):
                action_trigger = btn.callback_id
                return
        
        if x < param['video_w']:
            clicked_on_fish = False
            for box, tid, sp_n, conf_val, (cx, cy) in active_boxes:
                bx1, by1, bx2, by2 = map(int, box)
                if bx1 <= x <= bx2 and by1 <= y <= by2:
                    locked_target = {
                        "id": tid,
                        "species": sp_n,
                        "last_center": (cx, cy),
                        "lost_frames": 0,
                        "box": box,
                        "conf": conf_val
                    }
                    clicked_on_fish = True
                    param['hud_notifs'].add(f"🎯 TARGET LOCKED: ID #{tid} ({sp_n.upper()})", (255, 255, 0), 3.0)
                    
                    if sp_n not in GLOBAL_SPECIES_IMAGES:
                        threading.Thread(target=async_preload_species_image, args=(sp_n,), daemon=True).start()
                    break
            
            if not clicked_on_fish:
                locked_target = None

# --- 5. VIDEO PROCESSING SETUP WITH DYNAMIC SCREEN SCALING ---
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"❌ ERROR: Cannot load video at {video_path}")
    exit()

raw_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
raw_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
if fps <= 0:
    fps = 30

max_target_h = 900
if raw_h > max_target_h:
    scale_factor = float(max_target_h) / float(raw_h)
    video_w = int(raw_w * scale_factor)
    video_h = max_target_h
    print(f"📐 Dynamic UI Scale Applied: {raw_w}x{raw_h} -> {video_w}x{video_h} (scale={scale_factor:.3f})")
else:
    scale_factor = 1.0
    video_w = raw_w
    video_h = raw_h

sidebar_w = 420
canvas_w = video_w + sidebar_w
canvas_h = video_h

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (canvas_w, canvas_h))

window_name = "Spreewald Cyberpunk Vision Telemetry"
cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

buffer_duration_sec = 2.0
buffer_frames = int(buffer_duration_sec * fps)
pre_buffer = deque(maxlen=buffer_frames)
is_recording = False
post_record_counter = 0

hud_notifs = HUDNotificationManager()
johnny_relic = JohnnySilverhandRelicConstruct(fps)

all_unique_ids = set()
known_species_dialogue = {} 
queued_dialogue = set()     
recent_gbif_species = deque(maxlen=4) 
master_script = ""

track_history = defaultdict(lambda: deque(maxlen=30))
heatmap_acc = np.zeros((video_h, video_w), dtype=np.float32)

cv2.setMouseCallback(window_name, on_mouse_event, param={'buttons': [], 'hud_notifs': hud_notifs, 'video_w': video_w})

hud_notifs.add(f"⚡ DYNAMIC CASCADING Y-ENGINE ONLINE // SCALE: {video_w}x{video_h}", (0, 255, 255), 4.0)
hud_notifs.add("🌿 GBIF OCCURRENCE API + PERSISTENT MEMORY CACHE ACTIVE", (255, 255, 0), 4.0)

prev_time = time.time()
fps_smooth = 0.0
frame_counter = 0

# --- 6. MAIN LOOP ---
while cap.isOpened():
    success, raw_frame_full = cap.read()
    if not success:
        break

    frame_counter += 1
    curr_time = time.time()
    elapsed = curr_time - prev_time
    prev_time = curr_time
    instant_fps = (1.0 / elapsed) if elapsed > 0 else float(fps)
    fps_smooth = instant_fps if fps_smooth == 0.0 else (0.9 * fps_smooth + 0.1 * instant_fps)

    update_pauly_fade_state_machine()

    if scale_factor != 1.0:
        raw_frame = cv2.resize(raw_frame_full, (video_w, video_h))
    else:
        raw_frame = raw_frame_full

    canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)

    # 1. APPLY OPTICAL VISION FILTER TO VIDEO FRAME
    filtered_frame = apply_vision_filter(raw_frame, current_fx_idx)
    frame = filtered_frame.copy()

    # 2. ANIMATED WATER GIF OVERLAY [W]
    if show_water_gif and water_gif_cap is not None:
        ret_g, gif_frame = water_gif_cap.read()
        if not ret_g:
            water_gif_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret_g, gif_frame = water_gif_cap.read()
        if ret_g and gif_frame is not None:
            resized_gif = cv2.resize(gif_frame, (video_w, video_h))
            frame = cv2.addWeighted(frame, 0.80, resized_gif, 0.20, 0)

    # 3. DRAW BACKGROUND VFX
    draw_cyberpunk_background_vfx(frame, frame_counter)

    # 4. DRAW SONAR GRID IF ENABLED
    if show_sonar_grid:
        draw_sonar_grid(frame)

    active_filter = selectable_filters[current_filter_idx]

    # Run YOLO tracking on detected hardware device
    results = model.track(frame, persist=True, tracker="botsort.yaml", device=active_device, conf=conf_threshold, verbose=False)

    has_high_conf_detection = False
    best_target_crop = None
    best_target_info = None
    current_frame_detections = []
    active_boxes.clear()

    if results[0].boxes is not None and results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        track_ids = results[0].boxes.id.cpu().numpy()
        class_indices = results[0].boxes.cls.cpu().numpy()
        confidences = results[0].boxes.conf.cpu().numpy()
        names = results[0].names

        for cls_i in class_indices:
            sp_n = names[int(cls_i)]
            sp_clean = sp_n if sp_n.lower() != "fish" else "Salmo trutta"
            if sp_clean not in selectable_filters:
                selectable_filters.append(sp_clean)

        for box, track_id, cls_idx, conf in zip(boxes, track_ids, class_indices, confidences):
            tid = int(track_id)
            species_name = names[int(cls_idx)]
            search_species = species_name if species_name.lower() != "fish" else "Salmo trutta"

            if active_filter == "FISH ONLY" and "fish" not in species_name.lower() and "salmo" not in search_species.lower():
                continue
            elif active_filter not in ["ALL OBJECTS", "FISH ONLY"] and search_species.lower() != active_filter.lower():
                continue

            all_unique_ids.add(tid)
            x1, y1, x2, y2 = map(int, box)
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            active_boxes.append((box, tid, search_species, conf, (center_x, center_y)))
            current_frame_detections.append((box, tid, search_species, conf, (center_x, center_y)))

            if conf > 0.75:
                has_high_conf_detection = True

            track_history[tid].append((center_x, center_y))

            if 0 <= center_x < video_w and 0 <= center_y < video_h:
                cv2.circle(heatmap_acc, (center_x, center_y), radius=15, color=1.0, thickness=-1)

            if show_motion_vectors and len(track_history[tid]) > 1:
                pts = np.array(track_history[tid], dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], isClosed=False, color=(0, 255, 255), thickness=2)
                p1 = track_history[tid][-2]
                p2 = track_history[tid][-1]
                cv2.arrowedLine(frame, p1, p2, (255, 255, 0), 2, tipLength=0.4)

            # Fire asynchronous background image fetch for newly detected species
            if search_species not in GLOBAL_SPECIES_IMAGES:
                threading.Thread(target=async_preload_species_image, args=(search_species,), daemon=True).start()

            if search_species not in known_species_dialogue:
                hud_notifs.add(f"🐟 GBIF TAXONOMY: {search_species.upper()}", (0, 255, 255), 3.0)
                fish_data = fetch_gbif_data(search_species)
                pauly_dialogue = ask_dr_pauly(search_species, biology_data=fish_data, lang=language_mode)
                known_species_dialogue[search_species] = pauly_dialogue

                gbif_name = fish_data.get("Scientific Name", search_species)
                if gbif_name not in recent_gbif_species:
                    recent_gbif_species.append(gbif_name)

            if search_species not in queued_dialogue:
                queued_dialogue.add(search_species)
                master_script += known_species_dialogue[search_species] + " "

    # STICKY TARGET LOCKING UPDATE
    locked_target = update_sticky_target_lock(locked_target, current_frame_detections, max_dist=100, max_lost_frames=30)
    locked_id = locked_target["id"] if locked_target is not None else None

    # Draw target reticles and evaluate best crop
    for box, tid, search_species, conf, (center_x, center_y) in current_frame_detections:
        is_curr_locked = (locked_id == tid)
        
        if is_curr_locked or (best_target_crop is None and locked_id is None) or (locked_id is None and conf > best_target_info[1]):
            x1, y1, x2, y2 = map(int, box)
            x1_c, y1_c = max(0, x1), max(0, y1)
            x2_c, y2_c = min(video_w, x2), min(video_h, y2)
            crop_sub = raw_frame[y1_c:y2_c, x1_c:x2_c]
            if crop_sub.size > 0:
                best_target_crop = crop_sub
                best_target_info = (tid, conf, search_species)

        draw_cyberpunk_target(frame, box, tid, search_species, conf, is_selected=is_curr_locked, is_active=(conf > 0.75))

    # TRAJECTORY HEATMAP LAYER
    if show_heatmap:
        max_heat = np.max(heatmap_acc)
        if max_heat > 0:
            blurred_heat = cv2.GaussianBlur(heatmap_acc, (31, 31), 0)
            max_blurred = np.max(blurred_heat)
            if max_blurred > 0:
                norm_heat = np.clip((blurred_heat / max_blurred) * 255.0, 0, 255).astype(np.uint8)
                heatmap_color = cv2.applyColorMap(norm_heat, cv2.COLORMAP_JET)
                heat_mask = norm_heat > 15
                frame[heat_mask] = cv2.addWeighted(frame[heat_mask], 0.70, heatmap_color[heat_mask], 0.30, 0)

    # PICTURE-IN-PICTURE (PiP) MAGNIFIER ZOOM WINDOW
    if show_pip_zoom and best_target_crop is not None:
        pip_w, pip_h = 160, 160
        pip_x = video_w - pip_w - 20
        pip_y = video_h - pip_h - 20
        
        resized_crop = cv2.resize(best_target_crop, (pip_w, pip_h))
        frame[pip_y:pip_y+pip_h, pip_x:pip_x+pip_w] = resized_crop
        border_c = (255, 255, 0) if (best_target_info and best_target_info[0] == locked_id) else (0, 255, 255)
        cv2.rectangle(frame, (pip_x, pip_y), (pip_x+pip_w, pip_y+pip_h), border_c, 2)
        
        tid_z, conf_z, sp_z = best_target_info
        lock_lbl = " [LOCKED]" if tid_z == locked_id else ""
        cv2.putText(frame, f"ZOOM 2.0x{lock_lbl} | ID #{tid_z}", (pip_x + 5, pip_y - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, border_c, 1)

    # JOHNNY SILVERHAND RELIC CONSTRUCT STATE MACHINE [J]
    johnny_relic.check_auto_trigger(frame_counter, hud_notifs)
    johnny_relic.draw(frame, hud_notifs)

    hud_notifs.draw(frame)

    # COPY VIDEO FRAME TO LEFT PANEL OF CANVAS
    canvas[:, :video_w] = frame

    # --- 7. RENDER RIGHT SIDEBAR TELEMETRY COLUMN WITH DYNAMIC Y-STACKING ---
    sidebar = canvas[:, video_w:]
    sidebar[:] = (15, 22, 35)
    
    cv2.rectangle(sidebar, (2, 2), (sidebar_w - 2, canvas_h - 2), (255, 255, 0), 1)
    cv2.rectangle(sidebar, (5, 5), (sidebar_w - 5, canvas_h - 5), (255, 0, 255), 1)

    current_y = 15

    # SIDEBAR HEADER BOX
    cv2.rectangle(sidebar, (15, current_y), (sidebar_w - 15, current_y + 40), (25, 35, 55), -1)
    cv2.rectangle(sidebar, (15, current_y), (sidebar_w - 15, current_y + 40), (0, 255, 255), 1)
    cv2.putText(sidebar, "⚡ SPREEWALD CYBERDECK ⚡", (30, current_y + 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.58, (0, 255, 255), 2)
    current_y += 50

    # PANEL 1: SYSTEM TELEMETRY & HARDWARE
    cv2.rectangle(sidebar, (15, current_y), (sidebar_w - 15, current_y + 80), (20, 28, 42), -1)
    cv2.rectangle(sidebar, (15, current_y), (sidebar_w - 15, current_y + 80), (100, 100, 120), 1)
    
    comm_lbl = f"COMM: {ACTIVE_COMM}" if ACTIVE_COMM else "COMM: IDLE"
    cv2.putText(sidebar, f"TELEMETRY [{language_mode}] | {comm_lbl}", (25, current_y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 150), 1)
    
    cv2.putText(sidebar, f"FPS: {fps_smooth:.1f} | SCALE: {video_w}x{video_h}", (25, current_y + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)
    
    hw_str = fit_text_to_width(hw_telemetry_status, max_pixel_width=360)
    cv2.putText(sidebar, f"{hw_str}", (25, current_y + 58),
                cv2.FONT_HERSHEY_SIMPLEX, 0.36, (200, 200, 200), 1)
    
    rec_lbl = "RECORDING ACTIVE" if is_recording else "STANDBY (BUFFER)"
    cv2.putText(sidebar, f"REC: {rec_lbl}", (25, current_y + 74),
                cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 255, 0) if is_recording else (0, 165, 255), 1)
    current_y += 90

    # PANEL 2: GBIF MEMORY CACHED IMAGE & TARGET LOCK DETAILS
    cv2.rectangle(sidebar, (15, current_y), (sidebar_w - 15, current_y + 115), (20, 28, 42), -1)
    cv2.rectangle(sidebar, (15, current_y), (sidebar_w - 15, current_y + 115), (255, 255, 0) if locked_target else (100, 100, 120), 1)

    target_sp_name = locked_target["species"] if locked_target else (best_target_info[2] if best_target_info else "Salmo trutta")
    
    cached_img_obj = GLOBAL_SPECIES_IMAGES.get(target_sp_name)
    if isinstance(cached_img_obj, np.ndarray):
        thumb_res = cv2.resize(cached_img_obj, (80, 80))
        sidebar[current_y+25:current_y+105, 25:105] = thumb_res
        cv2.rectangle(sidebar, (25, current_y+25), (105, current_y+105), (0, 255, 255), 1)
        cv2.putText(sidebar, "GBIF CACHE", (28, current_y + 19), cv2.FONT_HERSHEY_SIMPLEX, 0.30, (0, 255, 255), 1)
    elif best_target_crop is not None:
        t_crop_res = cv2.resize(best_target_crop, (80, 80))
        sidebar[current_y+25:current_y+105, 25:105] = t_crop_res
        cv2.rectangle(sidebar, (25, current_y+25), (105, current_y+105), (255, 255, 0), 1)
        cv2.putText(sidebar, "YOLO CROP", (30, current_y + 19), cv2.FONT_HERSHEY_SIMPLEX, 0.30, (255, 255, 0), 1)

    cv2.putText(sidebar, "🎯 TARGET SPECIMEN DETAILS", (115, current_y + 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 255), 1)
    
    if locked_target is not None:
        cv2.putText(sidebar, f"ID: #{locked_target['id']} | CONF: {locked_target['conf']*100:.0f}%", 
                    (115, current_y + 44), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 0), 1)
        sp_line = fit_text_to_width(f"Species: {locked_target['species']}", max_pixel_width=270)
        cv2.putText(sidebar, sp_line, (115, current_y + 64), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1)
        lost_f = locked_target["lost_frames"]
        st_lbl = "STICKY LOCK" if lost_f == 0 else f"TRACKING ({30-lost_f}f)"
        cv2.putText(sidebar, f"Status: {st_lbl}", (115, current_y + 84), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 255, 150), 1)
    else:
        cv2.putText(sidebar, "AUTO SCANNING MODE", (115, current_y + 48), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (150, 150, 150), 1)
        cv2.putText(sidebar, "Click fish to lock target", (115, current_y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (120, 120, 120), 1)
    current_y += 125

    # PANEL 3: DR. PAULY VISUAL DIALOGUE & CONTINUOUS GBIF / WIKIMEDIA IMAGE
    if pauly_ui_alpha > 0.0 and pauly_active_dialogue:
        if scuba_pauly_img is not None:
            sp_w, sp_h = 45, 45
            resized_sp = cv2.resize(scuba_pauly_img[:, :, :3] if scuba_pauly_img.shape[2]==4 else scuba_pauly_img, (sp_w, sp_h))
            sidebar[current_y:current_y+sp_h, 20:20+sp_w] = resized_sp
            cv2.rectangle(sidebar, (20, current_y), (20+sp_w, current_y+sp_h), (0, 255, 255), 1)
            
        cv2.putText(sidebar, f"🤿 DR. PAULY HUD [{language_mode}]", (72, current_y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 255, 255), 1)
                    
        next_y = draw_wrapped_text(sidebar, pauly_active_dialogue, start_x=20, start_y=current_y + 22, max_w=380, max_lines=3, font_scale=0.34, bg_alpha=pauly_ui_alpha)
        current_y = max(current_y + 80, next_y)

        # RENDER PERSISTENT GBIF ECOLOGICAL SPECIES IMAGE SNAPSHOT
        img_state = GLOBAL_SPECIES_IMAGES.get(target_sp_name)
        if isinstance(img_state, np.ndarray):
            img_h, img_w = img_state.shape[:2] # 220, 380
            img_x = 20
            sidebar[current_y : current_y + img_h, img_x : img_x + img_w] = img_state
            cv2.rectangle(sidebar, (img_x, current_y), (img_x + img_w, current_y + img_h), (0, 255, 255), 1)
            cv2.putText(sidebar, "GBIF ECOLOGICAL SPECIES SNAPSHOT", (img_x + 10, current_y - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, (0, 255, 255), 1)
            current_y += img_h + 15
        elif img_state == "FAILED":
            cv2.rectangle(sidebar, (20, current_y), (380 + 20, current_y + 120), (20, 28, 42), -1)
            cv2.rectangle(sidebar, (20, current_y), (380 + 20, current_y + 120), (0, 0, 255), 1)
            cv2.putText(sidebar, "[IMAGE NOT FOUND IN ECOLOGICAL DATABANKS]", (25, current_y + 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, (0, 0, 255), 1)
            current_y += 135
        else: # None -> Asynchronous Download in progress
            cv2.rectangle(sidebar, (20, current_y), (380 + 20, current_y + 120), (20, 28, 42), -1)
            cv2.rectangle(sidebar, (20, current_y), (380 + 20, current_y + 120), (0, 255, 255), 1)
            cv2.putText(sidebar, "[DOWNLOADING SECURE ECOLOGICAL DATA...]", (28, current_y + 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, (0, 255, 255), 1)
            current_y += 135
    else:
        current_y += 10

    # DYNAMICALLY REPOSITION SIDEBAR BUTTON DOCK
    sb_x = video_w + 15
    btn_start_y = current_y

    buttons = [
        CyberButton(sb_x, btn_start_y, 125, 26, "[S] FILTER", "toggle_filter", (0, 255, 255)),
        CyberButton(sb_x + 135, btn_start_y, 125, 26, "[F] FX", "toggle_fx", (255, 255, 0)),
        CyberButton(sb_x + 270, btn_start_y, 120, 26, "[V] VEC", "toggle_vec", (0, 255, 150)),
        
        CyberButton(sb_x, btn_start_y + 32, 125, 26, "[H] HEAT", "toggle_heat", (255, 0, 255)),
        CyberButton(sb_x + 135, btn_start_y + 32, 125, 26, "[G] SONAR", "toggle_sonar", (0, 180, 255)),
        CyberButton(sb_x + 270, btn_start_y + 32, 120, 26, "[Z] ZOOM", "toggle_pip", (255, 255, 0)),
        
        CyberButton(sb_x, btn_start_y + 64, 125, 26, "CONF [+]", "conf_inc", (0, 255, 150)),
        CyberButton(sb_x + 135, btn_start_y + 64, 125, 26, "CONF [-]", "conf_dec", (0, 255, 150)),
        CyberButton(sb_x + 270, btn_start_y + 64, 120, 26, f"[L] LANG: {language_mode}", "toggle_lang", (0, 255, 255)),
        
        CyberButton(sb_x, btn_start_y + 96, 190, 26, "[W] WATER GIF", "toggle_gif", (0, 255, 255)),
        CyberButton(sb_x + 200, btn_start_y + 96, 190, 26, "[CTRL+T] CHAT", "toggle_chat", (255, 255, 0)),
        
        CyberButton(sb_x, btn_start_y + 128, 390, 28, "📞 [C] CALL DR. PAULY", "call_pauly", (0, 255, 0)),
        CyberButton(sb_x, btn_start_y + 160, 390, 28, "🎸 [J] JOHNNY RELIC", "trigger_johnny", (255, 0, 255))
    ]

    cv2.setMouseCallback(window_name, on_mouse_event, param={'buttons': buttons, 'hud_notifs': hud_notifs, 'video_w': video_w})

    # RENDER INTERACTIVE DOCK BUTTONS INSIDE SIDEBAR
    for btn in buttons:
        btn.draw(canvas, is_hovered=btn.contains(mouse_pos[0], mouse_pos[1]))

    # LIVE OPENCV CHAT INPUT DISPLAY BAR [CTRL+T]
    chat_y = canvas_h - 105
    cv2.rectangle(sidebar, (15, chat_y), (sidebar_w - 15, chat_y + 35), (10, 18, 30), -1)
    border_chat_c = (0, 255, 255) if chat_mode_active else (80, 80, 100)
    cv2.rectangle(sidebar, (15, chat_y), (sidebar_w - 15, chat_y + 35), border_chat_c, 1)
    
    cursor_str = "_" if (chat_mode_active and int(time.time()*2)%2==0) else ""
    chat_lbl = f"USER CHAT [CTRL+T]: {user_chat_buffer}{cursor_str}"
    chat_lbl = fit_text_to_width(chat_lbl, max_pixel_width=360, font_scale=0.36)
    cv2.putText(sidebar, chat_lbl, (25, chat_y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 255, 255) if chat_mode_active else (180, 180, 180), 1)

    # PANEL 4: HOTKEY LEGEND
    p4_y = canvas_h - 65
    cv2.rectangle(sidebar, (15, p4_y), (sidebar_w - 15, canvas_h - 15), (20, 28, 42), -1)
    cv2.rectangle(sidebar, (15, p4_y), (sidebar_w - 15, canvas_h - 15), (0, 255, 255), 1)
    cv2.putText(sidebar, f"[L]: LANG ({language_mode}) | [C]: Pauly | [J]: Johnny", (25, p4_y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.34, (0, 255, 255), 1)
    cv2.putText(sidebar, "[CTRL+T]: Chat | [S]: Filter | [W]: Gif | [Q]: Quit", (25, p4_y + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.34, (255, 255, 255), 1)

    # SMART EVENT SLICING LOGIC
    if has_high_conf_detection:
        if not is_recording:
            is_recording = True
            while pre_buffer:
                out.write(pre_buffer.popleft())
        post_record_counter = buffer_frames
        out.write(canvas)
    else:
        if is_recording:
            out.write(canvas)
            post_record_counter -= 1
            if post_record_counter <= 0:
                is_recording = False
        else:
            pre_buffer.append(canvas.copy())

    # Render OpenCV Video Window
    cv2.imshow(window_name, canvas)
    
    # PROCESS MOUSE CLICK ACTION TRIGGERS
    if action_trigger:
        if action_trigger == "toggle_filter":
            current_filter_idx = (current_filter_idx + 1) % len(selectable_filters)
            active_f = selectable_filters[current_filter_idx]
            hud_notifs.add(f"🎯 TARGET FILTER: {active_f.upper()}", (0, 255, 255), 2.5)
        elif action_trigger == "toggle_fx":
            current_fx_idx = (current_fx_idx + 1) % len(vision_fx_names)
            fx_name = vision_fx_names[current_fx_idx]
            hud_notifs.add(f"👁️ VISION FX MODE: {fx_name}", (255, 255, 0), 2.5)
        elif action_trigger == "toggle_vec":
            show_motion_vectors = not show_motion_vectors
            hud_notifs.add(f"🚀 MOTION VECTORS: {'ENABLED' if show_motion_vectors else 'DISABLED'}", (0, 255, 255), 2.5)
        elif action_trigger == "toggle_heat":
            show_heatmap = not show_heatmap
            hud_notifs.add(f"🔥 HEATMAP: {'ENABLED' if show_heatmap else 'DISABLED'}", (255, 0, 255), 2.5)
        elif action_trigger == "toggle_sonar":
            show_sonar_grid = not show_sonar_grid
            hud_notifs.add(f"🌐 SONAR GRID OVERLAY: {'ENABLED' if show_sonar_grid else 'DISABLED'}", (0, 180, 255), 2.5)
        elif action_trigger == "toggle_pip":
            show_pip_zoom = not show_pip_zoom
            hud_notifs.add(f"🔍 MAGNIFIER PiP ZOOM: {'ENABLED' if show_pip_zoom else 'DISABLED'}", (0, 255, 255), 2.5)
        elif action_trigger == "toggle_lang":
            language_mode = "DE" if language_mode == "EN" else "EN"
            hud_notifs.add(f"🌐 LANGUAGE MODE: {language_mode}", (0, 255, 255), 2.5)
        elif action_trigger == "toggle_gif":
            show_water_gif = not show_water_gif
            hud_notifs.add(f"🌊 WATER GIF OVERLAY: {'ACTIVE' if show_water_gif else 'INACTIVE'}", (0, 255, 255), 2.5)
        elif action_trigger == "toggle_chat":
            chat_mode_active = not chat_mode_active
            user_chat_buffer = ""
            if chat_mode_active:
                hud_notifs.add("💬 CHAT MODE ACTIVE (CTRL+T TO CLOSE / ENTER TO SUBMIT)", (0, 255, 255), 3.5)
            else:
                hud_notifs.add("💬 CHAT MODE CLOSED", (255, 255, 0), 2.0)
        elif action_trigger == "conf_inc":
            conf_threshold = min(0.95, round(conf_threshold + 0.05, 2))
            hud_notifs.add(f"⚙️ CONF THRESHOLD: {conf_threshold:.2f}", (0, 255, 150), 2.5)
        elif action_trigger == "conf_dec":
            conf_threshold = max(0.15, round(conf_threshold - 0.05, 2))
            hud_notifs.add(f"⚙️ CONF THRESHOLD: {conf_threshold:.2f}", (0, 255, 150), 2.5)
        elif action_trigger == "call_pauly":
            if ACTIVE_COMM == "JOHNNY":
                hud_notifs.add("⛔ COMM LINK LOCKED: JOHNNY RELIC ACTIVE", (0, 0, 255), 2.5)
            elif is_pauly_speaking() or pauly_fade_state != "IDLE":
                stop_pauly_audio()
                pauly_fade_state = "FADE_OUT"
                hud_notifs.add("🛑 DR. PAULY CALL TERMINATED", (0, 0, 255), 2.5)
            else:
                target_species = locked_target["species"] if locked_target is not None else ("Salmo trutta" if len(recent_gbif_species)==0 else recent_gbif_species[-1])
                trigger_pauly_call(target_species)
        elif action_trigger == "trigger_johnny":
            if ACTIVE_COMM == "PAULY":
                hud_notifs.add("⛔ COMM LINK LOCKED: DR. PAULY CALL ACTIVE", (0, 0, 255), 2.5)
            elif johnny_relic.is_active:
                johnny_relic.cancel(hud_notifs)
            else:
                johnny_relic.trigger(hud_notifs)
        action_trigger = None

    # --- 5. DEDICATED USER CHAT INPUT MODE SUB-LOOP [CTRL+T / ASCII 20] ---
    if chat_mode_active:
        hud_notifs.add("💬 LIVE CHAT MODE: TYPE & PRESS ENTER (CTRL+T OR ESC TO CLOSE)", (0, 255, 255), 2.0)
        while chat_mode_active:
            sidebar = canvas[:, video_w:]
            chat_y = canvas_h - 105
            cv2.rectangle(sidebar, (15, chat_y), (sidebar_w - 15, chat_y + 35), (10, 18, 30), -1)
            cv2.rectangle(sidebar, (15, chat_y), (sidebar_w - 15, chat_y + 35), (0, 255, 255), 1)
            
            cursor_str = "_" if int(time.time()*3)%2==0 else ""
            chat_lbl = f"USER CHAT [CTRL+T]: {user_chat_buffer}{cursor_str}"
            chat_lbl = fit_text_to_width(chat_lbl, max_pixel_width=360, font_scale=0.36)
            cv2.putText(sidebar, chat_lbl, (25, chat_y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 255, 255), 1)
            
            cv2.imshow(window_name, canvas)
            c_key = cv2.waitKey(20) & 0xFF
            
            if c_key == 20: # CTRL + T -> CLOSE CHAT MODE
                chat_mode_active = False
                hud_notifs.add("💬 CHAT MODE CLOSED", (255, 255, 0), 2.0)
            elif c_key == 13: # ENTER KEY -> SUBMIT QUERY
                if user_chat_buffer.strip():
                    if ACTIVE_COMM == "JOHNNY":
                        hud_notifs.add("⛔ COMM LINK LOCKED: JOHNNY RELIC ACTIVE", (0, 0, 255), 2.5)
                    else:
                        target_species = locked_target["species"] if locked_target is not None else ("Salmo trutta" if len(recent_gbif_species)==0 else recent_gbif_species[-1])
                        trigger_pauly_call(target_species, user_question=user_chat_buffer)
                chat_mode_active = False
            elif c_key == 27: # ESC KEY -> CANCEL CHAT
                chat_mode_active = False
            elif c_key in [8, 127]: # BACKSPACE
                user_chat_buffer = user_chat_buffer[:-1]
            elif 32 <= c_key <= 126: # PRINTABLE ASCII
                if len(user_chat_buffer) < 42:
                    user_chat_buffer += chr(c_key)

    # --- 4. STANDARD SINGLE KEY LISTENERS (RESTORED DIRECT HOTKEYS) ---
    key = cv2.waitKey(1) & 0xFF
    
    if key == 20: # CTRL + T (ACTIVATE/DEACTIVATE CHAT MODE)
        chat_mode_active = not chat_mode_active
        user_chat_buffer = ""
        if chat_mode_active:
            hud_notifs.add("💬 CHAT MODE ACTIVE (CTRL+T TO CLOSE / ENTER TO SUBMIT)", (0, 255, 255), 3.5)
        else:
            hud_notifs.add("💬 CHAT MODE CLOSED", (255, 255, 0), 2.0)

    elif key == ord('q') or key == ord('Q'):  
        break
    elif key == ord('c') or key == ord('C'):
        if ACTIVE_COMM == "JOHNNY":
            hud_notifs.add("⛔ COMM LINK LOCKED: JOHNNY RELIC ACTIVE", (0, 0, 255), 2.5)
        elif is_pauly_speaking() or pauly_fade_state != "IDLE":
            stop_pauly_audio()
            pauly_fade_state = "FADE_OUT"
            hud_notifs.add("🛑 DR. PAULY CALL TERMINATED", (0, 0, 255), 2.5)
        else:
            target_species = locked_target["species"] if locked_target is not None else ("Salmo trutta" if len(recent_gbif_species)==0 else recent_gbif_species[-1])
            trigger_pauly_call(target_species)
    elif key == ord('j') or key == ord('J'):
        if ACTIVE_COMM == "PAULY":
            hud_notifs.add("⛔ COMM LINK LOCKED: DR. PAULY CALL ACTIVE", (0, 0, 255), 2.5)
        elif johnny_relic.is_active:
            johnny_relic.cancel(hud_notifs)
        else:
            johnny_relic.trigger(hud_notifs)
    elif key == ord('l') or key == ord('L'):
        language_mode = "DE" if language_mode == "EN" else "EN"
        hud_notifs.add(f"🌐 LANGUAGE MODE SET TO: {language_mode}", (0, 255, 255), 2.5)
    elif key == ord('w') or key == ord('W'):
        show_water_gif = not show_water_gif
        hud_notifs.add(f"🌊 WATER GIF OVERLAY: {'ACTIVE' if show_water_gif else 'INACTIVE'}", (0, 255, 255), 2.5)
    elif key == ord('s') or key == ord('S'):
        current_filter_idx = (current_filter_idx + 1) % len(selectable_filters)
        active_f = selectable_filters[current_filter_idx]
        hud_notifs.add(f"🎯 TARGET FILTER: {active_f.upper()}", (0, 255, 255), 2.5)
    elif key == ord('f') or key == ord('F'):
        current_fx_idx = (current_fx_idx + 1) % len(vision_fx_names)
        fx_name = vision_fx_names[current_fx_idx]
        hud_notifs.add(f"👁️ VISION FX MODE: {fx_name}", (255, 255, 0), 2.5)
    elif key == ord('v') or key == ord('V'):
        show_motion_vectors = not show_motion_vectors
        hud_notifs.add(f"🚀 MOTION VECTORS: {'ENABLED' if show_motion_vectors else 'DISABLED'}", (0, 255, 255), 2.5)
    elif key == ord('z') or key == ord('Z'):
        show_pip_zoom = not show_pip_zoom
        hud_notifs.add(f"🔍 MAGNIFIER PiP ZOOM: {'ENABLED' if show_pip_zoom else 'DISABLED'}", (0, 255, 255), 2.5)
    elif key == ord('g') or key == ord('G'):
        show_sonar_grid = not show_sonar_grid
        hud_notifs.add(f"🌐 SONAR GRID OVERLAY: {'ENABLED' if show_sonar_grid else 'DISABLED'}", (0, 255, 255), 2.5)
    elif key == ord('h') or key == ord('H'):
        show_heatmap = not show_heatmap
        hud_notifs.add(f"🔥 HEATMAP: {'ENABLED' if show_heatmap else 'DISABLED'}", (255, 0, 255), 2.5)
    elif key == ord('+') or key == ord('='):
        conf_threshold = min(0.95, round(conf_threshold + 0.05, 2))
        hud_notifs.add(f"⚙️ CONF THRESHOLD: {conf_threshold:.2f}", (0, 255, 150), 2.5)
    elif key == ord('-') or key == ord('_'):
        conf_threshold = max(0.15, round(conf_threshold - 0.05, 2))
        hud_notifs.add(f"⚙️ CONF THRESHOLD: {conf_threshold:.2f}", (0, 255, 150), 2.5)

cap.release()
out.release()
cv2.destroyAllWindows()
print(f"✅ Processing complete. Video saved to: {output_path}")
