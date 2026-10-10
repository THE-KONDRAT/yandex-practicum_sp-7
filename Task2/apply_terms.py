import hashlib
import json
import random
import re
from pathlib import Path

RAW_DIR = Path("raw_pages")
OUT_DIR = Path("knowledge_base")
OUT_DIR.mkdir(exist_ok=True)

SEED_PATH = Path("Task2/terms_seed.json")

FIRST = ["Kae", "Vel", "Mor", "Dra", "Rho", "Nyx", "Tor", "Zha", "Kor", "Vex",
         "Ael", "Dor", "Gal", "Kel", "Lor", "Mal", "Nor", "Per", "Sel", "Tal",
         "Vor", "Xan", "Yor", "Zor", "Bra", "Cyn", "Fen", "Hal", "Ish", "Jor"]
LAST = ["morghul", "voss", "keth", "ryker", "solen", "reeve", "tallis", "vell",
        "drax", "korr", "vex", "nar", "thar", "dune", "marc", "holt", "rynn",
        "skov", "brandt", "crowe", "zyx", "lynn"]

LOC = ['Reach', 'Drift', 'Hollow', 'Spire', 'March', "Synth" ]
FRAC = ['Order', 'Concord', 'Pact', 'Compact']

# Planet code Regex
PLANET_CODE_RE = re.compile(r"\b[A-Z]{1,2}\d{1,2}[A-Z]-\d{3}\b")


def gen_name(term: str, kind: str = "tech") -> str:
    h = int.from_bytes(hashlib.sha256(term.encode()).digest()[:8])
    rng = random.Random(h)
    if kind == "person":
        return f"{rng.choice(FIRST)} {rng.choice(LAST).title()}"
    if kind == "location":
        return f"{rng.choice(FIRST)} {rng.choice(LOC)}"
    if kind == "fraction":
        return f"{rng.choice(FRAC)} of {rng.choice(FIRST)}{rng.choice(LAST).title()}"
    return rng.choice(FIRST) + rng.choice(LAST)


def repl_planet_code(m: re.Match) -> str:
    code = m.group(0)
    h = sum(ord(c) for c in code) % 26
    return f"V{chr(65 + h)}-{code[-3:]}"


def resolve(seed_entries: list, corpus_texts: list[str]) -> dict[str, str]:
    resolved, used = {}, set()
    for e in seed_entries:
        if "term" in e:
            name = e.get("name")
            if not name:
                name = gen_name(e["term"], e.get("kind", "tech"))
                salt = 0
                while name in used:
                    salt += 1
                    name = gen_name(f'{e["term"]}#{salt}', e.get("kind", "tech"))
            if name in used:
                print(f"  [warn] ручное имя '{name}' уже занято ({e['term']})")
            used.add(name)
            resolved[e["term"]] = name
        else:
            pat = re.compile(e["pattern"])
            for text in corpus_texts:
                for m in pat.finditer(text):
                    key = m.group(0)
                    resolved[key] = pat.sub(
                        lambda mm, t=e["template"]: t.format(*mm.groups()), key)
    # store planet codes
    for text in corpus_texts:
        for m in PLANET_CODE_RE.finditer(text):
            resolved.setdefault(m.group(0), repl_planet_code(m))
    return resolved


def make_search_pattern(term: str) -> re.Pattern:
    return re.compile(r"(?<![A-Za-z])" + re.escape(term) + r"(?![A-Za-z])")


def sanitize_filename(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")


def main():
    manifest = json.loads((RAW_DIR / "manifest.json").read_text(encoding="utf-8"))

    corpus = {fname: (RAW_DIR / fname).read_text(encoding="utf-8")
              for _, fname in manifest.items()}
    corpus_texts = list(corpus.values())

    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    TERMS = resolve(seed, corpus_texts)

    entries = sorted(
        ((k, make_search_pattern(k), v) for k, v in TERMS.items()),
        key=lambda e: -len(e[0]),
    )

    stats = {k: 0 for k in TERMS}
    new_manifest = {}

    # clear old files
    for old in OUT_DIR.glob("*.txt"):
        old.unlink()

    for title, fname in manifest.items():
        text = corpus[fname]
        text = text.replace("\u2019", "'").replace("\u2018", "'")

        for key, pat, repl in entries:
            text, n = pat.subn(repl, text)
            stats[key] += n

        new_title = TERMS.get(title, title)
        new_fname = f"{sanitize_filename(new_title)}.txt"
        (OUT_DIR / new_fname).write_text(text, encoding="utf-8")
        new_manifest[new_title] = new_fname

    (OUT_DIR / "manifest.json").write_text(
        json.dumps(new_manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    Path("terms_map.json").write_text(
        json.dumps(TERMS, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("=== STATS ===")
    for k, v in sorted(stats.items(), key=lambda x: -x[1])[:20]:
        print(f"  {k} -> {TERMS[k]}: {v}")
    planets = [k for k in TERMS if PLANET_CODE_RE.fullmatch(k)]
    print(f"  [codes of planets recorded]: {len(planets)}")

    zero = [k for k, v in stats.items() if v == 0]
    if zero:
        print(f"\nNot found ({len(zero)}): {zero}")
    print(f"\nTransformation done: {len(new_manifest)} docs in {OUT_DIR}/")


if __name__ == "__main__":
    main()