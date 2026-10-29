"""Genera ground truth (CSV) y guiones de lectura (markdown) desde guiones_data.py.

Uso:  python scripts/build_ground_truth.py
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import guiones_data as G  # noqa: E402
import medir_duracion as MD  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GT_DIR = ROOT / "data" / "ground_truth"
GT_DIR.mkdir(parents=True, exist_ok=True)

WPM = 140


def referencia(lineas) -> str:
    return " ".join(t for _, t in lineas)


def n_palabras(txt: str) -> int:
    return len(txt.split())


def md_guion(clip, titulo_extra: str) -> str:
    ref = referencia(clip["lineas"])
    out = [f"## {clip['id']}  ({titulo_extra})", ""]
    out.append(f"- Palabras: {n_palabras(ref)} · duración estimada: ~{MD.dur_est(clip['lineas']):.1f} min")
    if "orden_campos" in clip:
        out.append(f"- Orden de campos: {clip['orden_campos']}")
    out.append(f"- Trampas: {clip['trampas']}")
    out.append("")
    for spk, txt in clip["lineas"]:
        out.append(f"**{spk}:** {txt}")
        out.append("")
    return "\n".join(out)


def build_t1():
    rows = []
    for c in G.T1:
        gt, ref = c["gt"], referencia(c["lineas"])
        rows.append({
            "clip_id": c["id"],
            "anios_experiencia": gt["anios_experiencia"],
            "ultimo_puesto": gt["ultimo_puesto"],
            "tecnologias": "|".join(gt["tecnologias"]),
            "pretension_salarial": gt["pretension_salarial"],
            "moneda": gt["moneda"],
            "disponibilidad": gt["disponibilidad"],
            "disponibilidad_dicha": gt["disponibilidad_dicha"],
            "nivel_ingles": gt["nivel_ingles"],
            "orden_campos": c["orden_campos"],
            "trampas": c["trampas"],
            "n_palabras": n_palabras(ref),
            "transcripcion_referencia": ref,
        })
    with open(GT_DIR / "t1_entrevistas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    md = [
        "# Guiones — Tarea 1: Entrevistas (SET B)",
        "",
        "A = entrevistadora · B = candidata. Todo lo dicho es INVENTADO.",
        f"Fecha ficticia de las entrevistas: **{G.FECHA_REFERENCIA}** (resuelve 'a fin de mes', 'en dos semanas'…).",
        "Lean con naturalidad, a ritmo normal. Si improvisan, corrijan el texto en `scripts/guiones_data.py` y regeneren.",
        "",
        "## Cómo varía el corpus (reportar en el README)",
        "",
        "| Clip | Orden en que aparecen los campos |",
        "|---|---|",
    ]
    for c in G.T1:
        md.append(f"| {c['id']} | {c['orden_campos']} |")
    md += ["", "---", ""]
    for c in G.T1:
        md.append(md_guion(c, "entrevista"))
        md.append("---\n")
    (ROOT / "scripts" / "guiones_t1.md").write_text("\n".join(md), encoding="utf-8")
    return rows


def build_t2():
    rows = []
    for c in G.T2:
        gt, ref = c["gt"], referencia(c["lineas"])
        rows.append({
            "clip_id": c["id"],
            "items": json.dumps(gt["items"], ensure_ascii=False),
            "promocion": G.PROMOS[gt["promocion"]] if gt["promocion"] else "",
            "direccion_entrega": gt["direccion_entrega"],
            "metodo_pago": gt["metodo_pago"],
            "total_dicho": gt["total_dicho"],
            "total_calculado": gt["total_calculado"],
            "trampa_autocorreccion": int(c["autocorreccion"]),
            "trampa_total_incorrecto": int(c["total_incorrecto"]),
            "trampa_direccion_digitos": int(c["direccion_digitos"]),
            "nota": c["nota"],
            "n_palabras": n_palabras(ref),
            "transcripcion_referencia": ref,
        })
    with open(GT_DIR / "t2_llamadas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    carta_md = ["| Producto | Tamaño | Precio (S/) |", "|---|---|---|"]
    for prod, tam in G.CARTA.items():
        for t, p in tam.items():
            carta_md.append(f"| {prod} | {t} | {p} |")
    md = [
        f"# Guiones — Tarea 2: Llamadas de venta (restaurante) — SET B",
        "",
        f"Dominio: **Restaurante** — {G.NEGOCIO}. A = vendedora · B = clienta. Todo lo dicho es INVENTADO.",
        "",
        "## Carta y promociones (para el validador aritmético)",
        "",
        *carta_md,
        "",
    ]
    for k, v in G.PROMOS.items():
        md.append(f"- **{k}:** {v} ({G.PROMOS_REGLA[k]}).")
    md += [
        "",
        "## Trampas plantadas",
        "",
        "| Clip | Autocorrección | Total incorrecto | Dirección con dígitos | Total dicho | Total correcto |",
        "|---|---|---|---|---|---|",
    ]
    for c in G.T2:
        md.append(
            f"| {c['id']} | {'sí' if c['autocorreccion'] else '—'} | {'sí' if c['total_incorrecto'] else '—'} "
            f"| {'sí' if c['direccion_digitos'] else '—'} | {c['gt']['total_dicho']} | {c['gt']['total_calculado']} |"
        )
    md += ["", "---", ""]
    for c in G.T2:
        md.append(md_guion(c, "llamada"))
        md.append(f"> Nota para el validador: {c['nota']}\n")
        md.append("---\n")
    (ROOT / "scripts" / "guiones_t2.md").write_text("\n".join(md), encoding="utf-8")
    return rows


def reporte(rows1, rows2):
    print("=== T1 ===")
    for r in rows1:
        print(f"{r['clip_id']}: {r['n_palabras']} palabras")
    print("Distribución nivel_ingles:", dict(Counter(r["nivel_ingles"] for r in rows1)))
    print("Distribución moneda:", dict(Counter(r["moneda"] for r in rows1)))
    print("=== T2 ===")
    for r in rows2:
        print(f"{r['clip_id']}: {r['n_palabras']} palabras")
    print("Autocorrecciones:", sum(r["trampa_autocorreccion"] for r in rows2), "(mín. 3)")
    print("Totales incorrectos:", sum(r["trampa_total_incorrecto"] for r in rows2), "(mín. 3)")
    print("Direcciones con dígitos:", sum(r["trampa_direccion_digitos"] for r in rows2), "(mín. 1)")
    for c in G.T2:
        calc = G.calcular_total(c["gt"]["items"], c["gt"]["promocion"])
        ok = calc == c["gt"]["total_calculado"]
        coherente = (c["gt"]["total_dicho"] != c["gt"]["total_calculado"]) == c["total_incorrecto"]
        print(f"  {c['id']}: calculado={calc} gt={c['gt']['total_calculado']} {'OK' if ok else 'ERROR'} | trampa coherente: {coherente}")


if __name__ == "__main__":
    r1, r2 = build_t1(), build_t2()
    reporte(r1, r2)
    sys.exit(0 if MD.verificar(G) else 1)
