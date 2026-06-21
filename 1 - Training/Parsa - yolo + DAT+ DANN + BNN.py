import torch
import torch.nn as nn
import torch.nn.functional as F
import types
from ultralytics import YOLO

# ==========================================
# 1. DANN: Gradient Reversal Layer (GRL)
# ==========================================
class GradientReversalLayer(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, alpha):
        ctx.alpha = alpha
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        # Reverse the gradient and scale by alpha
        output = grad_output.neg() * ctx.alpha
        return output, None

def grl_hook(x, alpha=1.0):
    return GradientReversalLayer.apply(x, alpha)

# ==========================================
# 2. BNN: Bayesian Linear Layer
# ==========================================
class BayesianLinear(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        # Reparameterization variables (mu and rho)
        self.weight_mu = nn.Parameter(torch.Tensor(out_features, in_features).normal_(0, 0.1))
        self.weight_rho = nn.Parameter(torch.Tensor(out_features, in_features).normal_(-3, 0.1))
        self.bias_mu = nn.Parameter(torch.Tensor(out_features).normal_(0, 0.1))
        self.bias_rho = nn.Parameter(torch.Tensor(out_features).normal_(-3, 0.1))

    def forward(self, x):
        # F.softplus is numerically stable compared to log1p(exp(x)), preventing NaN errors
        weight_sigma = F.softplus(self.weight_rho)
        bias_sigma = F.softplus(self.bias_rho)

        if self.training:
            epsilon_w = torch.randn_like(weight_sigma)
            epsilon_b = torch.randn_like(bias_sigma)
            weight = self.weight_mu + weight_sigma * epsilon_w
            bias = self.bias_mu + bias_sigma * epsilon_b
        else:
            weight = self.weight_mu
            bias = self.bias_mu

        out = F.linear(x, weight, bias)
        
        # KL Divergence necessary for BNN Loss (ELBO)
        kl_weight = 0.5 * torch.sum(weight_sigma**2 + self.weight_mu**2 - 1 - torch.log(weight_sigma**2 + 1e-8))
        kl_bias = 0.5 * torch.sum(bias_sigma**2 + self.bias_mu**2 - 1 - torch.log(bias_sigma**2 + 1e-8))
        kl_loss = kl_weight + kl_bias
        
        return out, kl_loss

# ==========================================
# 3. ARCHITECTURE: YOLO Backbone + BNN + DANN
# ==========================================
class YOLOv8_DANN_BNN(nn.Module):
    def __init__(self, num_classes, yolo_weights="yolov8n-cls.pt"):
        super().__init__()
        
        # Load base model
        base_yolo = YOLO(yolo_weights).model
        self.feature_extractor = base_yolo
        
        # Safely remove the default classification head's linear layer
        self.feature_extractor.model[-1].linear = nn.Identity()
        
        # FIX: Override the forward method of the final YOLO head.
        # This prevents the backbone from applying a rogue softmax during model.eval()
        def custom_classify_forward(self_module, x):
            if isinstance(x, list):
                x = torch.cat(x, 1)
            # Flatten and return raw features safely
            return self_module.linear(self_module.drop(self_module.pool(self_module.conv(x)).flatten(1)))
            
        # Bind the custom method to the specific instance layer
        self.feature_extractor.model[-1].forward = types.MethodType(custom_classify_forward, self.feature_extractor.model[-1])
        
        # Feature dimension (1280 is standard for yolov8n-cls)
        feature_dim = 1280 

        # BNN Classifier Head
        self.bnn_classifier = BayesianLinear(feature_dim, num_classes)

        # DANN Domain Classifier Head
        self.domain_classifier = nn.Sequential(
            nn.Linear(feature_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 1),
            nn.Sigmoid()
        )

    def forward(self, x, alpha=1.0):
        # Extract features from YOLO backbone
        features = self.feature_extractor(x)
        
        # Ensure features are flattened safely
        features = features.view(features.size(0), -1)

        # BNN Class prediction & KL Loss
        class_preds, kl_loss = self.bnn_classifier(features)

        # DANN Domain prediction via GRL
        reversed_features = grl_hook(features, alpha)
        domain_preds = self.domain_classifier(reversed_features)

        return class_preds, domain_preds, kl_loss

# ==========================================
# 4. DAT: Domain Adversarial Training Loop
# ==========================================
def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    num_classes = 10 
    
    model = YOLOv8_DANN_BNN(num_classes=num_classes).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    
    class_criterion = nn.CrossEntropyLoss()
    domain_criterion = nn.BCELoss()

    # MOCK DATALOADERS FOR TESTING (Prevents script from crashing)
    # The team will replace these with actual PyTorch DataLoaders
    batch_size = 16
    source_loader = [(torch.randn(batch_size, 3, 224, 224), torch.randint(0, num_classes, (batch_size,)))] * 5
    target_loader = [(torch.randn(batch_size, 3, 224, 224), None)] * 5

    epochs = 50
    
    # Pre-calculate the correct KL weighting based on the number of batches
    kl_weight = 1.0 / len(source_loader) if len(source_loader) > 0 else 1.0

    for epoch in range(epochs):
        model.train()
        
        for batch_idx, ((source_img, source_labels), (target_img, _)) in enumerate(zip(source_loader, target_loader)):
            source_img, source_labels = source_img.to(device), source_labels.to(device)
            target_img = target_img.to(device)
            
            optimizer.zero_grad()

            # --- Source Domain Forward Pass ---
            src_class_preds, src_domain_preds, src_kl = model(source_img, alpha=1.0)
            
            # Use ones_like to ensure domain labels match the batch size dynamically
            src_domain_labels = torch.ones_like(src_domain_preds, device=device)
            
            # Loss: Classification + Domain (Source label = 1) + KL
            loss_class = class_criterion(src_class_preds, source_labels)
            loss_domain_src = domain_criterion(src_domain_preds, src_domain_labels)
            
            # --- Target Domain Forward Pass ---
            _, tgt_domain_preds, tgt_kl = model(target_img, alpha=1.0)
            
            tgt_domain_labels = torch.zeros_like(tgt_domain_preds, device=device)
            loss_domain_tgt = domain_criterion(tgt_domain_preds, tgt_domain_labels)
            
            # --- Total DAT Loss ---
            total_kl = (src_kl + tgt_kl) * kl_weight
            
            total_loss = loss_class + loss_domain_src + loss_domain_tgt + total_kl
            
            # Backward & Step
            total_loss.backward()
            optimizer.step()

        print(f"Epoch [{epoch+1}/{epochs}] complete. Handing off to validation...")

if __name__ == "__main__":
    main()