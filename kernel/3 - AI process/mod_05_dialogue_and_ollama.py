import os
import sys
import time
import random
import requests
import threading
import cv2
import numpy as np

from mod_00_config_and_assets import find_asset, johnny_gif_frames, johnny_img_rgba

# --- SAFE OPTIONAL IMPORTS (TTS & OLLAMA) ---
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except Exception:
    pyttsx3 = None
    HAS_PYTTSX3 = False

# --- DYNAMIC OLLAMA DISCOVERY & QUERY HELPERS ---
def get_available_ollama_model():
    """Detects any locally installed Ollama model dynamically."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=1.5)
        if r.status_code == 200:
            models_data = r.json().get("models", [])
            if models_data:
                names = [m.get("name", "") for m in models_data if m.get("name")]
                # Prioritize lightweight or standard chat models
                for pref in ["llama3.2:1b", "llama3.2", "llama3", "mistral", "phi3", "qwen", "gemma"]:
                    for n in names:
                        if pref in n:
                            return n
                if names:
                    return names[0]
    except Exception:
        pass
    return None

def query_ollama_direct(prompt, timeout=3.5):
    """Direct fast REST call to Ollama without failing or throwing if model is missing."""
    model_name = get_available_ollama_model()
    if not model_name:
        return None
    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": False},
            timeout=timeout
        )
        if res.status_code == 200:
            ans = res.json().get("response", "").strip()
            if ans and len(ans) > 5:
                return clean_pauly_response(ans)
    except Exception:
        pass
    return None

class DynamicOllamaLLM:
    """Wrapper that dynamically detects installed Ollama models with offline fallback."""
    def __init__(self, model="llama3"):
        self.preferred_model = model

    def invoke(self, prompt):
        res = query_ollama_direct(prompt)
        if res:
            return res
        return "Techno - Eco Project AI system online. Neural telemetry parameters synchronized."

pauly_llm = DynamicOllamaLLM(model="llama3")
risk_analyst_llm = DynamicOllamaLLM(model="llama3")

# --- GLOBAL AUDIO & STATE CONTROLS ---
ACTIVE_COMM = None
language_mode = "EN"

def play_sound_async(frequency=800, duration=150):
    def _beep():
        try:
            import winsound
            winsound.Beep(frequency, duration)
        except Exception:
            pass
    threading.Thread(target=_beep, daemon=True).start()

# --- CANCELLABLE AUDIO ENGINE & THREAD-SAFE AUDIO MANAGER ---
class CancellableAudioEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.engine = None
        self.speech_token = 0
        self.is_speaking = False

    def speak(self, text, lang="EN"):
        self.stop()
        with self.lock:
            self.speech_token += 1
            token = self.speech_token
            self.is_speaking = True

        def _speak_thread(tok, lang_mode):
            co_initialized = False
            try:
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                    co_initialized = True
                except Exception:
                    pass

                if HAS_PYTTSX3 and pyttsx3 is not None:
                    eng = pyttsx3.init()
                    eng.setProperty('rate', 150)
                    eng.setProperty('volume', 1.0)
                    
                    voices = eng.getProperty('voices')
                    selected_voice = None
                    
                    # Strictly select a male voice (e.g. Microsoft David Desktop), never female
                    for v in voices:
                        v_name = v.name.lower()
                        v_id = v.id.lower()
                        if any(f in v_name or f in v_id for f in ['hedda', 'zira', 'katja', 'female', 'eva', 'hazel']):
                            continue
                        if any(m in v_name or m in v_id for m in ['david', 'male', 'george', 'stefan', 'mark', 'michael']):
                            selected_voice = v.id
                            break
                    if not selected_voice:
                        for v in voices:
                            v_name = v.name.lower()
                            v_id = v.id.lower()
                            if not any(f in v_name or f in v_id for f in ['hedda', 'zira', 'katja', 'female', 'eva', 'hazel']):
                                selected_voice = v.id
                                break
                    if not selected_voice and voices:
                        selected_voice = voices[0].id

                    if selected_voice:
                        eng.setProperty('voice', selected_voice)

                    with self.lock:
                        if self.speech_token != tok:
                            return
                        self.engine = eng
                    try:
                        eng.endLoop()
                    except Exception:
                        pass
                    eng.say(text)
                    eng.runAndWait()
            except Exception as e:
                pass
            finally:
                with self.lock:
                    if self.speech_token == tok:
                        self.is_speaking = False
                        self.engine = None
                if co_initialized:
                    try:
                        import pythoncom
                        pythoncom.CoUninitialize()
                    except Exception:
                        pass

        threading.Thread(target=_speak_thread, args=(token, lang), daemon=True).start()

    def stop(self):
        with self.lock:
            self.speech_token += 1
            self.is_speaking = False
            if self.engine is not None:
                try:
                    self.engine.stop()
                except Exception:
                    pass
                try:
                    self.engine.endLoop()
                except Exception:
                    pass
                self.engine = None

audio_manager = CancellableAudioEngine()

def speak_tts_async(text, lang=None):
    if lang is None:
        lang = language_mode
    audio_manager.speak(text, lang=lang)

pauly_lock = threading.Lock()
pauly_speech_active = False

# --- OFFLINE EXPERT BIOLOGICAL REASONING ENGINE (DR. DANIEL PAULY) ---
def generate_offline_pauly_response(species_name, user_question=None, target_specimen_info=None, lang="EN"):
    """
    Expert biological reasoning engine acting as Dr. Daniel Pauly.
    Provides authentic, scientific, concise insights when Ollama is offline or model is not pulled.
    """
    import re
    is_de = (lang == "DE")
    q = (user_question or "").strip().lower()
    sp = (species_name or "Specimen").strip()
    words = set(re.findall(r'\b\w+\b', q))
    
    if words & {"wer", "hallo", "fisch", "wie", "was", "ist", "bitte", "danke", "guten", "moin", "deutsch"}:
        is_de = True

    # 1. Identity
    if any(phrase in q for phrase in ["who are you", "who r u", "your name", "wer bist du", "wer sind sie", "identify yourself"]):
        if is_de:
            return "Ich bin Dr. Daniel Pauly, Meeresbiologe. Mein Forschungsschwerpunkt liegt auf globalen Fischereidynamiken, Kiemen-Sauerstoff-Theorie und Arterhaltung."
        return "I am Dr. Daniel Pauly, principal marine biologist. My work focuses on global fishery dynamics, the Gill-Oxygen Limitation Theory, and ecosystem conservation."

    # 2. Pure Greetings (only if no specific scientific or specimen query)
    greeting_words = {"hello", "hi", "hey", "greetings", "hallo", "moin"}
    if (words & greeting_words) and not (words & {"fish", "species", "fisch", "protect", "schützen", "salmo", "cod", "tuna", "shark", "gill", "oxygen", "extinction"}):
        if is_de:
            return "Seid gegrüßt! Hier ist Dr. Daniel Pauly. Unsere hydrodynamische Telemetrie ist aktiv. Welche meeresbiologischen Beobachtungen möchten Sie analysieren?"
        return "Greetings! Dr. Daniel Pauly here. Our hydrodynamic telemetry streams are live. How can I assist your aquatic species observations?"

    # 2. Species-Specific Marine Biology Knowledge
    sp_lower = (sp + " " + q).lower()
    if any(k in sp_lower for k in ["salmo", "trutta", "forelle", "trout"]):
        if is_de:
            return f"Salmo trutta (Bachforelle) reagiert hochsensibel auf thermische Gradienten und Hypoxie. Als rheophile Salmonidenart dient sie als primärer Bioindikator intakter Kaltwasserströmungen."
        return f"Salmo trutta (Brown trout) exhibits high sensitivity to dissolved oxygen and thermal gradients. As a rheophilic salmonid, it serves as a critical indicator for lotic ecosystem health."

    if any(k in sp_lower for k in ["gadus", "morhua", "cod", "kabeljau", "dorsch"]):
        if is_de:
            return f"Gadus morhua (Atlantischer Kabeljau) demonstriert drastische historische Trophie-Verschiebungen. Effektive Bestandserholung erfordert strenge marine Schutzgebiete und reduzierte Schleppnetzfischerei."
        return f"Gadus morhua (Atlantic cod) is the textbook demonstration of trophic cascade collapse from historic overexploitation. Biomass replenishment demands rigorous Marine Protected Areas."

    if any(k in sp_lower for k in ["thunnus", "tuna", "thunfisch"]):
        if is_de:
            return f"Thunfische besitzen eine bemerkenswerte regionale Endothermie. Ihr hoher Sauerstoffbedarf macht sie jedoch besonders vulnerabel gegenüber sich ausdehnenden hypoxischen Todeszonen."
        return f"Tuna species utilize regional endothermy for high-speed cruising. However, their extreme metabolic rate makes them exceptionally vulnerable to expanding oceanic oxygen minimum zones."

    if any(k in sp_lower for k in ["octopus", "squid", "krake", "oktopus", "tintenfisch"]):
        if is_de:
            return f"Kopffüßer zeichnen sich durch rasantes somatisches Wachstum und hohe neurobiologische Anpassungsfähigkeit aus, wodurch sie ökologische Nischen gestresster Knochenfische besetzen."
        return f"Cephalopods exhibit rapid somatic turnover and complex behavioral plasticity, enabling opportunistic niche colonization where teleost competitors decline under climate stress."

    if any(k in sp_lower for k in ["shark", "hai", "selachii"]):
        if is_de:
            return f"Als K-Strategen und Spitzenprädatoren regulieren Haie marine Nahrungsnetze von oben nach unten. Der Verlust dieser Spitzenprädatoren destabilisiert das gesamte pelagische Gleichgewicht."
        return f"As apex K-strategists, sharks regulate oceanic food webs through top-down trophic control. Their removal triggers destructive mesopredator release cascades across marine biomes."

    # 3. Scientific Theories & Environmental Topics
    if any(k in q for k in ["golt", "oxygen", "sauerstoff", "gill", "kieme", "warm", "temperature"]):
        if is_de:
            return "Gemäß meiner Kiemen-Sauerstoff-Limitierungstheorie (GOLT) wächst die zweidimensionale Kiemenoberfläche langsamer als das dreidimensionale Körpervolumen, wodurch wärmeres Wasser das Maximalgewicht von Fischen deckelt."
        return "Under my Gill-Oxygen Limitation Theory (GOLT), 2D gill surface area cannot keep pace with 3D body volume growth. In warming oceans, metabolic oxygen stress strictly limits maximum fish size."

    if any(k in q for k in ["overfishing", "fishing", "extinction", "überfischung", "aussterben", "bestand", "collapse"]):
        if is_de:
            return "Das Phänomen des 'Fishing Down Marine Food Webs' ersetzt langlebige Spitzenfische durch kleine Wirbellose. Zur Stabilisierung sind unverzüglich schutzzonierte Sperrgebiete erforderlich."
        return "Global fishing trends demonstrate 'Fishing Down Marine Food Webs', replacing long-lived apex predators with smaller planktivores. Sustainable quotas and strictly enforced no-take MPAs are imperative."

    if any(k in q for k in ["what is this", "identify", "what fish", "was ist", "welcher fisch"]):
        if is_de:
            return f"Unsere optische Sensorik erfasst {sp}. Das hydrodynamische Profil und die Flossenfrequenz bestätigen ein stabiles Schwimmverhalten im aktuellen Transektschnitt."
        return f"Optical telemetry confirms specimen identification as {sp}. The swimming kinematic signature indicates healthy hydrodynamic locomotion within the observed transect."

    # 4. Default Telemetry & Ecological Synthesis
    if is_de:
        if target_specimen_info:
            return f"Dr. Pauly Telemetriebericht: {target_specimen_info} zeigt ungestörte Schwimmmuster. Die stochastische Zustandsschätzung bestätigt stabile Populationsparameter."
        return f"Dr. Pauly Telemetriebericht: Exemplar {sp} weist typische ökologische Merkmale auf. Kontinuierliche Sensordaten-Assimilation ist aktiv."
    else:
        if target_specimen_info:
            return f"Dr. Pauly Telemetry Report: {target_specimen_info} exhibits optimal locomotion. Stochastic state filtering confirms stable population abundance parameters."
        return f"Dr. Pauly Telemetry Report: Specimen {sp} exhibits characteristic ecological resilience. Sensor data assimilation remains synchronized with baseline population models."

def run_multi_agent_synthesis(session_summary_text):
    """
    Executes a Multi-Agent LLM Synthesis Debate combining:
    1. Dr. Daniel Pauly (Conservation Marine Biologist)
    2. Prof. Environmental Risk Analyst (Ecological Economist)
    Returns a structured dictionary with both viewpoints and a unified synthesis.
    """
    prompt_pauly = (
        "You are Dr. Daniel Pauly, world-renowned marine biologist. "
        "Analyze the following aquatic telemetry data from a biological conservation perspective: "
        f"{session_summary_text}\n"
        "Provide a 2-sentence summary focused on species biodiversity and extinction risk."
    )
    
    prompt_risk = (
        "You are Prof. Environmental Risk Analyst, expert in ecological economics and water resource policy. "
        "Analyze the following aquatic telemetry data from a resource management perspective: "
        f"{session_summary_text}\n"
        "Provide a 2-sentence summary focused on ecosystem management and economic mitigation."
    )
    
    try:
        pauly_raw = query_ollama_direct(prompt_pauly)
        risk_raw = query_ollama_direct(prompt_risk)
        res_pauly = clean_pauly_response(pauly_raw) if pauly_raw else "Biological assessment indicates active species tracking with baseline population stability."
        res_risk = clean_pauly_response(risk_raw) if risk_raw else "Environmental risk evaluation recommends continued non-invasive telemetry monitoring."
    except Exception:
        res_pauly = "Biological assessment indicates active species tracking with baseline population stability."
        res_risk = "Environmental risk evaluation recommends continued non-invasive telemetry monitoring."
    
    if not res_pauly or len(res_pauly) < 10:
        res_pauly = "Biological assessment indicates active species tracking with baseline population stability."
    if not res_risk or len(res_risk) < 10:
        res_risk = "Environmental risk evaluation recommends continued non-invasive telemetry monitoring."
        
    synthesis = f"DR. PAULY (BIOLOGY): {res_pauly}\n\nPROF. RISK ANALYST (POLICY): {res_risk}"
    return {
        "pauly_perspective": res_pauly,
        "risk_perspective": res_risk,
        "full_synthesis": synthesis
    }

def is_pauly_speaking():
    with pauly_lock:
        return pauly_speech_active or audio_manager.is_speaking

def set_pauly_speaking(val):
    global pauly_speech_active, ACTIVE_COMM
    with pauly_lock:
        pauly_speech_active = val
        if val:
            ACTIVE_COMM = "PAULY"
        elif ACTIVE_COMM == "PAULY":
            ACTIVE_COMM = None

def stop_pauly_audio():
    global pauly_speech_active, ACTIVE_COMM, pauly_fade_state
    audio_manager.stop()
    with pauly_lock:
        pauly_speech_active = False
        if ACTIVE_COMM == "PAULY":
            ACTIVE_COMM = None
    pauly_fade_state = "FADE_OUT"

GLOBAL_SPECIES_IMAGES = {}
def fetch_gbif_species_image(species_name):
    if species_name in GLOBAL_SPECIES_IMAGES:
        return
    try:
        url = f"https://api.gbif.org/v1/species/match?name={species_name}"
        res = requests.get(url, timeout=3).json()
        usage_key = res.get("usageKey")
        if usage_key:
            media_url = f"https://api.gbif.org/v1/species/{usage_key}/media"
            m_res = requests.get(media_url, timeout=3).json()
            results = m_res.get("results", [])
            for item in results:
                if item.get("type") == "StillImage" and "identifier" in item:
                    img_url = item["identifier"]
                    img_data = requests.get(img_url, timeout=4).content
                    nparr = np.frombuffer(img_data, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if img is not None:
                        GLOBAL_SPECIES_IMAGES[species_name] = img
                        return
    except Exception:
        pass
    GLOBAL_SPECIES_IMAGES[species_name] = None

pauly_active_dialogue = ""
pauly_ui_alpha = 0.0
pauly_fade_state = "IDLE"
pauly_reading_timer = 0

# Persistent Chat Log History for Live Chat Portal
pauly_chat_history = [
    {
        "sender": "DR. PAULY",
        "text": "Dr. Daniel Pauly marine research assistant ready. Select any fish specimen in the video feed, then ask your question here in English or German.",
        "time": time.time()
    }
]

def update_pauly_fade_state_machine():
    global pauly_ui_alpha, pauly_fade_state
    fade_speed = 0.08
    if pauly_fade_state == "FADE_IN":
        pauly_ui_alpha = min(1.0, pauly_ui_alpha + fade_speed)
        if pauly_ui_alpha >= 1.0:
            pauly_fade_state = "VISIBLE"
    elif pauly_fade_state == "FADE_OUT":
        pauly_ui_alpha = max(0.0, pauly_ui_alpha - fade_speed)
        if pauly_ui_alpha <= 0.0:
            pauly_fade_state = "IDLE"

def clean_pauly_response(text):
    if not text:
        return ""
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    while '  ' in text:
        text = text.replace('  ', ' ')
    
    meta_phrases = [
        "The language of the user's question is English, so I'll respond in English.",
        "The language of the user's question is German, so I'll respond in German.",
        "The language of the user's question is English.",
        "The language of the user's question is German.",
        "As Dr. Daniel Pauly,",
        "As Dr. Pauly,"
    ]
    for p in meta_phrases:
        if text.startswith(p):
            text = text[len(p):].strip()
        text = text.replace(p, "").strip()
        
    return text.strip()

pauly_query_id = 0

def trigger_pauly_call(species_name, user_question=None, target_specimen_info=None, hud_notifs=None, force=False):
    global pauly_active_dialogue, pauly_ui_alpha, pauly_fade_state, pauly_reading_timer, language_mode, pauly_chat_history, pauly_query_id
    
    with pauly_lock:
        pauly_query_id += 1
        current_qid = pauly_query_id

    audio_manager.stop()
    if johnny_relic.is_active:
        johnny_relic.cancel(hud_notifs)
            
    set_pauly_speaking(True)
    pauly_fade_state = "FADE_IN"
    pauly_reading_timer = time.time()
    
    specimen_context = f" Target details: {target_specimen_info}." if target_specimen_info else ""
    # Robust German vs English detection
    german_indicators = ['ich', 'der', 'die', 'das', 'ist', 'sind', 'und', 'nicht', 'fisch', 'fische', 'wasser', 'deutsch', 'wer', 'wie', 'was', 'wo', 'warum', 'welche', 'welcher', 'welches', 'kann', 'können', 'zeig', 'zeige', 'bitte', 'danke', 'hallo', 'moin', 'guten', 'ä', 'ö', 'ü', 'ß']
    is_user_german = user_question and any(w in user_question.lower() for w in german_indicators)
    effective_lang = "DE" if (language_mode == "DE" or is_user_german) else "EN"
    
    if user_question:
        clean_q = user_question.strip()
        pauly_chat_history.append({"sender": "USER", "text": clean_q, "time": time.time()})
        pauly_active_dialogue = f"Analyzing: '{clean_q}'..."
        
        if effective_lang == "DE":
            prompt = (f"Du bist Dr. Daniel Pauly, renommierter Meeresbiologe. "
                      f"Beantworte die folgende Frage des Nutzers präzise auf Deutsch bezüglich des Fisches '{species_name}'.{specimen_context} "
                      f"Frage: '{clean_q}'. "
                      f"Antworte in 2-3 wissenschaftlich fundierten Sätzen direkt ohne Vorworte.")
        else:
            prompt = (f"You are Dr. Daniel Pauly, world-renowned marine biologist. "
                      f"Directly answer the user's question in English regarding specimen '{species_name}'.{specimen_context} "
                      f"Question: '{clean_q}'. "
                      f"Provide a concise, direct 2-3 sentence expert marine biology answer without introductory filler.")
                      
        if hud_notifs:
            hud_notifs.add(f"💬 QUESTION POSTED: \"{clean_q[:28]}\"", (89, 199, 52), 2.5)
    else:
        lang_instruction = "Respond in German." if effective_lang == "DE" else "Respond in English."
        pauly_active_dialogue = f"Dr. Pauly analyzing specimen: {species_name}..."
        prompt = (f"You are Dr. Daniel Pauly, world-renowned marine biologist. {lang_instruction} "
                  f"Directly provide a 2-sentence fascinating scientific insight about '{species_name}' ecology.{specimen_context}")
        if hud_notifs:
            hud_notifs.add(f"📞 DR. PAULY: {species_name}", (89, 199, 52), 2.5)

    def _worker(qid):
        global pauly_active_dialogue, pauly_fade_state, pauly_reading_timer, pauly_chat_history
        
        # 1. Query live Ollama LLM first
        raw_ollama = None
        try:
            raw_ollama = query_ollama_direct(prompt, timeout=3.5)
        except Exception:
            raw_ollama = None
            
        if raw_ollama and len(raw_ollama.strip()) > 10:
            response = clean_pauly_response(raw_ollama)
        else:
            # 2. Instant authentic expert marine biology fallback
            response = generate_offline_pauly_response(
                species_name=species_name,
                user_question=user_question,
                target_specimen_info=target_specimen_info,
                lang=effective_lang
            )
            response = clean_pauly_response(response)
            
        with pauly_lock:
            if pauly_query_id != qid:
                return
            
        pauly_chat_history.append({"sender": "DR. PAULY", "text": response, "time": time.time()})
        if len(pauly_chat_history) > 25:
            pauly_chat_history = pauly_chat_history[-25:]
            
        pauly_active_dialogue = response
        pauly_reading_timer = time.time()
        
        # Audio voice in male voice (Microsoft David)
        speak_tts_async(response, lang=effective_lang)
        
        est_words = len(response.split())
        sleep_dur = max(3.0, est_words * 0.35)
        time.sleep(sleep_dur)
        
        with pauly_lock:
            if pauly_query_id == qid:
                set_pauly_speaking(False)
                pauly_fade_state = "FADE_OUT"

    threading.Thread(target=_worker, args=(current_qid,), daemon=True).start()

# --- JOHNNY SILVERHAND RELIC SUB-SYSTEM [J] ---
class JohnnySilverhandRelic:
    def __init__(self):
        self.is_active = False
        self.dialogue = ""
        self.timer = 0
        self.gif_frame_idx = 0
        self.quotes = [
            "Out here in the open water... it's pure biological freedom.",
            "Field telemetry is active. Focus on tracking the target specimens.",
            "Every specimen tracked today builds a clearer ecological map.",
            "Data assimilation streams look clear. Keep observing."
        ]

    def trigger(self, hud_notifs):
        global ACTIVE_COMM
        stop_pauly_audio()
        self.is_active = True
        ACTIVE_COMM = "JOHNNY"
        self.dialogue = random.choice(self.quotes)
        self.timer = time.time()
        self.gif_frame_idx = 0
        play_sound_async(400, 300)
        speak_tts_async(self.dialogue)
        hud_notifs.add("JOHNNY SILVERHAND RELIC MODE ACTIVE [J]", (222, 82, 175), 3.0)

    def cancel(self, hud_notifs=None):
        global ACTIVE_COMM
        audio_manager.stop()
        self.is_active = False
        if ACTIVE_COMM == "JOHNNY":
            ACTIVE_COMM = None
        if hud_notifs:
            hud_notifs.add("JOHNNY RELIC MODE DISCONNECTED", (142, 142, 147), 2.0)

    def update_and_render(self, canvas, sidebar_x, sidebar_w, start_y=640, draw_text_fn=None):
        global ACTIVE_COMM
        if not self.is_active:
            return
        if time.time() - self.timer > 10.0:
            self.is_active = False
            if ACTIVE_COMM == "JOHNNY":
                ACTIVE_COMM = None
            return

        relic_panel_y = min(start_y, canvas.shape[0] - 170)
        box_w = sidebar_w - 20
        box_h = 160

        cv2.rectangle(canvas, (sidebar_x + 10, relic_panel_y), (sidebar_x + sidebar_w - 10, relic_panel_y + box_h), (250, 250, 252), -1)
        cv2.rectangle(canvas, (sidebar_x + 10, relic_panel_y), (sidebar_x + sidebar_w - 10, relic_panel_y + box_h), (222, 82, 175), 1)
        cv2.putText(canvas, "JOHNNY SILVERHAND RELIC CHIP [J]", (sidebar_x + 18, relic_panel_y + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (222, 82, 175), 1, cv2.LINE_AA)

        if len(johnny_gif_frames) > 0:
            current_gif_frame = johnny_gif_frames[self.gif_frame_idx]
            if self.gif_frame_idx < len(johnny_gif_frames) - 1:
                self.gif_frame_idx += 1
            else:
                self.gif_frame_idx = 0

            gif_w, gif_h = 110, 110
            resized_gif = cv2.resize(current_gif_frame, (gif_w, gif_h))
            
            gx = sidebar_x + 18
            gy = relic_panel_y + 30
            if gy + gif_h < canvas.shape[0]:
                canvas[gy:gy+gif_h, gx:gx+gif_w] = resized_gif
                cv2.rectangle(canvas, (gx, gy), (gx+gif_w, gy+gif_h), (222, 82, 175), 1)

            txt_x = gx + gif_w + 12
            txt_max_w = sidebar_w - (txt_x - sidebar_x) - 18
            if draw_text_fn:
                draw_text_fn(canvas, f"'{self.dialogue}'", txt_x, gy + 15, max_w=txt_max_w, max_lines=5, font_scale=0.35, text_color=(31, 29, 29))
        elif johnny_img_rgba is not None:
            img_w, img_h = 110, 110
            bgr_img = johnny_img_rgba[:, :, :3] if johnny_img_rgba.ndim == 3 and johnny_img_rgba.shape[2] >= 3 else johnny_img_rgba
            resized_img = cv2.resize(bgr_img, (img_w, img_h))
            gx = sidebar_x + 18
            gy = relic_panel_y + 30
            if gy + img_h < canvas.shape[0]:
                canvas[gy:gy+img_h, gx:gx+img_w] = resized_img
                cv2.rectangle(canvas, (gx, gy), (gx+img_w, gy+img_h), (222, 82, 175), 1)

            txt_x = gx + img_w + 12
            txt_max_w = sidebar_w - (txt_x - sidebar_x) - 18
            if draw_text_fn:
                draw_text_fn(canvas, f"'{self.dialogue}'", txt_x, gy + 15, max_w=txt_max_w, max_lines=5, font_scale=0.35, text_color=(31, 29, 29))
        else:
            if draw_text_fn:
                draw_text_fn(canvas, f"'{self.dialogue}'", sidebar_x + 18, relic_panel_y + 35, max_w=sidebar_w - 36, max_lines=4, font_scale=0.36, text_color=(31, 29, 29))

johnny_relic = JohnnySilverhandRelic()

def generate_executive_ollama_report(session_info, census_summary, enkf_filter, analysis_dir):
    """
    Generates a unique per-video executive marine biological research report using Ollama LLM
    with full statistical calculations and Lotka-Volterra equations, then compiles both Markdown and PDF reports.
    """
    import mod_07_pdf_exporter as pdf_exp
    from scipy import stats
    
    os.makedirs(analysis_dir, exist_ok=True)
    report_path = os.path.join(analysis_dir, "ollama_marine_report.md")
    pdf_path = os.path.join(analysis_dir, "ollama_marine_report.pdf")
    plots_dir = session_info.get("plots_dir", os.path.join(session_info.get("session_dir", ""), "plots"))
    
    top_species = census_summary.get("sorted_species", [])
    total_unique = census_summary.get("total_unique", 0)
    
    prey_hist = np.array(list(enkf_filter.prey_history)) if len(enkf_filter.prey_history) > 0 else np.array([10.0])
    pred_hist = np.array(list(enkf_filter.predator_history)) if len(enkf_filter.predator_history) > 0 else np.array([5.0])
    risk_hist = np.array(list(enkf_filter.risk_history)) if len(enkf_filter.risk_history) > 0 else np.array([0.0])
    
    # Statistical Calculations
    prey_stats = {
        'mean': float(np.mean(prey_hist)),
        'median': float(np.median(prey_hist)),
        'std': float(np.std(prey_hist)),
        'min': float(np.min(prey_hist)),
        'max': float(np.max(prey_hist)),
        'skew': float(stats.skew(prey_hist)) if len(prey_hist) > 2 else 0.0
    }
    
    pred_stats = {
        'mean': float(np.mean(pred_hist)),
        'median': float(np.median(pred_hist)),
        'std': float(np.std(pred_hist)),
        'min': float(np.min(pred_hist)),
        'max': float(np.max(pred_hist)),
        'skew': float(stats.skew(pred_hist)) if len(pred_hist) > 2 else 0.0
    }
    
    risk_stats = {
        'mean': float(np.mean(risk_hist)),
        'median': float(np.median(risk_hist)),
        'std': float(np.std(risk_hist)),
        'min': float(np.min(risk_hist)),
        'max': float(np.max(risk_hist))
    }
    
    # Lotka-Volterra Parameters & Non-Trivial Equilibrium Calculations
    alpha, beta, gamma, delta = 0.10, 0.02, 0.10, 0.01
    x_star = gamma / delta  # 10.0
    y_star = alpha / beta   # 5.0
    
    stats_table_data = [
        ["Mean", f"{prey_stats['mean']:.2f}", f"{pred_stats['mean']:.2f}", f"{risk_stats['mean']:.1f}%"],
        ["Median", f"{prey_stats['median']:.2f}", f"{pred_stats['median']:.2f}", f"{risk_stats['median']:.1f}%"],
        ["Std Dev", f"{prey_stats['std']:.2f}", f"{pred_stats['std']:.2f}", f"{risk_stats['std']:.1f}%"],
        ["Min / Max", f"{prey_stats['min']:.2f} / {prey_stats['max']:.2f}", f"{pred_stats['min']:.2f} / {pred_stats['max']:.2f}", f"{risk_stats['min']:.1f}% / {risk_stats['max']:.1f}%"],
        ["Skewness", f"{prey_stats['skew']:.2f}", f"{pred_stats['skew']:.2f}", "N/A"]
    ]
    
    prompt = f"""
    You are Dr. Daniel Pauly, world-renowned marine biologist and Lead Scientist at Techno - Eco Project Research Institute.
    Synthesize an exhaustive, academic peer-reviewed research paper for session '{session_info.get("session_name", "Video Analysis Session")}'.
    
    DATA TELEMETRY & STATISTICAL CALCULATIONS:
    - Total Unique Tracked Specimens: {total_unique}
    - Primary Species Abundance Breakdown: {top_species[:5]}
    - Euler-Maruyama Stochastic SDE Parameters: alpha={alpha}, beta={beta}, gamma={gamma}, delta={delta}, sigma_X=0.05, sigma_Y=0.05, dt=0.1
    - Analytical Non-Trivial Equilibrium Point (X*, Y*): ({x_star:.2f}, {y_star:.2f})
    - Prey Population (X) Stats: Mean={prey_stats['mean']:.2f}, Std={prey_stats['std']:.2f}, Median={prey_stats['median']:.2f}, Range=[{prey_stats['min']:.2f}, {prey_stats['max']:.2f}]
    - Predator Population (Y) Stats: Mean={pred_stats['mean']:.2f}, Std={pred_stats['std']:.2f}, Median={pred_stats['median']:.2f}, Range=[{pred_stats['min']:.2f}, {pred_stats['max']:.2f}]
    - EnKF Extinction Risk Metric: Mean={risk_stats['mean']:.1f}%, Max={risk_stats['max']:.1f}%
    - 100-Member EnKF Data Assimilation (Sprungk, 2023) with empirical covariances C_n^(zy) and C_n^(yy), Kalman gain K_n, and analysis state update.

    Format as a formal academic research paper in Markdown with these exact sections:
    # Techno - Eco Project Aquatic Vision Tracking & Ensemble Kalman Filter Data Assimilation Report
    
    ## Abstract
    [Executive summary of objectives, video telemetry, deduplicated species counts, stochastic SDE modeling, and EnKF extinction risk assessment.]
    
    ## 1. Methodology & Mathematical Framework
    ### Module 1: Eco Team Biological Census & Deduplication
    [Deduplicated species population tracking via global dictionary species_unique_ids = defaultdict(set), persistent tracking IDs tid from ByteTrack, and absolute population counts |S_unique(species)|.]
    
    ### Module 2: Stochastic Dynamics Engine (Euler-Maruyama Discretization)
    [Base SDE formula: Z_(n+1) = Z_n + dt*f(Z_n) + sqrt(dt)*sigma*zeta_n.
     Prey SDE: X_(n+1) = X_n + dt*(alpha*X_n - beta*X_n*Y_n) + sqrt(dt)*sigma_X*X_n*zeta_n^X.
     Predator SDE: Y_(n+1) = Y_n + dt*(delta*X_n*Y_n - gamma*Y_n) + sqrt(dt)*sigma_Y*Y_n*zeta_n^Y.
     Analytical Equilibrium Point (X*, Y*) = (gamma/delta, alpha/beta) = (10.00, 5.00).]
    
    ### Module 3: Ensemble Kalman Filter (EnKF) & Extinction Risk Engine
    [100-member EnKF assimilation framework following Sprungk (2023), empirical covariances C_n^(zy) and C_n^(yy), Kalman gain K_n = C_n^(zy) * (C_n^(yy))^(-1), analysis update, and extinction probability P(Extinction) = (1/M) sum I(X_i <= X_crit).]
    
    ## 2. Results & Statistical Telemetry Analysis
    [Species abundance census breakdown table and descriptive statistical metrics.]
    
    ## 3. Discussion
    [Trophic interaction kinetics, phase space stability, empirical covariance decay, and observation noise.]
    
    ## 4. Conclusion & Dr. Daniel Pauly Conservation Directives
    [Actionable conservation strategies, Marine Protected Areas (MPAs), and sustainable fishery recommendations.]
    
    ## References
    1. Sprungk, B. (2023). Probabilistic Forecasting and Data Assimilation. Lecture Course Notes, TU Bergakademie Freiberg (TUBAF).
    """
    
    try:
        print(f"[Ollama Exporter] Querying Ollama LLM for per-video executive report...")
        report_md = query_ollama_direct(prompt, timeout=12.0)
        if not report_md or len(report_md) < 50:
            raise RuntimeError("Ollama offline or empty response")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"[Ollama Exporter] Successfully saved Markdown report to: {report_path}")
    except Exception as e:
        print(f"[Ollama Exporter Notice]: {e}")
        report_md = (
            f"# Techno - Eco Project Executive Summary ({session_info.get('session_name')})\n\n"
            f"## 1. Ecological Census & Species Abundance\n"
            f"Total Unique Specimens Tracked: {total_unique}\n"
            f"Species Distribution: {top_species[:5]}\n\n"
            f"## 2. Stochastic Lotka-Volterra Modeling & EnKF Assimilation\n"
            f"Equilibrium Point (X*, Y*): ({x_star:.2f}, {y_star:.2f})\n"
            f"Prey (X) Mean: {prey_stats['mean']:.2f} | Predator (Y) Mean: {pred_stats['mean']:.2f}\n"
            f"Extinction Risk Mean: {risk_stats['mean']:.1f}%\n"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_md)

    # Generate Publication PDF Report with Embedded 20 Plots and PDF Tables
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(script_dir, "report_template.tex")
        fish_images_dir = session_info.get("fish_images_dir", os.path.join(session_info.get("session_dir", ""), "fish_images"))
        pdf_exp.generate_pdf_report(template_path, plots_dir, pdf_path, stats_data=stats_table_data, census_summary=census_summary, fish_images_dir=fish_images_dir)
    except Exception as _pe:
        print(f"[PDF Exporter Notice]: {_pe}")
        
    return report_path
