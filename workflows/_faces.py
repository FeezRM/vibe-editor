"""One face detector for every node. OpenCV 4 ships the Haar cascade; OpenCV 5 dropped it and ships YuNet
(FaceDetectorYN) instead, whose ~230 KB model is fetched once into vendor/models/ (gitignored)."""
import subprocess
from pathlib import Path

import cv2
import numpy as np

YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet_2023mar.onnx"


class FaceFinder:
    def __init__(self, w: int, h: int):
        """w, h: the size frames are analysed at (a third of the canvas is plenty)."""
        self.w, self.h = w, h
        self.casc = self.yunet = None
        if hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "data"):
            self.casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        else:
            model = Path(__file__).resolve().parent.parent / "vendor" / "models" / "face_detection_yunet_2023mar.onnx"
            if not model.exists():
                import urllib.request
                model.parent.mkdir(parents=True, exist_ok=True)
                urllib.request.urlretrieve(YUNET_URL, model)
            self.yunet = cv2.FaceDetectorYN.create(str(model), "", (w, h), 0.7, 0.3, 5000)

    def frame(self, video: Path, t: float):
        r = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                            "-vf", f"scale={self.w}:{self.h}", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
        arr = np.frombuffer(r.stdout, np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR) if arr.size else None

    def find(self, img):
        """Largest (Haar) / most confident (YuNet) face as (x, y, w, h) in analysis pixels, or None."""
        if img is None:
            return None
        if self.casc is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = [tuple(f) for f in self.casc.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(40, 40))]
        else:
            self.yunet.setInputSize((img.shape[1], img.shape[0]))
            _, det = self.yunet.detect(img)
            # highest confidence wins, not the biggest box: a hand holding a mic scores 0.79 and is bigger than the face
            cands = sorted((d for d in (det if det is not None else []) if d[2] >= 40 and d[3] >= 40), key=lambda d: -float(d[14]))
            faces = [tuple(int(v) for v in cands[0][:4])] if cands else []
        if not faces:
            return None
        return max(faces, key=lambda f: f[2] * f[3])

    def at(self, video: Path, t: float):
        return self.find(self.frame(video, t))
