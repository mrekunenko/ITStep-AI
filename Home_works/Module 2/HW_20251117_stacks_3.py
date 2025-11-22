import cv2
import numpy as np

# Завдання 1
# Відкрийте зображення data\lesson2\darken.png.
# Переведіть його в HSV формат та обробіть канал Value:
# 1) застосуйте вирівнювання гістограми;
# 2) збільште значення яскравості на 20–50%, використовуючи float32,
#    потім застосуйте np.clip та перетворіть назад у uint8.
# Виведіть результати обох обробок на екран.

# Читаємо оригінальне зображення (BGR)
orig_img = cv2.imread('data/lesson2/darken.png', cv2.IMREAD_COLOR)

# Перевірка, що зображення зчиталось
if orig_img is None:
    raise FileNotFoundError("Не вдалося відкрити файл 'data/lesson2/darken.png'")

# ============================================================
# 1) Вирівнювання гістограм для каналу Value (V) в HSV
# ============================================================

# Переводимо в HSV
hsv_eq = cv2.cvtColor(orig_img, cv2.COLOR_BGR2HSV)

# Беремо канал V
v = hsv_eq[:, :, 2]

# Вирівнюємо гістограму яскравості
v_eq = cv2.equalizeHist(v)

# Записуємо оновлений канал V назад у зображення HSV
hsv_eq[:, :, 2] = v_eq

# Переводимо назад у BGR для відображення
bgr_eq = cv2.cvtColor(hsv_eq, cv2.COLOR_HSV2BGR)

# ============================================================
# 2) Збільшення яскравості на ~50% через множення каналу V
# ============================================================

# Ще раз переводимо оригінал у HSV (новий об’єкт)
hsv_coef = cv2.cvtColor(orig_img, cv2.COLOR_BGR2HSV)

# Беремо канал V як float32 для коректних обчислень
v_coef = hsv_coef[:, :, 2].astype(np.float32)

# Коефіцієнт збільшення яскравості (1.5 = +50%)
coef = 1.5
v_coef = v_coef * coef

# Обрізаємо значення до діапазону [0, 255]
v_coef = np.clip(v_coef, 0, 255)

# Повертаємо тип uint8
v_coef = v_coef.astype(np.uint8)

# Записуємо оновлений канал V назад у HSV-зображення
hsv_coef[:, :, 2] = v_coef

# Переводимо назад у BGR
bgr_coef = cv2.cvtColor(hsv_coef, cv2.COLOR_HSV2BGR)

# ============================================================
# Вивід результатів
# ============================================================

cv2.imshow('Original', orig_img)
cv2.imshow('HSV equalizeHist (Value)', bgr_eq)
cv2.imshow('HSV Value * 1.5 (brightened)', bgr_coef)

cv2.waitKey(0)
cv2.destroyAllWindows()
