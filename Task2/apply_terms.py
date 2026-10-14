import argparse
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

GALLERY_RE = re.compile(r"\.(png|jpe?g|gif)\s*\|", re.I)
MIN_CHUNK_LEN = 120

def gen_name_part(term: str, part: str) -> str:
    h = int.from_bytes(hashlib.sha256(f"{term}:{part}".encode()).digest()[:8])
    rng = random.Random(h)
    pool = FIRST if part == "first" else LAST
    return rng.choice(pool).title() if part == "first" else rng.choice(pool)


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


def pick_name_part(full: str, is_first: bool) -> str:
    return full.split()[0] if is_first else full.split()[-1]


def resolve(seed_entries: list, corpus_texts: list[str]) -> dict[str, str]:
    resolved, used = {}, set()
    pattern_entries = [e for e in seed_entries if "pattern" in e]
    refs = []

    # PASS 1: Common terms
    for e in seed_entries:
        if "pattern" in e:
            continue
        t = e["term"]

        if "first_of" in e or "last_of" in e:   # links
            refs.append(e)
            continue

        # 1. name
        if e.get("name"):
            name = e["name"]
        elif e.get("kind") == "person":
            name = (f'{e.get("first") or gen_name_part(t, "first")} '
                    f'{e.get("last") or gen_name_part(t, "last")}')
        else:
            name = gen_name(t, e.get("kind", "tech"))

        # 2. name deduplication
        if e.get("name"):
            if name in used:
                print(f"  [warn] user specified name '{name}' has already  taken ({t})")
        else:
            salt = 0
            while name in used:
                salt += 1
                name = gen_name(f"{t}#{salt}", e.get("kind", "tech"))
        used.add(name)

        # 3. terms with synonyms are reduced to a single name
        resolved[t] = name
        for syn in e.get("synonyms", []):
            if syn in resolved and resolved[syn] != name:
                print(f"  [warn] synonym '{syn}' has already mapped to '{resolved[syn]}' "
                      f"(pass for '{t}')")
                continue
            resolved[syn] = name

    # PASS 2: name parts
    part_owner: dict[str, str] = {}

    for e in refs:
        parent = e.get("first_of") or e.get("last_of")
        is_first = "first_of" in e

        part = pick_name_part(resolved[parent], is_first)

        if part in part_owner and part_owner[part] != parent:
            # When firts/last name collision found full name regeneration needed
            salt = 1
            while True:
                new_name = gen_name(f"{parent}#{salt}", "person")
                if pick_name_part(new_name, is_first) not in part_owner \
                        and new_name not in used:
                    break
                salt += 1
            print(f"  [ref] collision on '{part}': '{parent}' renamed "
                  f"{resolved[parent]} -> {new_name}")
            used.discard(resolved[parent])   # release old name
            used.add(new_name)
            resolved[parent] = new_name
            # reissue all refs
            for e2 in refs:
                if (e2.get("first_of") or e2.get("last_of")) == parent:
                    resolved[e2["term"]] = pick_name_part(
                        new_name, "first_of" in e2)

        part = pick_name_part(resolved[parent], is_first)
        part_owner[part] = parent
        resolved[e["term"]] = part
        print(f'  [ref] {e["term"]} -> {part} (of {parent})')

    # PASS 3: pattern-records (SG-N)
    for e in pattern_entries:
        pat = re.compile(e["pattern"])
        for text in corpus_texts:
            for m in pat.finditer(text):
                key = m.group(0)
                resolved[key] = pat.sub(
                    lambda mm, t=e["template"]: t.format(*mm.groups()), key)

    # PASS 4: planet codes
    for text in corpus_texts:
        for m in PLANET_CODE_RE.finditer(text):
            resolved.setdefault(m.group(0), repl_planet_code(m))

    return resolved


def make_search_pattern(term: str) -> re.Pattern:
    return re.compile(r"(?<![A-Za-z])" + re.escape(term) + r"(?![A-Za-z])")


def sanitize_filename(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")



def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--raw-dir", default="raw_pages")
    p.add_argument("--out-dir", default="knowledge_base")
    p.add_argument("--terms-out", default="terms_map.json")
    p.add_argument("--seed", default="Task2/terms_seed.json")
    return p.parse_args()


def main():
    args = parse_args()
    RAW_DIR, OUT_DIR = Path(args.raw_dir), Path(args.out_dir)
    OUT_DIR.mkdir(exist_ok=True)
    SEED_PATH = Path(args.seed)

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

        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+\n", "\n", text)

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

    Path(args.terms_out).write_text(json.dumps(TERMS, ensure_ascii=False, indent=2), encoding="utf-8")

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