# 0 - model_download.py
from huggingface_hub import hf_hub_download
import shutil
import ssl

# Bypass local Windows SSL Certificate Errors
ssl._create_default_https_context = ssl._create_unverified_context

print("Downloading YOLO fish model...")
try:
    model_path = hf_hub_download(
        repo_id="akridge/yolo11-fish-detector-grayscale", 
        filename="yolo11n_fish_trained.pt"
    )
    shutil.copy(model_path, "fish_model.pt")
    print("✅ Model saved as 'fish_model.pt'. Ready for main application.")
except Exception as e:
    print(f"❌ Model download failed: {e}")