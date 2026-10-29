import os
import threading
import cv2
from ultralytics import YOLO

_MODEL_PATH = os.environ.get("QSR_YOLO_MODEL_PATH", "your_model.pt")
_model = None
_model_lock = threading.Lock()
_inference_lock = threading.Lock()


def get_model():
    global _model
    with _model_lock:
        if _model is None:
            _model = YOLO(_MODEL_PATH)
        return _model


def analyze_frame(frame, model=None):
    """Shared inference and metric calculation for uploaded/live video frames."""
    detector = model or get_model()
    with _inference_lock:
        results = detector(frame)
    people = sum(1 for result in results for box in result.boxes if int(box.cls[0]) == 0)
    return {
        "customer_count": people,
        "queue_length": round(people * 0.2),
        "average_wait_time": round(people * 0.5),
        "occupancy": min(people * 5, 100),
    }


def process_video(video_path, on_frame=None):
    cap = cv2.VideoCapture(video_path)
    max_people = 0
    try:
        model = get_model()
        while True:
            success, frame = cap.read()
            if not success:
                break
            metrics = analyze_frame(frame, model=model)
            if on_frame is not None:
                on_frame(metrics, frame)
            max_people = max(max_people, metrics["customer_count"])
    finally:
        cap.release()
    return {
        "customer_count": max_people,
        "queue_length": round(max_people * 0.2),
        "average_wait_time": round(max_people * 0.5),
        "occupancy": min(max_people * 5, 100),
    }
