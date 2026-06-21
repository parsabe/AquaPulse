import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os
import torch
import torch.nn.functional as F

# Check if CUDA is available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device for processing: {device}")

# Separable Gaussian Blur on GPU
def gaussian_blur_gpu(tensor, sigma):
    ksize = int(6 * sigma) | 1
    x = torch.arange(ksize, dtype=tensor.dtype, device=tensor.device)
    mean = (ksize - 1) / 2.0
    variance = sigma ** 2
    kernel_1d = torch.exp(-((x - mean) ** 2) / (2.0 * variance))
    kernel_1d = kernel_1d / kernel_1d.sum()
    
    channels = tensor.shape[1]
    kernel_h = kernel_1d.view(1, 1, ksize, 1).repeat(channels, 1, 1, 1)
    kernel_w = kernel_1d.view(1, 1, 1, ksize).repeat(channels, 1, 1, 1)
    
    pad = ksize // 2
    padded = F.pad(tensor, (pad, pad, pad, pad), mode='replicate')
    
    blurred = F.conv2d(padded, kernel_h, groups=channels)
    blurred = F.conv2d(blurred, kernel_w, groups=channels)
    return blurred

# MSRCR pre-processing on GPU
def apply_msrcr_cuda(img):
    img_tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).to(device, dtype=torch.float32)
    img_tensor = img_tensor + 1.0
    
    sigmas = [15, 80, 250]
    retinex = torch.zeros_like(img_tensor)
    
    for s in sigmas:
        blur = gaussian_blur_gpu(img_tensor, s)
        retinex += torch.log10(img_tensor) - torch.log10(blur)
    retinex /= len(sigmas)
    
    channel_sum = torch.sum(img_tensor, dim=1, keepdim=True)
    color_rest = torch.log10(125.0 * img_tensor) - torch.log10(channel_sum + 1.0)
    
    msrcr = retinex * color_rest
    
    # Normalize to 0-255
    min_val = msrcr.min()
    max_val = msrcr.max()
    if max_val > min_val:
        msrcr = (msrcr - min_val) / (max_val - min_val) * 255.0
    else:
        msrcr = torch.zeros_like(msrcr)
        
    return msrcr.squeeze(0).permute(1, 2, 0).cpu().numpy().astype(np.uint8)

# MSRCR pre-processing on CPU (Fallback)
def apply_msrcr_cpu(img):
    img_float = np.float64(img) + 1.0
    sigmas = [15, 80, 250]
    retinex = np.zeros_like(img_float)
    for s in sigmas:
        blur = cv2.GaussianBlur(img_float, (0, 0), s)
        retinex += np.log10(img_float) - np.log10(blur)
    retinex /= len(sigmas)
    color_rest = np.log10(125.0 * img_float) - np.log10(np.sum(img_float, axis=2, keepdims=True) + 1.0)
    msrcr = retinex * color_rest
    msrcr = cv2.normalize(msrcr, None, 0, 255, cv2.NORM_MINMAX)
    return msrcr.astype(np.uint8)

# Unified apply_msrcr function that redirects based on device availability
def apply_msrcr(img):
    if device == 'cuda':
        return apply_msrcr_cuda(img)
    else:
        return apply_msrcr_cpu(img)

# Define the path to your video directory
video_directory_path = Path(r"C:\Users\parsa\Desktop\Code")
output_directory_path = video_directory_path / 'output'

# Create the output directory if it doesn't exist
output_directory_path.mkdir(parents=True, exist_ok=True)

if not video_directory_path.exists():
    print(f"Error: Video directory not found at {video_directory_path}. Please ensure the path is correct.")
else:
    # Get all .mp4 video files in the directory
    video_files = [f for f in video_directory_path.iterdir() if f.is_file() and f.suffix.lower() == '.mp4']

    if not video_files:
        print(f"No .mp4 video files found in {video_directory_path}.")
    else:
        print(f"Processing {len(video_files)} video files from {video_directory_path}...")

        for video_file_path in video_files:
            print(f"\nProcessing video: {video_file_path.name}")
            cap = cv2.VideoCapture(str(video_file_path))

            if not cap.isOpened():
                print(f"Error: Could not open video file {video_file_path}")
                continue

            # Get video properties
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            # Set up video writer for saving the dehazed video
            output_video_path = output_directory_path / f"dehazed_{video_file_path.name}"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec for .mp4
            out = cv2.VideoWriter(str(output_video_path), fourcc, fps, (frame_width, frame_height))

            if not out.isOpened():
                print(f"Error: Could not open video writer for {output_video_path}")
                cap.release()
                continue

            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Apply MSRCR dehazing (uses CUDA if available)
                dehazed_frame = apply_msrcr(frame)

                # Write processed frame to output video
                out.write(dehazed_frame)

                frame_count += 1

            cap.release()
            out.release()
            print(f"Finished processing '{video_file_path.name}'. Saved {frame_count} frames to '{output_video_path}'.")

        print("\nAll videos processed. Dehazed videos saved to output directory.")
