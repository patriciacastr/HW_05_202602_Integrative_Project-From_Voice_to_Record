"""Parche: ajusta reglas de años, puesto y disponibilidad. Sin librerías de UI."""
import re, sys
from src import extract_rules as R

_disp_original = R.f_disponibilidad

def _parse_anios(pre, unidad, medio):
    ns = [n for n in R.scan_numbers(pre) if n[2] == len(pre)]
    if not ns:
        return None
    v = ns[-1][0] + (0.5 if medio else 0)
    return v / 12 if unidad == "meses" else v

def f_anios(text):
    t = R.norm(text)
    # 1) respuesta tras la pregunta: "¿Cuántos años...? Cuatro años."
    for m in re.finditer(r"cuant[oa]s? (?:anos|experiencia)[^?]*\?", t):
        post = t[m.end():m.end() + 60]
        mm = re.match(r"\s*(.+?)\s+(anos?|meses)\b( y medio)?", post)
        if mm:
            v = _parse_anios(mm.group(1), mm.group(2), bool(mm.group(3)))
            if v is not None:
                return v, m.group(0)[-25:] + " " + mm.group(0).strip()
    # 2) afirmación: "dos años y medio de experiencia"
    for m in re.finditer(r"(anos?|meses)( y medio)? de experiencia", t):
        pre = t[max(0, m.start() - 40):m.start()].rstrip()
        v = _parse_anios(pre, m.group(1), bool(m.group(2)))
        if v is not None:
            return v, m.group(0)
    return None, ""

def f_puesto(text):
    fin = r"(?= en [A-ZÁÉÍÓÚ]| de [A-ZÁÉÍÓÚ]|[,.])"
    pats = [r"[uú]ltimo (?:puesto|cargo)\s*[?:]?(?: fue| era)?(?: la| el| una| un)?\s+(.+?)" + fin,
            r"(?:trabaj[eé] como|fui|me desempe[ñn][eé] como)(?: la| el| una| un)?\s+(.+?)" + fin]
    for p in pats:
        m = re.search(p, text)
        if m:
            return m.group(1).strip(), m.group(0)
    return None, ""

def f_disponibilidad(text, ref):
    t = R.norm(text)
    anclas = sorted(re.finditer(r"incorpor|disponib|empezar|comenzar|iniciar", t),
                    key=lambda m: (not m.group().startswith("incorpor"), m.start()))
    for k in anclas:
        v, ev = _disp_original(text[k.start():], ref)
        if v:
            return v, ev
    return _disp_original(text, ref)

R.f_anios, R.f_puesto, R.f_disponibilidad = f_anios, f_puesto, f_disponibilidad

if __name__ == "__main__":
    R.evaluar(sys.argv[1] if len(sys.argv) > 1 else "large_cuda_fp16_gl")
