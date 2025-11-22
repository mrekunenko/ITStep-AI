import cv2
import numpy as np

# ==============================================================
# Завдання 1
# Відкрити Lenna, застосувати маски, пікселі поза масками = 0
# ==============================================================

# Читання зображення та масок (grayscale)
img = cv2.imread("data/lesson1/Lenna.png", cv2.IMREAD_GRAYSCALE)
mask1 = cv2.imread("data/lesson1/mask1.png", cv2.IMREAD_GRAYSCALE)
mask2 = cv2.imread("data/lesson1/mask2.png", cv2.IMREAD_GRAYSCALE)

# Перетворюємо маски у тип bool
mask1_bool = mask1 > 0
mask2_bool = mask2 > 0

# Об'єднання масок через OR → результат також переводимо в bool
mask_or = cv2.bitwise_or(mask1.astype(np.uint8),
                         mask2.astype(np.uint8)) > 0

# Сегментація за mask1
res1 = img.copy()
res1[~mask1_bool] = 0

# Сегментація за mask2
res2 = img.copy()
res2[~mask2_bool] = 0

# Сегментація за об’єднаною маскою
res_or = img.copy()
res_or[~mask_or] = 0

# Вивід результатів
cv2.imshow("Original", img)
cv2.imshow("Mask1 result", res1)
cv2.imshow("Mask2 result", res2)
cv2.imshow("Mask1 OR Mask2 result", res_or)

cv2.waitKey(0)
cv2.destroyAllWindows()


# ==============================================================
# Завдання 2
# Вивести зображення та підбирати межі (слайсинг)
# ==============================================================

img2 = cv2.imread("data/lesson1/baboo.jpg", cv2.IMREAD_GRAYSCALE)

# показуємо оригінал
cv2.imshow("Baboo original", img2)

# Підібрані межі (можеш змінювати — це дозволено в умові)
row_start, row_end = 0, 50
col_start, col_end = 50, 200

cut_img = img2[row_start:row_end, col_start:col_end]

cv2.imshow("Baboo cut", cut_img)

cv2.waitKey(0)
cv2.destroyAllWindows()
