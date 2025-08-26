# img_to_text_controller.py
import sys
import os
import numpy as np
import onnxruntime as ort
from PIL import Image
import requests
import torch
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize, InterpolationMode
from PySide6.QtCore import QObject, QThread, Signal, Slot
from config.config_loader import load_config


# ----------------------------
# Worker + Controller
# ----------------------------
class ImgToTextWorker(QObject):
    """Worker that handles image → text conversion off-thread."""

    resultReady = Signal(dict)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    @Slot(str)
    def doWork(self, image_path: str):
        """Receive an image path, call engine, emit result."""
        print(f"[Worker] Got image_path={image_path}")

        try:
            matches = self.engine.image_to_text(image_path, top_k=4)  # always top 4
            self.resultReady.emit({"type": "img2text", "matches": matches})
        except Exception as e:
            self.resultReady.emit({"type": "error", "error": str(e)})


class ImgToTextController(QObject):
    """Controller: runs worker in a QThread."""

    operate = Signal(str)

    def __init__(self, engine, result_callback):
        super().__init__()
        self.workerThread = QThread()
        self.worker = ImgToTextWorker(engine)
        self.worker.moveToThread(self.workerThread)

        # Connect lifecycle
        self.workerThread.finished.connect(self.worker.deleteLater)
        self.operate.connect(self.worker.doWork)
        self.worker.resultReady.connect(result_callback)

        self.workerThread.start()
        self._closed = False

    def __del__(self):
        if self._closed:
            return
        self._closed = True

        if self.workerThread.isRunning():
            self.workerThread.quit()
            self.workerThread.wait(3000)


# ----------------------------
# Engines
# ----------------------------
class DummyImgToTextEngine:
    def image_to_text(self, image_path: str, top_k: int = 4):
        return [f"Dummy label {i}" for i in range(top_k)]


class ClipImgToTextEngine:
    """Real CLIP engine using ONNX + cached text embeddings."""

    def __init__(self, root_path):
        cfg = load_config()
        self.cfg = cfg["img_to_text"]["option"]

        # Paths from config
        self.image_encoder_path = os.path.join(root_path, self.cfg["image_encoder_path"])
        self.text_features_norm = os.path.join(root_path, self.cfg["text_features_norm"])
        self.text_features_labels = os.path.join(root_path, self.cfg["text_features_labels"])
        
        # Load ONNX session
        assert os.path.exists(self.image_encoder_path), f"❌ Model not found: {self.image_encoder_path}"
        self.image_sess = ort.InferenceSession(
            self.image_encoder_path, providers=["CPUExecutionProvider"]
        )

        # Load text features + labels
        self.text_features = np.load(self.text_features_norm)
        with open(self.text_features_labels, "r", encoding="utf-8") as f:
            self.labels = [line.strip() for line in f]

        if self.text_features.shape[0] != len(self.labels):
            print(f"⚠️ Mismatch: {self.text_features.shape[0]} features vs {len(self.labels)} labels")

        # Preprocessing pipeline
        self.preprocess = Compose([
            Resize(224, interpolation=InterpolationMode.BICUBIC),
            CenterCrop(224),
            lambda im: im.convert("RGB"),
            ToTensor(),
            Normalize((0.48145466, 0.4578275, 0.40821073),
                      (0.26862954, 0.26130258, 0.27577711)),
        ])

    def _softmax(self, x, axis=-1):
        e_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
        return e_x / e_x.sum(axis=axis, keepdims=True)

    def image_to_text(self, image_path: str, top_k: int = 4):
        # Load image (support URL or local path)
        if image_path.startswith("http://") or image_path.startswith("https://"):
            image = Image.open(requests.get(image_path, stream=True, timeout=10).raw)
        else:
            image = Image.open(image_path)

        # Preprocess
        image_tensor = self.preprocess(image).unsqueeze(0).numpy().astype(np.float32)

        # Encode image
        image_features = self.image_sess.run(["image_features"], {"image": image_tensor})[0]
        image_features /= np.linalg.norm(image_features, axis=-1, keepdims=True)

        # Similarity
        logit_scale = 100.0
        logits = logit_scale * (image_features @ self.text_features.T)
        probs = self._softmax(logits, axis=-1)

        # Top-k labels (text only, no probs)
        top_indices = probs[0].argsort()[-top_k:][::-1]
        results = [self.labels[idx] for idx in top_indices]

        return results
