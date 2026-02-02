import onnxruntime as ort
import numpy as np
from PIL import Image
from torchvision import transforms
import os

# 1. Завантаж ONNX модель
ort_session = ort.InferenceSession("models/model.onnx")
print("✅ ONNX модель завантажена!")

# 2. Список класів
classes = ['Apple Braeburn', 'Apple Granny Smith', 'Apricot', 'Avocado',
           'Banana', 'Blueberry', 'Cactus fruit', 'Cantaloupe', 'Cherry',
           'Clementine', 'Corn', 'Cucumber Ripe', 'Grape Blue', 'Kiwi',
           'Lemon', 'Limes', 'Mango', 'Onion White', 'Orange', 'Papaya',
           'Passion Fruit', 'Peach', 'Pear', 'Pepper Green', 'Pepper Red',
           'Pineapple', 'Plum', 'Pomegranate', 'Potato Red', 'Raspberry',
           'Strawberry', 'Tomato', 'Watermelon']

# 3. Трансформація
transform = transforms.Compose([
    transforms.Resize([200, 200]),
    transforms.ToTensor()
])


# 4. Функція передбачення з ONNX
def predict_onnx(image_path):
    # Завантаж і обробь зображення
    img = Image.open(image_path).convert('RGB')
    img_tensor = transform(img).unsqueeze(0)

    # Конвертуй в numpy (ONNX працює з numpy)
    img_numpy = img_tensor.numpy()

    # Запусти inference
    outputs = ort_session.run(
        None,
        {'input': img_numpy}
    )[0]

    # Softmax вручну
    exp_outputs = np.exp(outputs - np.max(outputs))
    probabilities = exp_outputs / exp_outputs.sum()

    predicted_class = np.argmax(outputs)
    confidence = probabilities[0][predicted_class] * 100

    # Визначаємо правильний клас з назви файлу
    filename = os.path.basename(image_path)
    true_label = filename.rsplit('_', 1)[0]

    # Перевіряємо чи правильно
    is_correct = "✅" if classes[predicted_class] == true_label else "❌"

    print(f"{is_correct} {filename}")
    print(f"   Очікувалось: {true_label}")
    print(f"   Передбачено (ONNX): {classes[predicted_class]} ({confidence:.2f}%)")
    print()

    return classes[predicted_class] == true_label


# 5. ТЕСТУВАННЯ
print("\n🔍 ТЕСТУВАННЯ ONNX МОДЕЛІ:\n")
print("=" * 70)

test_images = [
    'test_images/Apple Braeburn_0.jpg',
    'test_images/Apple Granny Smith_0.jpg',
    'test_images/Apricot_12.jpg',
    'test_images/Avocado_0.jpg',
    'test_images/Cactus fruit_0.jpg'
]

correct = 0
total = len(test_images)

for img_path in test_images:
    if predict_onnx(img_path):
        correct += 1

print("=" * 70)
print(f"\n📊 РЕЗУЛЬТАТ ONNX: {correct}/{total} правильних ({correct / total * 100:.1f}%)")
print("=" * 70)
