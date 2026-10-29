"""Normalización de texto para comparar transcripciones (WER/CER).
Misma regla para referencia e hipótesis. Sin imports de UI."""
import re
import unicodedata
from num2words import num2words

_THOUSANDS = re.compile(r"(?<=\d)[.,](?=\d{3}(?:\D|$))")   # 5.200 / 5,200 -> 5200
_DIGITS = re.compile(r"\d+(?:[.,]\d+)?")


def _digits_to_words(text: str) -> str:
    def repl(m):
        s = m.group(0).replace(",", ".")
        try:
            n = float(s)
            n = int(n) if n.is_integer() else n
            return " " + num2words(n, lang="es") + " "
        except Exception:
            return m.group(0)
    return _DIGITS.sub(repl, text)


def normalize(text: str, cfg: dict) -> str:
    t = unicodedata.normalize("NFC", text)
    if cfg.get("lowercase", True):
        t = t.lower()
    if cfg.get("digits_to_words", True):
        t = _THOUSANDS.sub("", t)
        t = _digits_to_words(t)
    if cfg.get("strip_punctuation", True):
        t = re.sub(r"[^\w\s]", " ", t, flags=re.UNICODE)
        t = t.replace("_", " ")
    if not cfg.get("keep_accents", True):
        t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    if cfg.get("collapse_whitespace", True):
        t = re.sub(r"\s+", " ", t).strip()
    return t
