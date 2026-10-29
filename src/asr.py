"""Capa ASR (semilla del motor). Sin imports de UI.
- Falla si pides GPU y no hay (no cae a CPU en silencio).
- Lee el dispositivo REAL desde la librería y mide VRAM pico con NVML."""
import subprocess
import threading
import time

import numpy as np

import ctranslate2
from faster_whisper import WhisperModel


class VramMonitor:
    """Sondea la memoria de GPU usada (NVML) en un hilo y guarda el pico."""
    def __init__(self, interval_s=0.05, index=0):
        self.interval, self.index = interval_s, index
        self.peak_mb = self.base_mb = 0.0
        self._stop = threading.Event()
        self._t = None
        self.available = False

    def _used_mb(self):
        info = self._pynvml.nvmlDeviceGetMemoryInfo(self._h)
        return info.used / 1024**2

    def __enter__(self):
        try:
            import pynvml
            pynvml.nvmlInit()
            self._pynvml = pynvml
            self._h = pynvml.nvmlDeviceGetHandleByIndex(self.index)
            self.available = True
            self.base_mb = self.peak_mb = self._used_mb()
            self._t = threading.Thread(target=self._loop, daemon=True)
            self._t.start()
        except Exception:
            self.available = False
        return self

    def _loop(self):
        while not self._stop.is_set():
            self.peak_mb = max(self.peak_mb, self._used_mb())
            time.sleep(self.interval)

    def __exit__(self, *exc):
        self._stop.set()
        if self._t:
            self._t.join()
        if self.available:
            self.peak_mb = max(self.peak_mb, self._used_mb())

    @property
    def delta_mb(self):
        return max(0.0, self.peak_mb - self.base_mb)


def load_model(model_size, device, compute_type, fail_if_gpu_unavailable=True):
    if device == "cuda" and fail_if_gpu_unavailable and ctranslate2.get_cuda_device_count() == 0:
        raise RuntimeError("Pediste GPU (cuda) pero no hay ninguna disponible: no se cae a CPU en silencio.")
    return WhisperModel(model_size, device=device, compute_type=compute_type)


def runtime_device(model) -> str:
    """Dispositivo que la librería reporta en tiempo de ejecución (no el de config)."""
    return str(model.model.device)


def build_glossary_kwargs(terms, mechanism):
    if not terms:
        return {}
    if mechanism == "hotwords":
        return {"hotwords": ", ".join(terms)}
    return {"initial_prompt": "Vocabulario: " + ", ".join(terms) + "."}



def decode_audio_ffmpeg(path, sr=16000):
    """Decodifica cualquier audio (m4a, wav, ...) a float32 mono 16 kHz con ffmpeg.
    Evita depender de PyAV, cuya versión puede chocar con faster-whisper."""
    cmd = ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(path),
           "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"]
    out = subprocess.run(cmd, capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"ffmpeg no pudo decodificar {path}: {out.stderr.decode(errors='ignore')[:300]}")
    return np.frombuffer(out.stdout, dtype=np.float32)


def transcribe(model, audio_path, language="es", beam_size=5, vad_filter=False, glossary_kwargs=None):
    audio = decode_audio_ffmpeg(audio_path)       # array float32 16 kHz
    audio_s = len(audio) / 16000.0
    t0 = time.perf_counter()
    segments, info = model.transcribe(
        audio, language=language, beam_size=beam_size,
        vad_filter=vad_filter, **(glossary_kwargs or {}))
    text = " ".join(s.text.strip() for s in segments).strip()   # el generador se consume aquí
    elapsed = time.perf_counter() - t0
    return {"text": text, "elapsed_s": elapsed, "audio_s": audio_s,
            "sec_per_min_audio": elapsed / (audio_s / 60.0) if audio_s else None}


from src.audio_utils import find_audio  # noqa: E402,F401  (re-export)
