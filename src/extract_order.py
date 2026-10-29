"""Tarea 2: extractor de pedidos + validación aritmética + diagnóstico. Sin librerías de UI."""
import re, json, csv, sys, yaml
from collections import Counter
from src import extract_rules as R

PRODUCTOS = [  # la sopa va primero para que "sopa de wantán" no se confunda con "wantán frito"
    ("sopa de wantán", r"sopas? de (?:wantan(?:es)?|wanton|guantan(?:es)?)"),
    ("wantán frito", r"(?:porcion(?:es)? de )?(?:wantan(?:es)?|wanton(?:es)?|guantan(?:es)?)(?: frit[oa]s?)?"),
    ("arroz chaufa", r"arro(?:z|ces)(?: chaufa)?|chaufas?|chafas?|chafos?"),
    ("tallarín saltado", r"tallarin(?:es)?(?: saltad[oa]s?)?"),
    ("gaseosa", r"gaseosas?"),
    ("limonada", r"(?:jarras? de )?limonadas?"),
]

def oraciones(text):
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text) if s.strip()]

def productos_en(t):
    usados, out = [], []
    for prod, pat in PRODUCTOS:
        for m in re.finditer(r"\b(?:" + pat + r")\b", t):
            if any(m.start() < e and m.end() > s for s, e in usados):
                continue
            usados.append((m.start(), m.end())); out.append((m.start(), m.end(), prod))
    return sorted(out)

def items_de(sent, carta_tam):
    t = R.norm(sent); items, prev = [], 0
    for s, e, prod in productos_en(t):
        seg = t[prev:s].rstrip(); prev = e
        ns = [n for n in R.scan_numbers(seg) if n[2] == len(seg)]
        cant = ns[-1][0] if ns else 1                       # "un/una" o sin número = 1
        tams = carta_tam[prod]
        if len(tams) == 1: tam = tams[0]
        else:
            mm = re.match(r"\s*(personal|familiar)", t[e:e + 30]); tam = mm.group(1) if mm else None
        items.append({"producto": prod, "tamano": tam, "cantidad": cant})
    return items

def f_items(text, carta_tam):
    """Regla: el pedido es la ÚLTIMA oración, antes de que se digan los precios, que lista >=2 productos.
    Así gana la versión final cuando el cliente se corrige (la vendedora repite el pedido corregido)."""
    sents = oraciones(text)
    ip = next((i for i, s in enumerate(sents) if re.search(r"precios son|cuesta", R.norm(s))), len(sents))
    cand = []
    for i, s in enumerate(sents[:ip]):
        if "soles" in R.norm(s): continue
        its = items_de(s, carta_tam)
        if len({x["producto"] for x in its}) >= 2: cand.append(its)
    corr = any(re.search(r"\bmejor\b|perdon|pensandolo bien|espera", R.norm(s)) for s in sents[:ip])
    return (cand[-1] if cand else []), corr

def f_promo(text):
    t = R.norm(text)
    if re.search(r"no aplica (?:ninguna )?promocion|no hay promocion", t): return None
    if re.search(r"tres por dos", t): return "Q2"
    if "descuento" in t: return "Q1"
    return None

def f_direccion(text):
    sents = oraciones(text); n = [R.norm(s) for s in sents]
    ini = next((i for i, s in enumerate(n) if "direccion" in s), None)
    if ini is None:
        return None
    fin = next((i for i in range(ini, len(n)) if "pagar" in n[i]), len(n) - 1)
    cand = []
    for s in sents[ini + 1: fin + 1]:
        corte = s.split("¿")[0].strip(" ,.")
        if re.search(r"\b(avenida|av\.?|jiron|giron|calle|pasaje|jr\.?)\b", R.norm(corte)): cand.append(corte)
    return cand[-1] if cand else None       # la última: la vendedora repite la dirección

def f_pago(text):
    sents = oraciones(text); n = [R.norm(s) for s in sents]
    ini = next((i for i, s in enumerate(n) if "pagar" in s), 0)
    ventana = " ".join(n[ini: ini + 3]); mejor = None
    for w in ("yape", "tarjeta", "efectivo"):
        m = re.search(w, ventana)
        if m and (mejor is None or m.start() < mejor[1]): mejor = (w, m.start())
    return mejor[0] if mejor else None

def f_total_menciones(text):
    sents = oraciones(text)
    ini = next((i for i, s in enumerate(sents) if re.search(r"\btotal\b", R.norm(s))), None)
    if ini is None: return []
    out = []
    for s in sents[ini:]:
        t = R.norm(s)
        vals = [x[0] for x in R.scan_numbers(t) if re.match(r"\s*soles?\b", t[x[2]:])]
        if vals: out.append(vals[-1])
    return out

def calcular(items, promo, carta):
    sub = sum(i["cantidad"] * carta.get(f'{i["producto"]}|{i["tamano"]}', 0) for i in items)
    if promo == "Q1" and sub >= 90: sub -= 15
    elif promo == "Q2": sub -= (sum(i["cantidad"] for i in items if i["producto"] == "gaseosa") // 3) * 5
    return sub

def _subsecuencia(a, b):
    it = iter(b)
    return all(ch in it for ch in a)

def diagnosticar(menciones, calculado):
    """Si el desajuste existe: total repetido >=2 veces con el mismo valor -> error del HABLANTE;
    si no se repite y alguna mención coincide con el cálculo -> error del ASR; si no, indeterminado."""
    c = Counter(menciones); ult = {v: i for i, v in enumerate(menciones)}
    dicho = max(c, key=lambda v: (c[v], ult[v]))
    if dicho == calculado: return dicho, "coincide"
    if len(str(dicho)) < len(str(calculado)) and _subsecuencia(str(dicho), str(calculado)):
        return dicho, "asr"           # regla v2: al valor dicho le falta un dígito del cálculo ("13" vs "113")
    if c[dicho] >= 2: return dicho, "hablante"
    if calculado in c: return dicho, "asr"
    return dicho, "indeterminado"

def procesar(text, carta):
    """Función de entrada para un transcript de llamada (la usa también la app)."""
    carta_tam = {}
    for k in carta:
        p, t = k.split("|"); carta_tam.setdefault(p, []).append(t)
    items, corr = f_items(text, carta_tam)
    for i in items: i["precio_unitario"] = carta.get(f'{i["producto"]}|{i["tamano"]}')
    promo = f_promo(text); mens = f_total_menciones(text)
    calc = calcular(items, promo, carta)
    dicho, diag = diagnosticar(mens, calc) if mens else (None, "sin_total")
    return {"items": items, "promocion": promo, "direccion_entrega": f_direccion(text),
            "metodo_pago": f_pago(text), "total_dicho": dicho, "menciones_total": mens,
            "total_calculado": calc, "autocorreccion_detectada": corr, "diagnostico": diag}

def _normdir(s):
    if not s: return ""
    s = R.norm(s).replace("giron", "jiron")
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", s)).replace(" en ", " ").strip()

def _nums(s):
    return sorted(x[0] for x in R.scan_numbers(R.norm(s or "")))

def evaluar(run="large_cuda_fp16_gl", level="L0"):
    cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))
    gt = json.load(open(cfg["paths"]["gt_t2"], encoding="utf-8"))
    carta = gt["carta"]; filas = []; ok_n = tot_n = 0
    for clip in cfg["clips"]["t2"]:
        text = json.load(open(f"{cfg['paths']['cache_asr']}/{level}/{run}/{clip}.json", encoding="utf-8"))["text"]
        r = procesar(text, carta); g = gt["clips"][clip]
        set_e = {(i["producto"], i["tamano"], i["cantidad"]) for i in r["items"]}
        set_g = {(i["producto"], i["tamano"], i["cantidad"]) for i in g["items"]}
        ok = {"items": set_e == set_g, "promocion": r["promocion"] == g["promocion"],
              "direccion_entrega": _normdir(r["direccion_entrega"]) == _normdir(g["direccion_entrega"]),
              "direccion_numeros": _nums(r["direccion_entrega"]) == _nums(g["direccion_entrega"]),
              "metodo_pago": r["metodo_pago"] == g["metodo_pago"],
              "total_dicho": r["total_dicho"] == g["total_dicho"]}
        print(f"\n== {clip} ==  menciones del total: {r['menciones_total']}")
        for k, v in ok.items():
            print(f"  {'OK   ' if v else 'FALLA'} {k}"); ok_n += v; tot_n += 1
        if not ok["items"]: print("     extraído:", sorted(set_e, key=str), "\n     gt:      ", sorted(set_g, key=str))
        if not ok["direccion_entrega"]: print("     dirección extraída:", r["direccion_entrega"], "| gt:", g["direccion_entrega"])
        trampa = g["total_dicho"] != g["total_correcto"]
        marcado = r["total_calculado"] != r["total_dicho"]
        causa_real = "asr" if r["total_dicho"] != g["total_dicho"] else ("hablante" if trampa else "ninguna")
        print(f"  VALIDADOR: calculado={r['total_calculado']} dicho={r['total_dicho']} -> "
              f"{'ALERTA' if marcado else 'sin alerta'} | trampa plantada={trampa} | diagnóstico={r['diagnostico']} (real={causa_real})")
        filas.append({"clip": clip, "nivel": level, "calculado": r["total_calculado"], "dicho_extraido": r["total_dicho"],
                      "alerta": marcado, "trampa": trampa, "atrapada": marcado and trampa, "perdida": trampa and not marcado,
                      "falsa_alarma": marcado and not trampa, "diagnostico": r["diagnostico"], "causa_real": causa_real,
                      **{f"ok_{k}": v for k, v in ok.items()}})
    print(f"\nExactitud de campos ({run}, {level}): {ok_n}/{tot_n} = {ok_n/tot_n:.2f}")
    print(f"Trampas atrapadas: {sum(f['atrapada'] for f in filas)}/{sum(f['trampa'] for f in filas)} | "
          f"perdidas: {sum(f['perdida'] for f in filas)} | falsas alarmas: {sum(f['falsa_alarma'] for f in filas)}")
    with open(f"{cfg['paths']['tables']}/t2_pedido_{run}_{level}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=filas[0].keys()); w.writeheader(); w.writerows(filas)

if __name__ == "__main__":
    evaluar(sys.argv[1] if len(sys.argv) > 1 else "large_cuda_fp16_gl", sys.argv[2] if len(sys.argv) > 2 else "L0")
