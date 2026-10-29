"""Genera la escalera de degradación (Tarea 2) a partir de data/audio/original.
L1 WhatsApp (opus 16 kbps mono) · L2 teléfono (300-3400 Hz, 8 kHz) · L3 = L1 + ruido a SNR fijo.
Requiere ffmpeg. Registra el SNR REALMENTE logrado en results/tables/ladder_manifest.json
Uso: python scripts/make_ladder.py [--tasks t1 t2]"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, soundfile as sf, yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.audio_utils import find_audio

cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))
P, L = cfg["paths"], cfg["ladder"]
ap = argparse.ArgumentParser(); ap.add_argument("--tasks", nargs="*", default=["t2"]); args = ap.parse_args()


def ff(*a):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, a)], check=True)


def pink_noise(n, rng):
    spec = rng.standard_normal(n // 2 + 1) + 1j * rng.standard_normal(n // 2 + 1)
    f = np.arange(len(spec)); f[0] = 1
    x = np.fft.irfft(spec / np.sqrt(f), n)
    return x / np.std(x)


def rms(x): return float(np.sqrt(np.mean(np.square(x))))


def add_noise(sig, snr_db, kind, rng):
    noise = pink_noise(len(sig), rng) if kind == "pink" else rng.standard_normal(len(sig))
    noise *= rms(sig) / (rms(noise) * 10 ** (snr_db / 20))
    out = sig + noise
    achieved = 20 * np.log10(rms(sig) / rms(noise))
    peak = np.max(np.abs(out)); out = out / peak * 0.95 if peak > 0.99 else out
    return out, achieved


manifest = []
for task in args.tasks:
    for clip in cfg["clips"][task]:
        src = find_audio(P["audio_original"], clip)
        if src is None:
            print(f"[falta audio] {clip}"); continue
        d = {k: Path(P["audio_ladder"]) / k for k in ("L1", "L2", "L3")}
        for p in d.values(): p.mkdir(parents=True, exist_ok=True)
        # L1
        l1 = L["l1_whatsapp"]
        with tempfile.TemporaryDirectory() as tmp:
            enc = Path(tmp) / "x.ogg"
            ff("-i", src, "-ac", l1["channels"], "-ar", l1["sample_rate"], "-c:a", l1["codec"], "-b:a", l1["bitrate"], enc)
            ff("-i", enc, "-ar", l1["sample_rate"], "-ac", 1, d["L1"] / f"{clip}.wav")
        # L2
        l2 = L["l2_phone"]
        ff("-i", src, "-ac", l2["channels"], "-af", f"highpass=f={l2['highpass_hz']},lowpass=f={l2['lowpass_hz']}",
           "-ar", l2["sample_rate"], d["L2"] / f"{clip}.wav")
        # L3 = L1 + ruido a SNR objetivo
        l3 = L["l3_noisy"]
        sig, sr = sf.read(d["L1"] / f"{clip}.wav")
        out, achieved = add_noise(sig, l3["snr_db"], l3["noise_type"], np.random.default_rng(l3["seed"]))
        sf.write(d["L3"] / f"{clip}.wav", out, sr)
        manifest.append(dict(clip=clip, snr_target_db=l3["snr_db"], snr_achieved_db=round(achieved, 2),
                             noise=l3["noise_type"], seed=l3["seed"]))
        print(f"{clip}: L1/L2/L3 ok (SNR L3 = {achieved:.1f} dB)")
Path(P["tables"]).mkdir(parents=True, exist_ok=True)
json.dump(manifest, open(Path(P["tables"]) / "ladder_manifest.json", "w"), indent=2)
