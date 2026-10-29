"""Transcribe el corpus con cada corrida de config.yaml (benchmark.runs) y cachea resultados.
Uso (Colab con GPU):
    python scripts/run_asr_benchmark.py                       # todas las corridas, nivel L0
    python scripts/run_asr_benchmark.py --runs small_cuda_fp16 large_cuda_fp16
    python scripts/run_asr_benchmark.py --level L2            # escalera (T2)
Salida: results/cache/asr/<nivel>/<corrida>/<clip>.json  y  results/tables/benchmark_<nivel>.csv
"""
import argparse, gc, json, sys
from pathlib import Path
import pandas as pd, yaml, jiwer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import asr
from src.audio_utils import find_audio
from src.text_norm import normalize

ap = argparse.ArgumentParser()
ap.add_argument("--level", default="L0")
ap.add_argument("--runs", nargs="*")
ap.add_argument("--tasks", nargs="*", default=["t1", "t2"])
ap.add_argument("--force", action="store_true", help="re-transcribir aunque exista caché")
args = ap.parse_args()

cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))
P, A, N = cfg["paths"], cfg["asr"], cfg["normalization"]
audio_dir = Path(P["audio_original"] if args.level == "L0" else Path(P["audio_ladder"]) / args.level)
runs = [r for r in cfg["benchmark"]["runs"] if not args.runs or r["name"] in args.runs]
rows = []

for run in runs:
    print(f"\n=== {run['name']} | {args.level} ===")
    with asr.VramMonitor(A["vram_poll_interval_s"]) as vram:
        model = asr.load_model(run["model"], run["device"], run["compute_type"], A["fail_if_gpu_unavailable"])
        device_rt = asr.runtime_device(model)          # lo que reporta la librería, no la config
        for task in args.tasks:
            kw = asr.build_glossary_kwargs(cfg["glossary"]["terms"][task] if run["glossary"] else None,
                                           cfg["glossary"]["mechanism"])
            for clip in cfg["clips"][task]:
                out = Path(P["cache_asr"]) / args.level / run["name"] / f"{clip}.json"
                path = find_audio(audio_dir, clip)
                if path is None:
                    print(f"  [falta audio] {clip} en {audio_dir}"); continue
                if out.exists() and not args.force:
                    res = json.load(open(out, encoding="utf-8"))
                else:
                    res = asr.transcribe(model, path, A["language"], A["beam_size"], A["vad_filter"], kw)
                    res.update(clip=clip, level=args.level, run=run["name"], model=run["model"],
                               compute_type=run["compute_type"], device_requested=run["device"],
                               device_runtime=device_rt, glossary=run["glossary"])
                    out.parent.mkdir(parents=True, exist_ok=True)
                    json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                ref = open(Path(P["reference_dir"]) / f"{clip}.txt", encoding="utf-8").read()
                r, h = normalize(ref, N), normalize(res["text"], N)
                rows.append(dict(run=run["name"], level=args.level, clip=clip, model=run["model"],
                                 compute_type=run["compute_type"], device_runtime=res["device_runtime"],
                                 glossary=run["glossary"], wer=jiwer.wer(r, h), cer=jiwer.cer(r, h),
                                 sec_per_min=res["sec_per_min_audio"], audio_s=res["audio_s"]))
                print(f"  {clip}: WER={rows[-1]['wer']:.3f} CER={rows[-1]['cer']:.3f} "
                      f"{res['sec_per_min_audio']:.1f}s/min [{res['device_runtime']}]")
    for r in rows:
        if r["run"] == run["name"]:
            r["vram_peak_mb"] = round(vram.peak_mb, 1) if vram.available else None
            r["vram_delta_mb"] = round(vram.delta_mb, 1) if vram.available else None
    print(f"  VRAM pico: {vram.peak_mb:.0f} MB (delta {vram.delta_mb:.0f} MB)" if vram.available else "  (sin NVML/GPU)")
    del model; gc.collect()

Path(P["tables"]).mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(Path(P["tables"]) / f"benchmark_{args.level}.csv", index=False)
print("\nListo ->", Path(P["tables"]) / f"benchmark_{args.level}.csv")
