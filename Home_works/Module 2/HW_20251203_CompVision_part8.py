# Завдання 1
# Відкрийте відео data/lesson_pose/squat.mp4
# Ваша задача рахувати кількість присідань.
# Отримайте перший кадр та виділіть основні точки.
# Отримайте координати 3-ох точок ноги
# Визначте кут між цими трьома точками. Скористайтесь
# функцією utils.get_angle(x1, y1, x2, y2, x3, y3) де x2, y2 –
# координати коліна(центральна точка)
# Запустіть відео та добавте на сам кадр кут згинання ніг.
# Визначіть нижню межу кута(якщо людина опустилась
# нижче вважаємо що вона достатньо опустилась) та верхню
# межу кута(якщо людина піднялась вище вважаємо що вона
# достатньо піднялась)
# Добавте кількість присідань та
# кут на кожен кадр.

import cv2
import ultralytics
import numpy as np


def get_angle(x1, y1, x2, y2, x3, y3):
    a = np.array([x1, y1])
    b = np.array([x2, y2])
    c = np.array([x3, y3])

    ab = a - b
    cb = c - b

    dot = ab @ cb
    norm_ab = np.linalg.norm(ab)
    norm_cb = np.linalg.norm(cb)

    angle = np.arccos(dot / (norm_ab * norm_cb))
    return np.degrees(angle)


cap = cv2.VideoCapture(r'data/lesson_pose/squat.mp4')
model = ultralytics.YOLO('yolo11s-pose.pt')

move_down = True
squat_counter = 0

while True:
    success, img = cap.read()
    if not success:
        break

    img_resized = cv2.resize(img, None, fx=0.5, fy=0.5)
    results = model.predict(img_resized, verbose=False)
    result = results[0]

    img_plot = result.plot()

    # Перевірка наявності keypoints
    if result.keypoints is None or len(result.keypoints.xy) == 0:
        cv2.imshow("Squats", img_plot)
        continue

    xy = result.keypoints.xy[0]

    # Точки: 12-стегно, 14-коліно, 16-щиколотка
    hip = xy[12].cpu().numpy()
    knee = xy[14].cpu().numpy()
    ankle = xy[16].cpu().numpy()

    # Обчислення кута
    angle = get_angle(hip[0], hip[1], knee[0], knee[1], ankle[0], ankle[1])

    # Підрахунок присідань
    if angle < 90 and move_down:
        squat_counter += 1
        move_down = False

    if angle > 160 and not move_down:
        move_down = True

    # Виведення тексту
    cv2.putText(img_plot, f'Squats: {squat_counter}',
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2)

    cv2.putText(img_plot, f'Angle: {int(angle)}°',
                (20, 80), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 255, 0), 2)

    cv2.imshow("Squats", img_plot)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()