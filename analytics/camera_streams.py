import logging
import threading
import time
import cv2
from django.db import close_old_connections
from django.utils import timezone
from analytics.alert_evidence import record_threshold_alerts
from analytics.models import LiveAnalytics
from analytics.video_analytics import analyze_frame, get_model
from branches.models import Camera
logger = logging.getLogger(__name__)

class CameraStreamWorker:
    def __init__(self, camera_id):
        self.camera_id = camera_id
        self.stop_event = threading.Event()
        self.capture_lock = threading.Lock()
        self.capture = None
        self.error = None
        self.thread = threading.Thread(target=self._run, name=f"camera-stream-{camera_id}", daemon=True)

    def start(self):
        self.thread.start()

    def stop(self, timeout=4):
        self.stop_event.set()
        with self.capture_lock:
            capture = self.capture
        if capture is not None:
            try:
                capture.release()
            except Exception:
                logger.exception("Error releasing camera %s", self.camera_id)
        self.thread.join(timeout=timeout)
        return not self.thread.is_alive()

    def _set_camera(self, **values):
        close_old_connections()
        Camera.objects.filter(pk=self.camera_id).update(**values)

    def _run(self):
        close_old_connections()
        capture = None
        failure = None
        try:
            camera = Camera.objects.select_related("branch").get(pk=self.camera_id)
            try:
                capture = cv2.VideoCapture(camera.rtsp_url, cv2.CAP_FFMPEG, [
                    cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000,
                    cv2.CAP_PROP_READ_TIMEOUT_MSEC, 2000,
                ])
            except (TypeError, cv2.error):
                capture = cv2.VideoCapture(camera.rtsp_url)
            with self.capture_lock:
                self.capture = capture
            if not capture.isOpened():
                raise RuntimeError("Unable to open RTSP stream")
            model = get_model()
            self._set_camera(stream_status="running")
            read_failures = 0
            last_persist_at = 0.0
            while not self.stop_event.is_set():
                ok, frame = capture.read()
                if not ok:
                    read_failures += 1
                    if read_failures >= 5:
                        raise RuntimeError("RTSP stream stopped returning frames")
                    self.stop_event.wait(0.2)
                    continue
                read_failures = 0
                metrics = analyze_frame(frame, model=model)
                now = timezone.now()
                self._set_camera(stream_status="running", occupancy=metrics["occupancy"],
                    queue_length=metrics["queue_length"], estimated_wait_time=metrics["average_wait_time"], last_seen=now)
                if time.monotonic() - last_persist_at >= 5:
                    LiveAnalytics.objects.create(branch=camera.branch, camera=camera,
                        customer_count=metrics["customer_count"], queue_length=metrics["queue_length"],
                        average_wait_time=metrics["average_wait_time"], occupancy=metrics["occupancy"])
                    last_persist_at = time.monotonic()
                self._update_alerts(camera, metrics, frame)
        except Exception as exc:
            failure = exc
            self.error = str(exc)
            logger.exception("Camera stream %s failed", self.camera_id)
            self._set_camera(stream_status="error")
        finally:
            if capture is not None:
                try:
                    capture.release()
                except Exception:
                    logger.exception("Error releasing camera %s", self.camera_id)
            with self.capture_lock:
                self.capture = None
            if failure is None:
                self._set_camera(stream_status="stopped")
            close_old_connections()

    @staticmethod
    def _update_alerts(camera, metrics, frame):
        record_threshold_alerts(camera, metrics, frame)

class CameraStreamManager:
    def __init__(self):
        self._workers = {}
        self._lock = threading.RLock()

    def start(self, camera_id):
        with self._lock:
            worker = self._workers.get(camera_id)
            if worker and worker.thread.is_alive():
                raise ValueError("Camera stream is already running")
            worker = CameraStreamWorker(camera_id)
            self._workers[camera_id] = worker
            Camera.objects.filter(pk=camera_id).update(stream_status="running")
            worker.start()
            return worker

    def stop(self, camera_id):
        with self._lock:
            worker = self._workers.get(camera_id)
        if worker is None or not worker.thread.is_alive():
            Camera.objects.filter(pk=camera_id).exclude(stream_status="error").update(stream_status="stopped")
            return True
        stopped = worker.stop()
        if stopped:
            with self._lock:
                if self._workers.get(camera_id) is worker:
                    self._workers.pop(camera_id, None)
        else:
            Camera.objects.filter(pk=camera_id).update(stream_status="stopping")
        return stopped


camera_streams = CameraStreamManager()
