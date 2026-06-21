"""

Please do not consider this code, this was jsut to test the .pt file - ignore it.

"""


import os
import torch
import torchvision.transforms as transforms
from PIL import Image

def run_pure_torch_inference(model_filename, image_filename):
    # 1. Dynamically locate the script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, model_filename)
    image_path = os.path.join(current_dir, image_filename)

    # 2. Force CUDA device execution
    if not torch.cuda.is_available():
        print("[!] CUDA is not available on this machine. Exiting script.")
        return
        
    device = torch.device('cuda')
    print(f"Device successfully locked to: {device.type.upper()} ({torch.cuda.get_device_name(0)})")

    # 3. Load the YOLO checkpoint and extract the model
    print(f"Loading checkpoint from: {model_path}")
    try:
        # Load the checkpoint dictionary safely
        checkpoint = torch.load(model_path, map_location=device, weights_only=False)
        
        # EXTRACT THE MODEL: This fixes the dictionary/state_dict error
        if isinstance(checkpoint, dict) and 'model' in checkpoint:
            print("Extracting model architecture from YOLO checkpoint...")
            model = checkpoint['model']
        else:
            model = checkpoint
            
    except FileNotFoundError:
        print(f"[!] Error: Could not find '{model_filename}' in {current_dir}")
        return
    except Exception as e:
        print(f"\n[!] Critical loading error: {e}")
        return

    # Set model to evaluation mode and move to GPU
    model.to(device)
    model.float()  # Ensure model weights are Float (FP32) to match standard FloatTensor inputs
    model.eval()

    # 4. Preprocess the Image (YOLO standard 224x224 for classification)
    print(f"Processing image from: {image_path}")
    try:
        img = Image.open(image_path).convert('RGB')
    except FileNotFoundError:
        print(f"[!] Error: Could not find '{image_filename}' in {current_dir}")
        return

    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    
    # Transform and add batch dimension: [3, 224, 224] -> [1, 3, 224, 224]
    input_tensor = preprocess(img).unsqueeze(0).to(device)

    # 5. Forward Pass
    print("Executing forward pass on GPU...")
    with torch.no_grad():
        output = model(input_tensor)

    # 6. Parse the Output
    print("\n--- INFERENCE RESULTS ---")
    print(f"Raw Output Type: {type(output)}")
    
    if isinstance(output, (list, tuple)):
        # For YOLOv8 classification checkpoints:
        # output[0] = class probabilities (after softmax)
        # output[1] = raw logits
        print("Detected YOLO output tuple (index 0: probabilities, index 1: logits).")
        probabilities_tensor = output[0]
    elif isinstance(output, torch.Tensor):
        # Standard PyTorch model output (logits)
        print("Detected single tensor output. Applying softmax...")
        probabilities_tensor = torch.nn.functional.softmax(output, dim=-1)
    else:
        print("Model output structure is not a standard tensor or tuple/list. Raw output:")
        print(output)
        return

    # Extract class predictions from the batch (assuming batch size 1)
    if len(probabilities_tensor.shape) >= 2:
        probabilities = probabilities_tensor[0]
        top_prob, top_class_idx = torch.topk(probabilities, 1)
        
        print(f"Predicted Class Index: {top_class_idx.item()}")
        print(f"Confidence Score: {top_prob.item():.4f}")
    else:
        print(f"Unexpected tensor shape: {list(probabilities_tensor.shape)}")
        print(probabilities_tensor)

if __name__ == "__main__":
    MODEL_NAME = "yolov8n-cls.pt"
    IMAGE_NAME = "img.png"
    
    run_pure_torch_inference(MODEL_NAME, IMAGE_NAME)