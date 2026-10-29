"""Aplica el relleno a los guiones y verifica la cantidad que pide el caso.

Caso: 4-5 clips por tarea, 2-4 min cada uno, ~16-20 min de audio por tarea.
Estimación: 140 palabras/min + 0.5 s de pausa por cambio de turno.
"""
from __future__ import annotations

PAL_MIN = 140
PAUSA_S = 0.5


def dur_est(lineas) -> float:
    palabras = sum(len(t.split()) for _, t in lineas)
    return palabras / PAL_MIN + len(lineas) * PAUSA_S / 60


def _coincide(texto: str, ancla: str) -> bool:
    return texto == ancla or (len(ancla) > 25 and texto.startswith(ancla))


def aplicar_relleno(clips, relleno) -> None:
    """Inserta cada bloque justo después de su línea ancla, verificando que los turnos alternen."""
    for c in clips:
        if c["id"] not in relleno:
            continue
        ancla, bloque = relleno[c["id"]]
        ls = c["lineas"]
        pos = [i for i, (_, t) in enumerate(ls) if _coincide(t, ancla)]
        assert len(pos) == 1, f"{c['id']}: ancla ambigua o inexistente ({len(pos)}): {ancla!r}"
        i = pos[0]
        hab_ancla = ls[i][0]
        assert len(bloque) % 2 == 0, f"{c['id']}: el bloque debe tener longitud par"
        assert bloque[0][0] != hab_ancla, f"{c['id']}: el bloque debe empezar con el otro hablante"
        for (h1, _), (h2, _) in zip(bloque, bloque[1:]):
            assert h1 != h2, f"{c['id']}: turnos repetidos dentro del bloque"
        if i + 1 < len(ls):
            assert ls[i + 1][0] != bloque[-1][0], f"{c['id']}: turno repetido al cerrar el bloque"
        c["lineas"] = ls[: i + 1] + list(bloque) + ls[i + 1:]


def turnos_repetidos(clips):
    """Devuelve (clip, indice) donde el mismo hablante habla dos veces seguidas."""
    out = []
    for c in clips:
        for k in range(1, len(c["lineas"])):
            if c["lineas"][k][0] == c["lineas"][k - 1][0]:
                out.append((c["id"], k))
    return out


def verificar(G) -> bool:
    ok = True
    print("\n=== Alineación con el caso (4-5 clips, 2-4 min c/u, ~16-20 min por tarea) ===")
    for nombre, clips in (("T1 entrevistas", G.T1), ("T2 llamadas", G.T2)):
        total = 0.0
        for c in clips:
            m = dur_est(c["lineas"])
            total += m
            bien = 2.0 <= m <= 4.0
            ok &= bien
            print(f"  {c['id']}: ~{m:.1f} min {'OK' if bien else '<-- FUERA DE 2-4 MIN'}")
        n_ok = 4 <= len(clips) <= 5
        t_ok = 16.0 <= total <= 20.0
        ok &= n_ok and t_ok
        print(f"  {nombre}: {len(clips)} clips {'OK' if n_ok else 'FUERA'} | total ~{total:.1f} min {'OK' if t_ok else 'FUERA DE 16-20'}")
    rep = turnos_repetidos(G.T1) + turnos_repetidos(G.T2)
    print("  Turnos dobles del mismo hablante:", rep if rep else "ninguno")
    ok &= not rep
    return ok
