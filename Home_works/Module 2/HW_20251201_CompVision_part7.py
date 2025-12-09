# Завдання 1
# Відкрийте зображення data/lesson_seg/tumor1.jpg
# Проведіть сегментацію зображення використовуючи
# модель data/lesson_seg/brain-tumor-seg.jpg
# Визначте площу пухлини в пікселях.
# Визначте площу в
# (1 піксель – 0,0025
# )
# В залежності від площі присвойте пухлині певний тип
#  <10 – small
#  10-25 – middle
#  >25 – large
# Покажіть пухлину – за допомогою маски усі лишні
# пікселі зробіть 0, а як назву зображення використайте її тип

import ultralytics
import numpy as np
import cv2

model = ultralytics.YOLO(r'data\lesson_seg\brain-tumor-seg.pt')
img = cv2.imread(r'data\lesson_seg\tumor1.jpg')

# Сегментація
results = model.predict(img, verbose=False)
result = results[0]

# Маска
mask = result.masks.data[0].cpu().numpy().astype(np.uint8)
mask *= 255

# Площа пухлини
pixels_area = mask.astype(bool).sum()
cm2_area = pixels_area * 0.0025

# Класифікація
if cm2_area < 10:
    tumor_type = "small"
elif cm2_area <= 25:
    tumor_type = "middle"
else:
    tumor_type = "large"

# Застосування маски (розширення для 3 каналів)
mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
tumor_img = cv2.bitwise_and(img, mask_3ch)

# Виведення
print(f"Pixels: {pixels_area}")
print(f"Area cm²: {cm2_area:.2f}")
print(f"Type: {tumor_type}")

cv2.imshow(tumor_type, tumor_img)
cv2.waitKey(0)
cv2.destroyAllWindows()