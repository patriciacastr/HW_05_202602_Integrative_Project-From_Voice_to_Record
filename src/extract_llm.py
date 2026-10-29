"""Extracción con modelo de lenguaje + verificación literal (Fase 3, camino 2). Sin UI."""
import json, csv, sys, re, yaml
from src import extract_rules as R

DEFAULT_LLM = "Qwen/Qwen2.5-3B-Instruct"   # se usa solo si config.yaml tiene llm_model vacío

def cargar_modelo(nombre):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tok = AutoTokenizer.from_pretrained(nombre)
    mod = AutoModelForCausalLM.from_pretrained(nombre, torch_dtype=torch.float16, device_map="cuda")
    return tok, mod

def generar(tok, mod, prompt):
    msgs = [{"role": "user", "content": prompt}]
    enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    ids = enc["input_ids"].to(mod.device)
    out = mod.generate(ids, attention_mask=enc["attention_mask"].to(mod.device), max_new_tokens=450, do_sample=False)
    return tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)

def parsear_json(s):
    m = re.search(r"\{.*\}", s, re.S)
    try:
        return json.loads(m.group()) if m else {}
    except Exception:
        return {}

def en_texto(frag, text):
    return bool(frag) and R.norm(str(frag)).strip() in R.norm(text)

def extraer_llm(text, cfg, tok, mod, prompts):
    p = prompts["t1_extraccion"].replace("__FECHA__", cfg["extraction"]["fecha_referencia_t1"]).replace("__TEXTO__", text)
    j = parsear_json(generar(tok, mod, p))
    def num(x):
        try: return float(x) if x is not None else None
        except Exception: return None
    anios, monto = num(j.get("anios_experiencia")), num(j.get("pretension_salarial_monto"))
    if anios is not None and anios == int(anios): anios = int(anios)
    if monto is not None and monto == int(monto): monto = int(monto)
    techs = [t for t in (j.get("tecnologias") or []) if isinstance(t, str)]
    ok_monto = monto is not None and R.numero_en_transcripcion(monto, text)
    disp, ing = j.get("disponibilidad"), j.get("nivel_ingles")
    r = {
      "anios_experiencia": (anios, "", anios is not None and R.numero_en_transcripcion(anios, text)),
      "ultimo_puesto": (j.get("ultimo_puesto"), "", en_texto(j.get("ultimo_puesto"), text)),
      "tecnologias": (techs, "", bool(techs) and all(en_texto(t, text) for t in techs)),
      "pretension_salarial_monto": (monto, "", ok_monto),
      "pretension_salarial_moneda": (j.get("pretension_salarial_moneda"), "", ok_monto and j.get("pretension_salarial_moneda") in ("PEN", "USD")),
      "disponibilidad": (disp, j.get("disponibilidad_evidencia"), disp is not None and en_texto(j.get("disponibilidad_evidencia"), text)),
      "nivel_ingles": (ing, j.get("nivel_ingles_evidencia"), ing is not None and en_texto(j.get("nivel_ingles_evidencia"), text)),
    }
    return {k: (v, ev, "verificado" if ok else "sin_verificar") for k, (v, ev, ok) in r.items()}

def evaluar(run="large_cuda_fp16_gl"):
    cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))
    prompts = yaml.safe_load(open(cfg["extraction"]["prompts_file"], encoding="utf-8"))
    tok, mod = cargar_modelo(cfg["extraction"].get("llm_model") or DEFAULT_LLM)
    gt = {r["clip_id"]: r for r in csv.DictReader(open(cfg["paths"]["gt_t1"], encoding="utf-8"))}
    filas = []
    for clip in cfg["clips"]["t1"]:
        text = json.load(open(f"{cfg['paths']['cache_asr']}/L0/{run}/{clip}.json", encoding="utf-8"))["text"]
        res = extraer_llm(text, cfg, tok, mod, prompts); g = gt[clip]
        correcto = {
          "anios_experiencia": res["anios_experiencia"][0] is not None and abs(res["anios_experiencia"][0] - float(g["anios_experiencia"])) < 1e-6,
          "ultimo_puesto": R.norm(res["ultimo_puesto"][0] or "").strip() == R.norm(g["ultimo_puesto"]),
          "tecnologias": {R.norm(t) for t in res["tecnologias"][0]} == {R.norm(t) for t in g["tecnologias"].split("|")},
          "pretension_salarial_monto": res["pretension_salarial_monto"][0] == float(g["pretension_salarial_monto"]),
          "pretension_salarial_moneda": res["pretension_salarial_moneda"][0] == g["pretension_salarial_moneda"],
          "disponibilidad": res["disponibilidad"][0] == g["disponibilidad"],
          "nivel_ingles": res["nivel_ingles"][0] == g["nivel_ingles"],
        }
        print(f"\n== {clip} ==")
        for campo, ok in correcto.items():
            val, ev, ver = res[campo]
            print(f"  {'OK   ' if ok else 'FALLA'} {campo:28s} extraído={val!r:40} gt={g[campo]!r:32} [{ver}]")
            filas.append({"clip": clip, "campo": campo, "extraido": val, "gt": g[campo], "correcto": ok, "verificacion": ver})
    n = sum(f["correcto"] for f in filas)
    print(f"\nExactitud global (LLM, {run}): {n}/{len(filas)} = {n/len(filas):.2f}")
    with open(f"{cfg['paths']['tables']}/t1_llm_{run}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=filas[0].keys()); w.writeheader(); w.writerows(filas)

if __name__ == "__main__":
    evaluar(sys.argv[1] if len(sys.argv) > 1 else "large_cuda_fp16_gl")
