import cv2
import numpy as np
import torch
import torch.nn.functional as F
import os
from pathlib import Path

# Disable gradient tracking to maximize inference speed and free VRAM
torch.set_grad_enabled(False)

# Enforce strict CUDA usage
device = torch.device('cuda')
print(f"Executing math operations on: {device}")

# Define paths
script_dir = Path(__file__).resolve().parent
output_folder = script_dir / 'output'
os.makedirs(output_folder, exist_ok=True)

video_path = script_dir / "VID_20260710_080712_00_009.insv" 
output_path = output_folder / "cuda_flat_2D_highres.mp4"

if not video_path.exists():
    print(f"Error: Could not find {video_path.name}")
else:
    print(f"Opening high-resolution dual-fisheye video: {video_path.name}...")
    
    cap = cv2.VideoCapture(str(video_path), cv2.CAP_FFMPEG)
    
    if not cap.isOpened():
        print("Failed to open video.")
    else:
        W_in = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        H_in = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        tot_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Left circle center and radius
        cx = W_in / 4.0
        cy = H_in / 2.0
        R = H_in / 2.0 
        
        W_out, H_out = 1920, 1080
        fov_x_deg = 120.0
        
        print("Calculating high-resolution geometric grid directly on CUDA...")
        
        # 1. Output grid coordinates generated natively on the GPU
        u = torch.arange(W_out, device=device, dtype=torch.float32)
        v = torch.arange(H_out, device=device, dtype=torch.float32)
        v_grid, u_grid = torch.meshgrid(v, u, indexing='ij')
        
        # 2. Focal length calculation
        fov_x_rad = np.radians(fov_x_deg)
        f = (W_out / 2.0) / np.tan(fov_x_rad / 2.0)
        
        # 3. 3D Rectilinear rays
        x = (u_grid - W_out / 2.0) / f
        y = (v_grid - H_out / 2.0) / f
        
        # 4. Polar coordinates
        r = torch.sqrt(x**2 + y**2)
        theta = torch.atan(r)
        
        # 5. Equidistant projection
        f_fish = 2.0 * R / np.pi
        r_fish = f_fish * theta
        
        # 6. Cartesian coordinates on raw image (using torch.where to prevent division by zero)
        r_safe = torch.where(r == 0, torch.tensor(1.0, device=device), r)
        map_x = torch.where(r == 0, torch.tensor(cx, device=device), cx + r_fish * (x / r_safe))
        map_y = torch.where(r == 0, torch.tensor(cy, device=device), cy + r_fish * (y / r_safe))
        
        # 7. Normalize coordinates to [-1, 1] range strictly required by PyTorch grid_sample
        norm_map_x = 2.0 * map_x / (W_in - 1) - 1.0
        norm_map_y = 2.0 * map_y / (H_in - 1) - 1.0
        
        # Shape: [1, H_out, W_out, 2]
        grid = torch.stack((norm_map_x, norm_map_y), dim=-1).unsqueeze(0)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (W_out, H_out))
        
        print(f"Processing {tot_frames} frames using GPU-accelerated interpolation...")
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Transfer frame array to GPU memory and format to [Batch, Channels, Height, Width]
            frame_tensor = torch.from_numpy(frame).to(device, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)
            
            # Execute hardware-accelerated bilinear interpolation
            warped_tensor = F.grid_sample(frame_tensor, grid, mode='bilinear', padding_mode='zeros', align_corners=True)
            
            # Download processed frame back to CPU memory for saving
            warped_frame = warped_tensor.squeeze(0).permute(1, 2, 0).to(torch.uint8).cpu().numpy()
            
            out.write(warped_frame)
            frame_idx += 1
            
            if frame_idx % 100 == 0:
                print(f"Processed {frame_idx} / {tot_frames} frames...")
                
        cap.release()
        out.release()
        print(f"Success! Saved CUDA accelerated flat video to: {output_path}")