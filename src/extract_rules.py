"""Extracción por reglas (Fase 3, camino 1). Sin librerías de UI."""
import re, json, csv, sys, unicodedata, calendar
from datetime import date, timedelta
import yaml

def norm(s):
    """minúsculas y sin tildes (conserva el largo del texto, así las posiciones coinciden)"""
    s = unicodedata.normalize("NFD", unicodedata.normalize("NFC", s))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()

# ---------- números hablados y en dígitos ----------
UNID = {"cero":0,"uno":1,"dos":2,"tres":3,"cuatro":4,"cinco":5,"seis":6,"siete":7,"ocho":8,"nueve":9}
ESP = {"diez":10,"once":11,"doce":12,"trece":13,"catorce":14,"quince":15,"dieciseis":16,
       "diecisiete":17,"dieciocho":18,"diecinueve":19,"veinte":20,"veintiuno":21,"veintidos":22,
       "veintitres":23,"veinticuatro":24,"veinticinco":25,"veintiseis":26,"veintisiete":27,
       "veintiocho":28,"veintinueve":29}
DEC = {"treinta":30,"cuarenta":40,"cincuenta":50,"sesenta":60,"setenta":70,"ochenta":80,"noventa":90}
CEN = {"cien":100,"ciento":100,"doscientos":200,"trescientos":300,"cuatrocientos":400,
       "quinientos":500,"seiscientos":600,"setecientos":700,"ochocientos":800,"novecientos":900}
NUM = {**UNID, **ESP, **DEC, **CEN, "mil":1000}
for k, v in list(CEN.items()):               # femenino: quinientas, etc.
    if k.endswith("ientos"): NUM[k[:-2] + "as"] = v

def scan_numbers(t):
    """t ya normalizado. Devuelve [(valor, inicio, fin)], de dígitos y de palabras.
    Regla de dígitos: separador seguido de exactamente 3 dígitos = miles ('11.500' -> 11500);
    si no, es decimal ('2.5' -> 2.5)."""
    out = []
    for m in re.finditer(r"\d{1,3}(?:[.,]\d{3})+(?!\d)|\d+(?:[.,]\d+)?", t):
        s = m.group()
        if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", s):
            v = int(re.sub(r"[.,]", "", s))
        else:
            v = float(s.replace(",", "."))
            v = int(v) if v == int(v) else v
        out.append((v, m.start(), m.end()))
    toks = [(m.group(), m.start(), m.end()) for m in re.finditer(r"[a-z]+", t)]
    i = 0
    while i < len(toks):
        if toks[i][0] in NUM:
            j, total, cur = i, 0, 0
            while j < len(toks):
                w = toks[j][0]
                if w in NUM:
                    if w == "mil": total += max(cur, 1) * 1000; cur = 0
                    else: cur += NUM[w]
                    j += 1
                elif w == "y" and j + 1 < len(toks) and toks[j-1][0] in DEC and toks[j+1][0] in UNID:
                    j += 1                    # "treinta y cinco"
                else:
                    break
            out.append((total + cur, toks[i][1], toks[j-1][2]))
            i = j
        else:
            i += 1
    return sorted(out, key=lambda x: x[1])

# ---------- campos ----------
def f_anios(text):
    t = norm(text)
    for m in re.finditer(r"(anos?|meses) de experiencia|experiencia (?:de|por) (?:unos |aproximadamente )?", t):
        if m.group(1):                                   # "<num> años de experiencia"
            pre = t[max(0, m.start()-40):m.start()].rstrip()
            unidad = m.group(1)
            medio = pre.endswith("y medio")
            if medio: pre = pre[:-7].rstrip()
        else:                                            # "experiencia de <num> años"
            post = t[m.end():m.end()+40]
            mm = re.match(r"(.+?) (anos?|meses)", post)
            if not mm: continue
            pre, unidad, medio = mm.group(1), mm.group(2), False
        ns = scan_numbers(pre)
        ns = [n for n in ns if n[2] == len(pre)]
        if not ns: continue
        v = ns[-1][0] + (0.5 if medio else 0)
        if unidad == "meses": v = v / 12
        return v, m.group(0)
    return None, ""

def f_puesto(text):
    m = re.search(r"(?:[uú]ltimo (?:puesto|cargo)|trabaj[eé] como|fui|me desempe[ñn][eé] como)"
                  r"(?: fue| era)?(?: la| el| una| un)? (.+?)(?= en [A-ZÁÉÍÓÚ]|[,.])", text)
    return (m.group(1).strip(), m.group(0)) if m else (None, "")

def f_tecnologias(text, terms):
    hallados = []
    for term in terms:
        flags = 0 if len(term) == 1 else re.IGNORECASE   # "R" solo si es mayúscula
        if re.search(r"(?<![A-Za-z])" + r"\s+".join(map(re.escape, term.split())) + r"(?![A-Za-z])", text, flags):
            hallados.append(term)
    return hallados

def f_salario(text):
    t = norm(text)
    cands = []
    for m in re.finditer(r"\b(soles|sol|dolares|dolar|usd)\b|s/\.?|\$", t):
        pre = t[max(0, m.start()-45):m.start()].rstrip()
        pre = re.sub(r"\s*(nuevos)$", "", pre)
        ns = [n for n in scan_numbers(pre) if n[2] == len(pre) and n[0] >= 100]
        if ns:
            usd = bool(re.match(r"dolar|usd|\$", m.group()))
            cands.append((ns[-1][0], "USD" if usd else "PEN", m.start()))
    if not cands: return None, None, ""
    elegido = cands[0]
    if len(cands) > 1 and re.search(r"\b(no,|perdon|mejor dicho|corrijo|me equivoque|quise decir)",
                                    t[cands[0][2]:cands[-1][2]]):
        elegido = cands[-1]                              # autocorrección: gana el último
    return elegido[0], elegido[1], t[max(0, elegido[2]-30):elegido[2]+8]

MESES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre",
         "octubre","noviembre","diciembre"]

def add_months(d, n):
    m = d.month - 1 + n
    y, m = d.year + m // 12, m % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))

def f_disponibilidad(text, ref):
    t = norm(text)
    k = re.search(r"incorpor|disponib|empezar|comenzar|iniciar", t)
    w = t[k.start():k.start()+300] if k else t
    # 1) fecha absoluta: "primero de febrero", "quince de noviembre"
    for m in re.finditer(r"\bde (%s)\b" % "|".join(MESES), w):
        pre = w[max(0, m.start()-30):m.start()].rstrip()
        dia = 1 if pre.endswith("primero") else None
        if dia is None:
            ns = [n for n in scan_numbers(pre) if n[2] == len(pre)]
            dia = ns[-1][0] if ns else None
        if isinstance(dia, int) and 1 <= dia <= 31:
            mes = MESES.index(m.group(1)) + 1
            try:
                y = ref.year if date(ref.year, mes, dia) >= ref else ref.year + 1
                return date(y, mes, dia).isoformat(), pre[-12:] + " " + m.group()
            except ValueError:
                pass
    # 2) fin de mes
    m = re.search(r"fin(?:ales)? (?:de|del) mes", w)
    if m:
        return date(ref.year, ref.month, calendar.monthrange(ref.year, ref.month)[1]).isoformat(), m.group()
    # 3) relativa: "en dos semanas", "dentro de un mes"
    m = re.search(r"(?:\ben|dentro de) ([a-z0-9., ]{1,25}?) (semanas?|dias?|meses|mes)\b", w)
    if m:
        g = m.group(1).strip()
        ns = scan_numbers(g)
        n = 1 if g in ("un", "una") else (ns[0][0] if ns else None)
        if n is not None:
            u = m.group(2)
            d = add_months(ref, n) if u.startswith("mes") else ref + timedelta(days=n * (7 if u.startswith("sem") else 1))
            return d.isoformat(), m.group()
    if re.search(r"inmediat|ya mismo|desde ya", w):
        return ref.isoformat(), "inmediata"
    return None, ""

def f_ingles(text):
    t = norm(text)
    k = re.search(r"\bingles\b", t)
    w = t[k.start():k.start()+250] if k else t
    pats = {"avanzado": r"avanzado|\bc[12]\b|fluido|nativo|bilingue",
            "intermedio": r"intermedio|\bb[12]\b",
            "basico": r"basico|\ba[12]\b|elemental"}
    mejor = None
    for cat, p in pats.items():
        m = re.search(p, w)
        if m and (mejor is None or m.start() < mejor[1]): mejor = (cat, m.start(), m.group())
    return (mejor[0], mejor[2]) if mejor else (None, "")

# ---------- verificación literal ----------
def numero_en_transcripcion(valor, text):
    """¿el valor aparece literalmente (dígitos o palabras) en la transcripción?"""
    t = norm(text)
    ns = scan_numbers(t)
    if valor in {n[0] for n in ns}: return True
    for v, ini, fin in ns:
        if v == valor * 12 and re.match(r"\s+meses", t[fin:]): return True           # 0.5 <- "seis meses"
        if v == valor - 0.5 and re.match(r"\s+anos?\s+y\s+medio", t[fin:]): return True  # 2.5 <- "dos años y medio"
    return False

def extraer(text, cfg):
    ref = date.fromisoformat(cfg["extraction"]["fecha_referencia_t1"])
    terms = cfg["glossary"]["terms"]["t1"]
    r = {}
    v, ev = f_anios(text);       r["anios_experiencia"] = (v, ev, v is not None and numero_en_transcripcion(v, text))
    v, ev = f_puesto(text);      r["ultimo_puesto"] = (v, ev, bool(v) and norm(v) in norm(text))
    v = f_tecnologias(text, terms); r["tecnologias"] = (v, "", bool(v))   # cada término está literal por construcción
    monto, mon, ev = f_salario(text)
    r["pretension_salarial_monto"] = (monto, ev, monto is not None and numero_en_transcripcion(monto, text))
    r["pretension_salarial_moneda"] = (mon, ev, mon is not None)
    v, ev = f_disponibilidad(text, ref)
    r["disponibilidad"] = (v, ev, bool(ev))                  # fecha calculada: se verifica la expresión que la origina
    v, ev = f_ingles(text);      r["nivel_ingles"] = (v, ev, bool(ev))
    return {k: (val, ev, "verificado" if ok else "sin_verificar") for k, (val, ev, ok) in r.items()}

# ---------- evaluación contra el ground truth ----------
def evaluar(run="large_cuda_fp16_gl"):
    cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))
    gt = {r["clip_id"]: r for r in csv.DictReader(open(cfg["paths"]["gt_t1"], encoding="utf-8"))}
    filas = []
    for clip in cfg["clips"]["t1"]:
        text = json.load(open(f"{cfg['paths']['cache_asr']}/L0/{run}/{clip}.json", encoding="utf-8"))["text"]
        res = extraer(text, cfg); g = gt[clip]
        correcto = {
            "anios_experiencia": res["anios_experiencia"][0] is not None and abs(res["anios_experiencia"][0] - float(g["anios_experiencia"])) < 1e-6,
            "ultimo_puesto": norm(res["ultimo_puesto"][0] or "") == norm(g["ultimo_puesto"]),
            "tecnologias": set(res["tecnologias"][0]) == set(g["tecnologias"].split("|")),
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
    n_ok = sum(f["correcto"] for f in filas)
    print(f"\nExactitud global (reglas, {run}): {n_ok}/{len(filas)} = {n_ok/len(filas):.2f}")
    with open(f"{cfg['paths']['tables']}/t1_reglas_{run}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=filas[0].keys()); w.writeheader(); w.writerows(filas)

if __name__ == "__main__":
    evaluar(sys.argv[1] if len(sys.argv) > 1 else "large_cuda_fp16_gl")
