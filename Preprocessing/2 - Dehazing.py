import torch
import kornia
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm

# Define paths
BASE_DIR = Path(r"C:\Users\parsa\Desktop\Code\Yolo\YOLO_Ready_Dataset")
OUTPUT_DIR = Path(r"C:\Users\parsa\Desktop\Code\Yolo\YOLO_Ready_Dataset\YOLO_Dehazed")

def gpu_physics_dehaze(img_numpy, device):
    """
    Executes Underwater Red-Channel Compensation and CLAHE entirely on the GPU.
    Includes safety fallbacks for abnormal image dimensions and accurate Kornia color routing.
    """
    # 1. Convert to GPU Tensor (Float 0-1) -> Shape: (1, C, H, W)
    img_tensor = torch.from_numpy(img_numpy).permute(2, 0, 1).unsqueeze(0).float() / 255.0
    img_tensor = img_tensor.to(device)

    # Split BGR channels on the GPU
    b, g, r = img_tensor[:, 0, :, :], img_tensor[:, 1, :, :], img_tensor[:, 2, :, :]

    # 2. Physics Math (Red Channel Compensation) executed on CUDA cores
    mean_g = g.mean()
    mean_r = r.mean()
    
    # torch.where acts like an if-statement for every pixel simultaneously
    compensated_r = torch.where(
        mean_r < mean_g, 
        r + (mean_g - mean_r) * (1 - r) * g, 
        r
    )
    
    # Recombine channels
    compensated_tensor = torch.stack([b, g, compensated_r], dim=1)

    # 3. Apply CLAHE (Contrast Enhancement) on the GPU using Kornia
    # ACCURATE COLOR ROUTING: BGR -> RGB -> LAB
    rgb_tensor = kornia.color.bgr_to_rgb(compensated_tensor)
    lab_tensor = kornia.color.rgb_to_lab(rgb_tensor)
    
    # Apply CLAHE only to the Lightness (L) channel (index 0)
    l_channel = lab_tensor[:, 0:1, :, :] / 100.0 # Normalize L channel for Kornia
    
    # The Safety Net for weird/tiny image sizes
    try:
        clahe = kornia.enhance.equalize_clahe(l_channel, clip_limit=2.0, grid_size=(8, 8))
    except ValueError:
        clahe = kornia.enhance.equalize(l_channel)
    
    # Put enhanced L channel back 
    lab_tensor[:, 0:1, :, :] = clahe * 100.0
    
    # ACCURATE COLOR ROUTING: LAB -> RGB -> BGR
    rgb_final_tensor = kornia.color.lab_to_rgb(lab_tensor)
    final_tensor = kornia.color.rgb_to_bgr(rgb_final_tensor)

    # 4. Pull back to CPU and convert to Numpy Image format
    final_img = (final_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy() * 255)
    return np.clip(final_img, 0, 255).astype(np.uint8)

def process_dehazing():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Dehazing on: {device.type.upper()}")

    splits = ['train', 'val', 'test']
    
    for split in splits:
        img_dir = BASE_DIR / "images" / split
        out_img_dir = OUTPUT_DIR / "images" / split
        out_img_dir.mkdir(parents=True, exist_ok=True)
        
        images = list(img_dir.glob("*.jpg"))
        if not images: continue
        
        print(f"\nDehazing {split} set...")
        
        for img_path in tqdm(images):
            img = cv2.imread(str(img_path))
            if img is None: continue
                
            # Run the GPU math
            with torch.no_grad():
                dehazed_img = gpu_physics_dehaze(img, device)
            
            # Save the result
            cv2.imwrite(str(out_img_dir / img_path.name), dehazed_img)

        # Note: You would also copy the labels from YOLO_Ready_Dataset/labels to YOLO_Dehazed/labels
        # using the shutil.copytree method we used in the previous steps.

if __name__ == "__main__":
    process_dehazing()