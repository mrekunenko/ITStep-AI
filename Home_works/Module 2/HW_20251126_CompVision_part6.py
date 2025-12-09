# Завдання 1
# Відкрийте відео з файлу data\lesson8\meetings.mp4
# Застосуйте детекцію та виведіть результат, підберіть
# параметри
# Можете змінити розмір кадру для кращої візуалізації
# cv2.resize()

import ultralytics
import cv2

model = ultralytics.YOLO('yolov8s.pt')
cap = cv2.VideoCapture(r'data\lesson8\meetings.mp4')

while True:
    success, img = cap.read()
    if not success:
        break

    # Зменшення розміру для швидкості
    img = cv2.resize(img, None, fx=0.5, fy=0.5)

    # Детекція
    results = model.predict(img, conf=0.3, iou=0.5)
    result = results[0]

    # Візуалізація
    res_img = result.plot()
    cv2.imshow('Detection', res_img)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


# Завдання 2
# Відкрийте відео з файлу data\lesson8\meetings.mp4
# Застосуйте детекцію та почніть показувати відео з
# моменту, коли людей стало 5

cap = cv2.VideoCapture(r'data\lesson8\meetings.mp4')

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.resize(img, None, fx=0.5, fy=0.5)

    results = model.predict(img, conf=0.3)
    result = results[0]

    # Підрахунок людей (клас 0 = person)
    cls = result.boxes.cls.tolist()
    person_count = cls.count(0.0)

    # Показ тільки коли >= 5 людей
    if person_count >= 5:
        res_img = result.plot()  # З bounding boxes!
        cv2.imshow(f'Video - {person_count} people', res_img)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
