import argparse
import json
import sys
import urllib.request

API = "http://localhost:8088/ask"
DONT_KNOW = "Я не знаю"

def ask(q: str) -> dict:
    req = urllib.request.Request(API, data=json.dumps({"question": q}).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=300).read())

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--golden", default="Task7/golden_questions.json")
    p.add_argument("--out", default="Task7/evaluate_report.json", help="report path (default evaluate_report.json)")
    args = p.parse_args()

    cases = json.load(open(args.golden, encoding="utf-8"))
    results, ok = [], 0
    for c in cases:
        r = ask(c["q"])
        refused = r["answer"] == DONT_KNOW
        if c["expect"] == "answer":
            passed = (not refused) and len(r["answer"]) > 40
        else:
            passed = refused
        ok += passed
        results.append({**c, "passed": passed, "dist_top1": r["dist_top1"], "sources": [s["title"] for s in r["sources"]],
                        "answer_head": r["answer"][:120]})
        print(f"{'PASS' if passed else 'FAIL'}  [{c['expect']:>9}]  {c['q']}  dist={r['dist_top1']}")

    summary = {"total": len(cases), "passed": ok, "accuracy": round(ok / len(cases), 3), "results": results}
    json.dump(summary, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\naccuracy: {ok}/{len(cases)} = {summary['accuracy']}  -> {args.out}")

if __name__ == "__main__":
    main()