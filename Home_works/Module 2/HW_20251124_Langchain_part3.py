# Тема: Langchain. Частина 3
# Завдання 1
# Відкрийте відео з файлу data\lesson7\meter.mp4.
# Проведіть бінарізацію кадрів та збережіть в новий файл.
# Можливо очистіть від шуму або наведіть різкість через
# bilateralFilter

import cv2

cap = cv2.VideoCapture(r'data\lesson7\meter.mp4')

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

writer = cv2.VideoWriter(
    'new_meter.mp4',
    fourcc,
    fps,
    (width, height),
    isColor=False
)

while True:
    success, img = cap.read()
    if not success:
        break

    # Конвертація в grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Фільтрація (bilateral для збереження країв)
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)

    # Адаптивна бінаризація
    binary = cv2.adaptiveThreshold(
        filtered, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        21, 3
    )

    writer.write(binary)
    cv2.imshow('Result', binary)

    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

cap.release()
writer.release()
cv2.destroyAllWindows()