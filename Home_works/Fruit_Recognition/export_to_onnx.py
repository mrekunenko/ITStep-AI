import torch
from torch import nn
import warnings
warnings.filterwarnings('ignore')

# 1. Створи модель
model = nn.Sequential(
    nn.Conv2d(3, 8, 3, padding='same'),
    nn.ReLU(),
    nn.MaxPool2d(2, 2),
    nn.Conv2d(8, 16, 3, padding='same'),
    nn.ReLU(),
    nn.MaxPool2d(2, 2),
    nn.Conv2d(16, 32, 3, padding='same'),
    nn.ReLU(),
    nn.MaxPool2d(2, 2),
    nn.Flatten(),
    nn.Linear(20000, 32),
    nn.ReLU(),
    nn.Linear(32, 33)
)

# 2. Завантаж навчені ваги
model.load_state_dict(torch.load('models/fruit_cnn_model.pth', map_location='cpu'))
model.eval()
print("✅ Модель завантажена!")

# 3. Створи dummy input
dummy_input = torch.randn(1, 3, 200, 200)

# 4. Експортуй в ONNX з новою версією (18 замість 11)
torch.onnx.export(
    model,
    dummy_input,
    "models/model.onnx",
    export_params=True,
    opset_version=18,  # ⬅️ Змінив на 18!
    input_names=['input'],
    output_names=['output']
)

print("✅ Модель експортована в ONNX: models/model.onnx")
