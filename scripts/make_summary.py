"""Resumen: WER vs exactitud del registro (T1 y T2), F1 macro, errores absolutos, escalera. Sin UI."""
import os
import numpy as np, pandas as pd, yaml

cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))
T = cfg["paths"]["tables"]
rng = np.random.default_rng(42)
pd.set_option("display.width", 250, "display.max_columns", 50)

def boot_ci(x, n=10000):
    x = np.asarray(x, float)
    if len(x) == 0: return (np.nan, np.nan)
    m = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return tuple(np.percentile(m, [2.5, 97.5]))

def ci_txt(x):
    lo, hi = boot_ci(x)
    return f"{np.mean(x):.3f} [{lo:.3f}, {hi:.3f}]"

def load_bench(paths, prefix):
    for p in paths:
        if os.path.exists(p):
            df = pd.read_csv(p); df = df[df["clip"].str.startswith(prefix)]
            if len(df): return df
    return None

def f1_macro(gt, pred):
    clases = sorted(set(gt)); f1s = {}
    for c in clases:
        tp = sum(g == c and p == c for g, p in zip(gt, pred))
        fp = sum(g != c and p == c for g, p in zip(gt, pred))
        fn = sum(g == c and p != c for g, p in zip(gt, pred))
        f1s[c] = 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)
    return float(np.mean(list(f1s.values()))), f1s

def ejemplos(df, titulo):
    perf = df[df["acc"] == 1]; rot = df[df["acc"] < 1]
    print(f"\n--- {titulo}: WER alto con registro perfecto / WER bajo con registro roto ---")
    if len(perf): print("WER ALTO + REGISTRO PERFECTO:\n", perf.sort_values("wer", ascending=False).head(3).to_string(index=False))
    if len(rot): print("WER BAJO + REGISTRO ROTO:\n", rot.sort_values("wer").head(3).to_string(index=False))

# ======================= TAREA 1 =======================
RUNS = ["small_cuda_fp16", "small_cpu_int8", "large_cuda_fp16", "large_cuda_int8", "large_cuda_fp16_gl"]
filas_run, filas_clip, filas_campo = [], [], []
for run in RUNS:
    b = load_bench([f"{T}/benchmark_L0_{run}.csv"], "t1")
    rg = f"{T}/t1_reglas_{run}.csv"
    if b is None or not os.path.exists(rg): print("[falta]", run); continue
    r = pd.read_csv(rg); r["correcto"] = r["correcto"].astype(bool)
    acc = r.groupby("clip")["correcto"].mean().rename("acc")
    d = b.merge(acc, on="clip"); d["run"] = run; filas_clip.append(d[["run", "clip", "wer", "cer", "acc"]])
    sin5 = d[d["clip"] != "t1_05"]
    ing = r[r["campo"] == "nivel_ingles"]
    f1, _ = f1_macro(list(ing["gt"].astype(str)), list(ing["extraido"].fillna("NONE").astype(str)))
    def mae(campo):
        x = r[r["campo"] == campo]
        e = (pd.to_numeric(x["extraido"], errors="coerce") - pd.to_numeric(x["gt"], errors="coerce")).abs()
        return e.mean(), int(e.isna().sum())
    ma, na = mae("anios_experiencia"); ms, ns = mae("pretension_salarial_monto")
    filas_run.append({"run": run, "WER medio [IC95]": ci_txt(d["wer"]), "WER sin t1_05": f"{sin5['wer'].mean():.3f}",
        "CER medio": f"{d['cer'].mean():.3f}", "exactitud registro [IC95]": ci_txt(d["acc"]),
        "F1 macro ingles": round(f1, 3), "MAE anios": ma, "anios sin valor": na, "MAE salario": ms, "salario sin valor": ns})
    for _, x in r.groupby("campo")["correcto"].mean().items(): pass
    for campo, v in r.groupby("campo")["correcto"].mean().items():
        filas_campo.append({"run": run, "campo": campo, "exactitud": v})

print("=========== TAREA 1: transcripcion vs registro (extractor por reglas) ===========")
res1 = pd.DataFrame(filas_run); print(res1.to_string(index=False)); res1.to_csv(f"{T}/resumen_t1_runs.csv", index=False)
c1 = pd.concat(filas_clip); c1.to_csv(f"{T}/resumen_t1_clips.csv", index=False)
print("\nExactitud por campo y corrida:")
pc = pd.DataFrame(filas_campo).pivot(index="campo", columns="run", values="exactitud").round(2); print(pc.to_string())
rho = c1["wer"].corr(c1["acc"], method="spearman")
print(f"\nCorrelacion de Spearman WER vs exactitud del registro ({len(c1)} pares clip-corrida, NO independientes): {rho:.2f}")
ejemplos(c1, "T1")

# ======================= TAREA 2 =======================
print("\n\n=========== TAREA 2: escalera de degradacion (large fp16 + glosario) ===========")
filas2, clips2 = [], []
for L in ["L0", "L1", "L2", "L3"]:
    b = load_bench([f"{T}/benchmark_{L}_large_cuda_fp16_gl_t2.csv", f"{T}/benchmark_{L}.csv"], "t2")
    pf = f"{T}/t2_pedido_large_cuda_fp16_gl_{L}.csv"
    if b is None or not os.path.exists(pf): print("[falta]", L); continue
    p = pd.read_csv(pf)
    okc = [c for c in p.columns if c.startswith("ok_")]
    p["acc"] = p[okc].astype(bool).mean(axis=1)
    d = b.merge(p, on="clip"); d["nivel"] = L; clips2.append(d[["nivel", "clip", "wer", "cer", "acc"]])
    al = p[p["alerta"].astype(bool)]
    diag_ok = int((al["diagnostico"] == al["causa_real"]).sum())
    filas2.append({"nivel": L, "WER medio [IC95]": ci_txt(d["wer"]), "WER sin t2_03": f"{d[d['clip'] != 't2_03']['wer'].mean():.3f}",
        "campos correctos": f"{int(p[okc].astype(bool).values.sum())}/{p[okc].size}",
        "trampas atrapadas": f"{int(p['atrapada'].sum())}/{int(p['trampa'].sum())}", "perdidas": int(p["perdida"].sum()),
        "falsas alarmas": int(p["falsa_alarma"].sum()), "diagnostico acertado (sobre alertas)": f"{diag_ok}/{len(al)}"})
res2 = pd.DataFrame(filas2); print(res2.to_string(index=False)); res2.to_csv(f"{T}/resumen_t2_escalera.csv", index=False)
c2 = pd.concat(clips2); c2.to_csv(f"{T}/resumen_t2_clips.csv", index=False)
ejemplos(c2, "T2")
print("\nNota: con 5 clips por corrida el IC bootstrap es optimista: no puede salirse del rango observado.")
