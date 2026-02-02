import torch
from torch import nn
from PIL import Image
from torchvision import transforms
import os

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

# 2. Завантаж ваги
model.load_state_dict(torch.load('models/fruit_cnn_model.pth', map_location='cpu'))
model.eval()
print("✅ Модель завантажена!")

# 3. Список класів
classes = ['Apple Braeburn', 'Apple Granny Smith', 'Apricot', 'Avocado',
           'Banana', 'Blueberry', 'Cactus fruit', 'Cantaloupe', 'Cherry',
           'Clementine', 'Corn', 'Cucumber Ripe', 'Grape Blue', 'Kiwi',
           'Lemon', 'Limes', 'Mango', 'Onion White', 'Orange', 'Papaya',
           'Passion Fruit', 'Peach', 'Pear', 'Pepper Green', 'Pepper Red',
           'Pineapple', 'Plum', 'Pomegranate', 'Potato Red', 'Raspberry',
           'Strawberry', 'Tomato', 'Watermelon']

# 4. Трансформація
transform = transforms.Compose([
    transforms.Resize([200, 200]),
    transforms.ToTensor()
])


# 5. Функція передбачення
def predict_fruit(image_path):
    img = Image.open(image_path).convert('RGB')
    img_tensor = transform(img).unsqueeze(0)

    with torch.no_grad():
        output = model(img_tensor)
        predicted_class = output.argmax(dim=1).item()
        confidence = torch.softmax(output, dim=1)[0][predicted_class] * 100

    # Визначаємо правильний клас з назви файлу
    filename = os.path.basename(image_path)
    true_label = filename.rsplit('_', 1)[0]  # Витягуємо назву до останнього "_"

    # Перевіряємо чи правильно
    is_correct = "✅" if classes[predicted_class] == true_label else "❌"

    print(f"{is_correct} {filename}")
    print(f"   Очікувалось: {true_label}")
    print(f"   Передбачено: {classes[predicted_class]} ({confidence:.2f}%)")
    print()

    return classes[predicted_class] == true_label


# 6. ТЕСТУВАННЯ ВСІХ 20 ФАЙЛІВ
print("\n🔍 ТЕСТУВАННЯ МОДЕЛІ НА 20 ЗОБРАЖЕННЯХ:\n")
print("=" * 70)

test_images = [
    'test_images/Apple Braeburn_0.jpg',
    'test_images/Apple Braeburn_1.jpg',
    'test_images/Apple Braeburn_10.jpg',
    'test_images/Apple Braeburn_100.jpg',
    'test_images/Apple Braeburn_119.jpg',
    'test_images/Apple Braeburn_122.jpg',
    'test_images/Apple Granny Smith_0.jpg',
    'test_images/Apple Granny Smith_110.jpg',
    'test_images/Apple Granny Smith_112.jpg',
    'test_images/Apple Granny Smith_114.jpg',
    'test_images/Apple Granny Smith_119.jpg',
    'test_images/Apricot_12.jpg',
    'test_images/Apricot_106.jpg',
    'test_images/Apricot_116.jpg',
    'test_images/Avocado_0.jpg',
    'test_images/Avocado_112.jpg',
    'test_images/Avocado_116.jpg',
    'test_images/Cactus fruit_0.jpg',
    'test_images/Cactus fruit_107.jpg',
    'test_images/Cactus fruit_115.jpg'
]

correct = 0
total = len(test_images)

for img_path in test_images:
    if predict_fruit(img_path):
        correct += 1

print("=" * 70)
print(f"\n📊 РЕЗУЛЬТАТ: {correct}/{total} правильних ({correct / total * 100:.1f}%)")
print("=" * 70)
