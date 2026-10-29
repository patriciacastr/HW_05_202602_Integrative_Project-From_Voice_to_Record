"""Convierte docs/guiones/*.md en transcripciones de referencia (texto plano, sin A:/B:)."""
import re
import sys
from pathlib import Path
import yaml

cfg = yaml.safe_load(open("config.yaml", encoding="utf-8"))
out = Path(cfg["paths"]["reference_dir"]); out.mkdir(parents=True, exist_ok=True)
n = 0
for md in sorted(Path(cfg["paths"]["guiones_dir"]).glob("guiones_t*.md")):
    clip, lines = None, {}
    for raw in md.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (t[12]_\d\d)\b", raw)
        if m:
            clip = m.group(1); lines[clip] = []; continue
        m = re.match(r"^\*\*[AB]:\*\*\s*(.+)$", raw)
        if clip and m:
            lines[clip].append(m.group(1).strip())
    for c, ls in lines.items():
        (out / f"{c}.txt").write_text(" ".join(ls) + "\n", encoding="utf-8"); n += 1
        print(f"{c}: {len(' '.join(ls).split())} palabras")
print(f"{n} referencias escritas en {out}")
