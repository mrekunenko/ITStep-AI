# Модуль 12. Структури даних
# Тема: Стеки. Частина 2
# Завдання 1
# Відкрийте зображення data/lesson3/sonet.png. Проведіть
# бінарізацію.
# Обов’язково використайте:
#  розмиття або наведення різкості
#  адаптивну бінарізацію
#  очищеня шумів

import cv2
import numpy as np

# Завантаження зображення
img = cv2.imread(r'data/lesson3/sonet.png', cv2.IMREAD_GRAYSCALE)
cv2.imshow("Original", img)

# 1. Розмиття (Gaussian Blur)
blurred = cv2.GaussianBlur(img, (5, 5), 0)
cv2.imshow("Gaussian Blur", blurred)

# 2. Адаптивна бінаризація
binary = cv2.adaptiveThreshold(
    blurred,
    255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY,
    11,  # розмір ядра (непарне число)
    2    # константа віднімання
)
cv2.imshow("Adaptive Threshold", binary)

# 3. Очищення шумів (морфологічні операції)
kernel = np.ones((2, 2), np.uint8)
cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
cv2.imshow("Cleaned (No Noise)", cleaned)

cv2.waitKey(0)
cv2.destroyAllWindows()
