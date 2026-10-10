import re
from pathlib import Path

LEFTOVER = [
    r"\bStargates?\b", r"\bGoa'uld\b", r"\bWraith\b", r"\bAncients?\b",
    r"\bAtlantis\b", r"\bDestiny\b", r"\bApophis\b", r"\bAsurans?\b",
    r"\bTodd\b", r"Area 51", r"\bTau'ri\b", r"\bJaffa\b", r"\bAsgard\b",
    r"\bThor\b", r"\bReplicators?\b", r"\bOri\b", r"\bPriors?\b", r"\bDoci\b",
    r"\bSangraal\b", r"\bSupergates?\b", r"\bHa'taks?\b", r"\bTel'taks?\b",
    r"\bAl'kesh\b", r"\bDeath Gliders?\b", r"\bunas\b", r"\bhive ships?\b",
    r"\bCheyenne\b", r"\bAbydos\b", r"\bChulak\b", r"\bDakara\b", r"\bDelmak\b",
    "Kree", r"\bShol'va?\b", r"\bNetu\b", r"\bIcarus\b", r"BC-30[1-4]",
    r"\bNaquadah\b", r"\bZPMs?\b", r"\bZero Point Modules?\b", r"\bSha're?\b",
    r"\bDHDs?\b", r"\bAnubis\b", r"\bDaedalus\b", r"\bPrometheus\b",
    r"\bKara kesh\b", r"\bhand device\b", r"\bribbon device\b",
    r"\bBa'al\b", r"\bHeru'ur\b", r"\bSokar\b", r"\bAmaunet\b", r"\bKlorel\b",
    r"\bMa'Tok\b", r"\bStaff weapons?\b", r"\bBra'tac\b", r"\bTretonin\b",
    r"\bTok'ra\b", r"\bSymbiotes?\b", r"\bSystem Lords?\b", r"\bPangarans?\b",
    r"O'Neill", r"\bCarter\b", r"Teal'c", r"\bJackson\b", r"\bZat'nik'tel\b",
    r"\bZats?\b", r"\bZat guns?\b", r"\bZa'tarcs?\b", r"\bMcKay\b",
    r"\bSheppard\b", r"\bKelno'reem\b", r"\bNakai\b", r"\bAdrias?\b",
    r"\bVala Mal Doran\b", r"Berzerker drones?", r"\bVala\b", r"\bWeir\b",
    r"\bTeyla\b", r"\bRonon\b", r"\bRush\b", r"\bYoung\b", r"Eli Wallace",
    r"SG-\d", r"\bReetou\b", r"\bRe'tu\b", r"\bReetalia\b",
    r"\bHarold Maybourne\b", r"\bMaybourne\b", r"Phase device",
    r"\bIris\b", r"Inverted phase communicator", r"Trinium",
    r"\bTollans?\b", r"\bTollana\b", r"\bCuria\b", r"\bOmoc\b",
    r"\bNarims?\b", r"Phase-shifting weapon", r"\bIon cannons?\b",
    r"\bSaritas?\b", r"\bPegasus galaxy\b", r"\bBeta Gates?\b",
]

PATTERNS = {t: re.compile(t) for t in LEFTOVER}

def main():
    files = sorted(Path("knowledge_base").glob("*.txt"))
    total = len(files)

    # STAGE 1. Collect data
    report = {t: {"count": 0, "files": set(), "contexts": []} for t in LEFTOVER}

    for p in files:
        text = p.read_text(encoding="utf-8")
        for t, pat in PATTERNS.items():
            matches = list(pat.finditer(text))
            if not matches:
                continue
            r = report[t]
            r["count"] += len(matches)
            r["files"].add(p.name)
            if len(r["contexts"]) < 3:
                for m in matches[: 3 - len(r["contexts"])]:
                    s, e = max(0, m.start() - 30), min(len(text), m.end() + 30)
                    r["contexts"].append((p.name, text[s:e].replace("\n", " ")))

    dirty_terms = {t: r for t, r in report.items() if r["count"] > 0}
    affected_files = set().union(*(r["files"] for r in dirty_terms.values())) if dirty_terms else set()

    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Files count: {total}")
    print(f"Files affected: {len(affected_files)} ({len(affected_files)/total*100:.1f}%)")
    print(f"Terms found: {len(dirty_terms)} of {len(LEFTOVER)}")
    print(f"Entries count: {sum(r['count'] for r in dirty_terms.values())}")

    # STAGE 2. Result output
    if not dirty_terms:
        print("\nAll clear")
        return

    # Term table
    print("\n" + "-" * 70)
    print(f"{'Term':<30} {'Entries':>10} {'Files':>8}")
    print("-" * 70)
    for t, r in sorted(dirty_terms.items(), key=lambda x: -x[1]["count"]):
        print(f"{t:<30} {r['count']:>10} {len(r['files']):>8}")

    print("\nAffected files:")
    for name in sorted(affected_files):
        terms_in_file = [t for t, r in dirty_terms.items() if name in r["files"]]
        print(f"  {name}: {terms_in_file}")

    # Contexts
    print("\n" + "-" * 70)
    print("Contexts (up to 3 per term)")
    print("-" * 70)
    for t, r in sorted(dirty_terms.items(), key=lambda x: -x[1]["count"]):
        print(f"\n### {t} ({r['count']} entries, {len(r['files'])} файлов)")
        for fname, ctx in r["contexts"]:
            print(f"  [{fname}] ...{ctx!r}...")


if __name__ == "__main__":
    main()