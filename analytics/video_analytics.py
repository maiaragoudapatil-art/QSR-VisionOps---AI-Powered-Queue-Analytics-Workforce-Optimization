import cv2
from ultralytics import YOLO


def process_video(video_path):

    model = YOLO(
        "your_model.pt"
    )

    cap = cv2.VideoCapture(
        video_path
    )

    max_people = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        results = model(frame)

        people = 0

        for result in results:

            for box in result.boxes:

                class_id = int(
                    box.cls[0]
                )

                if class_id == 0:
                    people += 1

        max_people = max(
            max_people,
            people
        )

    cap.release()

    return {
        "customer_count": max_people,
        "queue_length":
            round(max_people * 0.2),
        "average_wait_time":
            round(max_people * 0.5),
        "occupancy":
            min(max_people * 5, 100),
    }
