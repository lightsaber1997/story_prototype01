# version_report.py
import sys, importlib

# --- core libs -----------------------------------------------------
import torch
import transformers
import accelerate

# --- Qt binding ----------------------------------------------------
import PySide6
from PySide6 import QtCore

def fmt(name, value):
    print(f"{name:<18}: {value}")

print("=== Runtime versions ===")
fmt("Python",          sys.version.split()[0])
fmt("torch",           torch.__version__)
fmt("torch cuda",      torch.version.cuda or "cpu‑only build")
fmt("transformers",    transformers.__version__)
fmt("accelerate",      accelerate.__version__)
fmt("PySide6 binding", PySide6.__version__)

# ---- Qt runtime version (robust) ----------------------------------
try:
    # Works on most non‑abi3 builds
    from PySide6.QtCore import QT_VERSION_STR
    qt_runtime = QT_VERSION_STR
except (ImportError, AttributeError):
    # Fallback that always exists
    qt_runtime = QtCore.qVersion()
fmt("Qt runtime", qt_runtime)

# Optional: show first available GPU
if torch.cuda.is_available():
    idx = torch.cuda.current_device()
    fmt("CUDA device", torch.cuda.get_device_name(idx))
