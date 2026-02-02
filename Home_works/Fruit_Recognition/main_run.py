import onnxruntime as ort
from torchvision import transforms
from PIL import Image
import numpy as np


# назви класів (фруктів)
class_names = [
    'Apple Braeburn',
    'Apple Granny Smith',
    'Apricot',
    'Avocado',
    'Banana',
    'Blueberry',
    'Cactus fruit',
    'Cantaloupe',
    'Cherry',
    'Clementine',
    'Corn',
    'Cucumber Ripe',
    'Grape Blue',
    'Kiwi',
    'Lemon',
    'Limes',
    'Mango',
    'Onion White',
    'Orange',
    'Papaya',
    'Passion Fruit',
    'Peach',
    'Pear',
    'Pepper Green',
    'Pepper Red',
    'Pineapple',
    'Plum',
    'Pomegranate',
    'Potato Red',
    'Raspberry',
    'Strawberry',
    'Tomato',
    'Watermelon'
]

# відкриваємо модель
session = ort.InferenceSession(
    "models/model.onnx"
)

# трансформер
test_transformer = transforms.Compose([
    transforms.Resize([224, 224]),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# отримати зображення
img = Image.open("test_images/Avocado_0.jpg")

# застосувати трансформер
input_tensor = test_transformer(img)

# змінюємо shape (добавити 1)
input_tensor = input_tensor.unsqueeze(0)

# перевести в numpy
input_tensor = input_tensor.numpy()

# використання моделі
results = session.run(
    None,  # отримати всі результати
    input_feed={
        "input": input_tensor
    }
)

result = results[0][0]
print(result)

# отримати індекс де найбільша ймовірність
ind = result.argmax()

# отримати назву класу
label = class_names[ind]

# отримати ймовірність
# softmax
max_num = result.max()
result -= max_num
exp_result = np.exp(result)
probs = exp_result / exp_result.sum()

prob = probs[ind]

print(f"Індекс найбільшої ймовірності: {ind}")
print(f"Фрукт: {label}")
print(f"Ймовірність: {prob:.2%}")

img.show(f"{label} {prob:.2%}")
