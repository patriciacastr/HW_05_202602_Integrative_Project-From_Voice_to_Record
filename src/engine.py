"""Motor único: una función, audio -> registro verificado. Sin librerías de UI.
procesar_audio(ruta, esquema) sirve a los dos esquemas: 'entrevista' (T1) y 'pedido' (T2)."""
import json, sys, time, argparse
from pathlib import Path
import yaml
from src import asr, extract_rules as R
from src import extract_fix  # noqa: F401  (al importarse, parcha las reglas de años, puesto y disponibilidad)
from src import extract_order as O

ESQUEMAS = {"entrevista": "t1", "pedido": "t2"}
_MODELOS = {}

def cargar_config(path="config.yaml"):
    return yaml.safe_load(open(path, encoding="utf-8"))

def _run_cfg(cfg):
    nombre = cfg.get("engine", {}).get("run", "large_cuda_fp16_gl")
    return next(r for r in cfg["benchmark"]["runs"] if r["name"] == nombre)

def _modelo(run, cfg):
    if run["name"] not in _MODELOS:   # se carga una sola vez; si pide GPU y no hay, lanza error (no cae a CPU)
        _MODELOS[run["name"]] = asr.load_model(run["model"], run["device"], run["compute_type"],
                                               cfg["asr"]["fail_if_gpu_unavailable"])
    return _MODELOS[run["name"]]

def _transcribir(ruta, tarea, cfg, run, nivel, usar_cache):
    cache = Path(cfg["paths"]["cache_asr"]) / nivel / run["name"] / f"{Path(ruta).stem}.json"
    if usar_cache and cache.exists():
        d = json.load(open(cache, encoding="utf-8"))
        return d["text"], d.get("device_runtime"), d.get("elapsed_s"), True
    model = _modelo(run, cfg)
    terms = cfg["glossary"]["terms"][tarea] if run["glossary"] else None
    kw = asr.build_glossary_kwargs(terms, cfg["glossary"]["mechanism"])
    A = cfg["asr"]
    res = asr.transcribe(model, ruta, A["language"], A["beam_size"], A["vad_filter"], kw)
    return res["text"], asr.runtime_device(model), res["elapsed_s"], False

def _entrevista(text, cfg):
    res = R.extraer(text, cfg)
    campos = {k: v[0] for k, v in res.items()}
    verif = {k: v[2] == "verificado" for k, v in res.items()}
    return campos, verif, {"evidencias": {k: v[1] for k, v in res.items()}}

def _pedido(text, cfg):
    carta = json.load(open(cfg["paths"]["gt_t2"], encoding="utf-8"))["carta"]
    r = O.procesar(text, carta)
    campos = {k: r[k] for k in ("items", "promocion", "direccion_entrega", "metodo_pago", "total_dicho")}
    verif = {"items": bool(r["items"]),
             "promocion": r["promocion"] is not None,
             "direccion_entrega": bool(r["direccion_entrega"]) and O._normdir(r["direccion_entrega"]) in O._normdir(text),
             "metodo_pago": r["metodo_pago"] is not None,
             "total_dicho": r["total_dicho"] in r["menciones_total"]}
    val = {"total_calculado": r["total_calculado"], "menciones_total": r["menciones_total"],
           "diagnostico": r["diagnostico"], "autocorreccion_detectada": r["autocorreccion_detectada"],
           "alerta": r["total_dicho"] is not None and r["total_calculado"] != r["total_dicho"]}
    return campos, verif, {"validacion": val}

def procesar_audio(ruta, esquema, cfg=None, nivel="L0", usar_cache=False):
    """Audio -> {transcript, campos, verificados, device, elapsed_s, error, ...}. Nunca lanza: devuelve el error."""
    t0 = time.perf_counter()
    out = {"audio": str(ruta), "esquema": esquema, "transcript": None, "campos": None, "verificados": None,
           "device": None, "elapsed_s": None, "total_s": None, "desde_cache": None, "error": None}
    try:
        cfg = cfg or cargar_config()
        if esquema not in ESQUEMAS: raise ValueError(f"esquema desconocido: {esquema} (usa {list(ESQUEMAS)})")
        run = _run_cfg(cfg)
        text, dev, el, cache = _transcribir(ruta, ESQUEMAS[esquema], cfg, run, nivel, usar_cache)
        campos, verif, extra = (_entrevista if esquema == "entrevista" else _pedido)(text, cfg)
        out.update(transcript=text, campos=campos, verificados=verif, device=dev, elapsed_s=el, desde_cache=cache, **extra)
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {e}"
    out["total_s"] = round(time.perf_counter() - t0, 2)
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("audio"); ap.add_argument("esquema", choices=list(ESQUEMAS))
    ap.add_argument("--nivel", default="L0"); ap.add_argument("--cache", action="store_true")
    a = ap.parse_args()
    print(json.dumps(procesar_audio(a.audio, a.esquema, nivel=a.nivel, usar_cache=a.cache), ensure_ascii=False, indent=2, default=str))
