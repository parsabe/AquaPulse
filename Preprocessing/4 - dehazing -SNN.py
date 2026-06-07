import os
import cv2
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
from tqdm import tqdm

# ---------------------------------------------------------
# 1. Surrogate Gradient Function
# ---------------------------------------------------------
class SurrogateSpike(torch.autograd.Function):
    @staticmethod
    def forward(ctx, membrane_potential, threshold):
        ctx.save_for_backward(membrane_potential, threshold)
        return (membrane_potential >= threshold).float()

    @staticmethod
    def backward(ctx, grad_output):
        membrane_potential, threshold = ctx.saved_tensors
        alpha = 2.0
        grad_input = grad_output / (1.0 + (alpha * (membrane_potential - threshold)) ** 2)
        grad_threshold = -grad_input.sum(dim=(0, 2, 3), keepdim=True) 
        return grad_input, grad_threshold

spike_function = SurrogateSpike.apply

# ---------------------------------------------------------
# 2. Learnable Threshold LIF Neuron (LT-LIF)
# ---------------------------------------------------------
class LTLIFNode(nn.Module):
    def __init__(self, channels, decay=0.5):
        super(LTLIFNode, self).__init__()
        self.decay = decay
        self.threshold = nn.Parameter(torch.ones(1, channels, 1, 1) * 0.5)

    def forward(self, x, membrane_potential):
        membrane_potential = membrane_potential * self.decay + x
        spike = spike_function(membrane_potential, self.threshold)
        membrane_potential = membrane_potential - spike * self.threshold
        return spike, membrane_potential

# ---------------------------------------------------------
# 3. Spiking Self-Attention & Transformer Block
# ---------------------------------------------------------
class SpikingSelfAttention(nn.Module):
    def __init__(self, dim):
        super(SpikingSelfAttention, self).__init__()
        self.scale = dim ** -0.5
        self.qkv = nn.Conv2d(dim, dim * 3, kernel_size=1)
        self.proj = nn.Conv2d(dim, dim, kernel_size=1)
        self.lif_qkv = LTLIFNode(dim * 3)
        self.lif_proj = LTLIFNode(dim)

    def forward(self, x, mem_qkv, mem_proj):
        B, C, H, W = x.shape
        N = H * W
        
        qkv_out = self.qkv(x)
        spike_qkv, mem_qkv = self.lif_qkv(qkv_out, mem_qkv)
        
        q, k, v = spike_qkv.chunk(3, dim=1)
        q = q.view(B, C, N).transpose(1, 2)
        k = k.view(B, C, N)
        v = v.view(B, C, N).transpose(1, 2)

        attn = (q @ k) * self.scale
        attn = attn.softmax(dim=-1)
        
        out = (attn @ v).transpose(1, 2).view(B, C, H, W)
        proj_out = self.proj(out)
        spike_out, mem_proj = self.lif_proj(proj_out, mem_proj)
        
        return spike_out, mem_qkv, mem_proj

class snnTransBlock(nn.Module):
    def __init__(self, dim):
        super(snnTransBlock, self).__init__()
        self.ssa = SpikingSelfAttention(dim)
        self.conv1 = nn.Conv2d(dim, dim * 2, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(dim * 2, dim, kernel_size=3, padding=1)
        self.lif1 = LTLIFNode(dim * 2)
        self.lif2 = LTLIFNode(dim)

    def forward(self, x, mems):
        mem_qkv, mem_proj, mem1, mem2 = mems
        
        spike_attn, mem_qkv, mem_proj = self.ssa(x, mem_qkv, mem_proj)
        x = x + spike_attn
        
        x_conv1 = self.conv1(x)
        spike1, mem1 = self.lif1(x_conv1, mem1)
        x_conv2 = self.conv2(spike1)
        spike2, mem2 = self.lif2(x_conv2, mem2)
        
        out = x + spike2
        return out, (mem_qkv, mem_proj, mem1, mem2)

# ---------------------------------------------------------
# 4. The Complete snnTrans-DHZ Architecture
# ---------------------------------------------------------
class snnTrans_DHZ(nn.Module):
    def __init__(self, time_steps=4, dim=32):
        super(snnTrans_DHZ, self).__init__()
        self.T = time_steps
        self.dim = dim
        
        self.stem = nn.Conv2d(3, dim, kernel_size=3, padding=1)
        self.stem_lif = LTLIFNode(dim)
        self.block1 = snnTransBlock(dim)
        self.head = nn.Conv2d(dim, 3, kernel_size=3, padding=1)

    def forward(self, x):
        B, C, H, W = x.shape
        mem_stem = torch.zeros(B, self.dim, H, W, device=x.device)
        mems_block = (
            torch.zeros(B, self.dim * 3, H, W, device=x.device),
            torch.zeros(B, self.dim, H, W, device=x.device),
            torch.zeros(B, self.dim * 2, H, W, device=x.device),
            torch.zeros(B, self.dim, H, W, device=x.device)
        )
        
        out_spikes = 0
        
        for t in range(self.T):
            stem_out = self.stem(x)
            spike_stem, mem_stem = self.stem_lif(stem_out, mem_stem)
            spike_block, mems_block = self.block1(spike_stem, mems_block)
            out_spikes += self.head(spike_block)
            
        return out_spikes / self.T

# ---------------------------------------------------------
# 5. Execution Pipeline (Phase 0)
# ---------------------------------------------------------
BASE_DIR = Path(r"C:\Users\parsa\Desktop\Code\Yolo\YOLO_Ready_Dataset")
OUTPUT_DIR = Path(r"C:\Users\parsa\Desktop\Code\Yolo\YOLO_Ready_Dataset\YOLO_Dehazed")

def process_dehazing():
    print("[PHASE 0] Initializing snnTrans-DHZ Architecture...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    model = snnTrans_DHZ(time_steps=4, dim=32).to(device)
    
    # REQUIRED: Load pre-trained weights for the network to successfully dehaze
    # weights_path = BASE_DIR / "snnTrans_weights.pth"
    # if weights_path.exists():
    #     model.load_state_dict(torch.load(weights_path))
    # else:
    #     print("WARNING: Running without trained weights. Output will be noisy.")
        
    model.eval()

    splits = ['train', 'val', 'test']
    
    for split in splits:
        img_dir = BASE_DIR / "images" / split
        out_img_dir = OUTPUT_DIR / "images" / split
        out_img_dir.mkdir(parents=True, exist_ok=True)
        
        images = list(img_dir.glob("*.jpg"))
        if not images: continue
        
        print(f"Applying Spiking Inference to {split.upper()} images...")
        
        for img_path in tqdm(images):
            img = cv2.imread(str(img_path))
            if img is None: continue
            
            img_tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).float() / 255.0
            img_tensor = img_tensor.to(device)
            
            with torch.no_grad():
                dehazed_tensor = model(img_tensor)
                
            final_img = (dehazed_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy() * 255)
            final_img = np.clip(final_img, 0, 255).astype(np.uint8)
            
            cv2.imwrite(str(out_img_dir / img_path.name), final_img)

if __name__ == "__main__":
    process_dehazing()
    print("[PHASE 0] Complete. Images ready for YOLO Pipeline.")
