from ultralytics import YOLO
import cv2

model = YOLO("yolov9n.pt")

video_path = "media/videos/video1.mp4"

cap = cv2.VideoCapture(video_path)

while cap.isOpened():

    success, frame = cap.read()

    if not success:
        break

    results = model(frame)

    person_count = 0

    for result in results:

        for box in result.boxes:

            cls = int(box.cls[0])

            if cls == 0:  # person class
                person_count += 1

    print(
        f"People Detected: {person_count}"
    )

cap.release()