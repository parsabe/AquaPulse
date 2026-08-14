import os
import sys
import glob
import shutil
import subprocess
import torch

# Target dataset directory containing dehazed videos in subfolders
DEHAZED_VIDEOS_DIR = r"C:\Users\parsa\Desktop\Code\Datasets\Team's dataset\Dehazed Videos"

def verify_cuda():
    """Verify that CUDA GPU is strictly available."""
    if not torch.cuda.is_available():
        raise RuntimeError("[ERROR] CUDA is strictly required for this project, but PyTorch could not detect a CUDA GPU!")
    print("=" * 75)
    print("  [CUDA ENFORCED] GPU Acceleration Active")
    print(f"  Device Name : {torch.cuda.get_device_name(0)}")
    print(f"  Device Count: {torch.cuda.device_count()}")
    print("=" * 75)

def process_video_pipeline(video_path, script_dir):
    """
    Executes model inference on a single video file using RTX Tensor Cores (fp16) 
    and feature scale=0.5 to prevent cuDNN GPU memory allocation errors. Overwrites in-place upon success.
    """
    print(f"\n" + "-" * 75)
    print(f"[PIPELINE START] Processing Video: '{os.path.basename(video_path)}'")
    print("-" * 75)

    base, ext = os.path.splitext(video_path)
    temp_output = base + "_inference_temp.mp4"

    script_path = os.path.join(script_dir, "inference_video.py")
    if not os.path.exists(script_path):
        print(f"[ERROR] Inference script not found: '{script_path}'")
        return

    print(f"[STAGE 1/1] Running RIFE Video Inference ('inference_video.py' --scale 0.5 --fp16)...")

    # Command includes --scale 0.5 and --fp16 to optimize RTX 4060 GPU VRAM & memory allocation
    cmd = [sys.executable, script_path, "--video", video_path, "--output", temp_output, "--scale", "0.5", "--fp16"]
    result = subprocess.run(cmd, cwd=script_dir)

    if result.returncode == 0 and os.path.exists(temp_output) and os.path.getsize(temp_output) > 0:
        shutil.move(temp_output, video_path)
        print(f"[SUCCESS] Successfully processed and overwrote '{os.path.basename(video_path)}'.")
    else:
        if os.path.exists(temp_output):
            os.remove(temp_output)
        print(f"[WARNING] Inference failed for '{os.path.basename(video_path)}'. Original video retained.")

def main():
    verify_cuda()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.exists(DEHAZED_VIDEOS_DIR):
        print(f"[WARNING] Dehazed videos directory does not exist: '{DEHAZED_VIDEOS_DIR}'")
        return

    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm')
    video_files = []
    
    for root, _, files in os.walk(DEHAZED_VIDEOS_DIR):
        for file in files:
            if file.lower().endswith(video_extensions) and not file.endswith("_temp.mp4"):
                video_files.append(os.path.join(root, file))

    video_files = sorted(list(set(video_files)))
    
    print(f"Found {len(video_files)} video file(s) in '{DEHAZED_VIDEOS_DIR}'.")
    
    for vid_path in video_files:
        process_video_pipeline(vid_path, script_dir)

    print("\n" + "=" * 75)
    print("  ALL STAGES COMPLETED: VIDEO INFERENCE FINISHED")
    print("=" * 75)

if __name__ == "__main__":
    main()
