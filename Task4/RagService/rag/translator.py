import json
import re
from pathlib import Path

TERMS = json.loads(Path("terms_map.json").read_text(encoding="utf-8"))


def build_translation_rules(mapping: dict) -> list:
    pairs = sorted(mapping.items(), key=lambda kv: -len(kv[0]))
    return [
        (re.compile(r"(?<![A-Za-z])" + re.escape(k) + r"(?![A-Za-z])"), v)
        for k, v in pairs
    ]


def _canonical_reverse() -> dict:
    titles = set(json.loads(Path("knowledge_base/manifest.json").read_text(encoding="utf-8")).keys())
    by_value: dict[str, list[str]] = {}
    for k, v in TERMS.items():
        by_value.setdefault(v, []).append(k)
    reverse = {}
    for v, cands in by_value.items():
        titled = [c for c in cands if c in titles]
        #TODO: chose method from ENV VAR
        #reverse[v] = titled[0] if titled else sorted(cands, key=lambda c: (-len(c), c))[0]
        reverse[v] = titled[0] if titled else sorted(cands, key=lambda c: (c.endswith("s") and not c.endswith("'s"), -len(c), c))[0]
    return reverse


TO_FICTION = build_translation_rules(TERMS)
TO_REAL = build_translation_rules(_canonical_reverse())


def translate(text: str, rules=TO_FICTION) -> str:
    for pat, repl in rules:
        text = pat.sub(repl, text)
    return text


def to_fiction(text: str) -> str:
    return translate(text, TO_FICTION)


def to_real(text: str) -> str:
    return translate(text, TO_REAL)