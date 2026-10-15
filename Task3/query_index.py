import json
import re
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

DB_DIR = "index/chroma_db"
USE_FP32 = True                                 # for GTX 1080 Ti fp16 was way more slowly than fp32
COLLECTION = "knowledge_base"
TOP_K = 3
QUERY_PROMPT = "Instruct: Given a question, retrieve relevant passages that answer the question"

TERMS = json.loads(Path("terms_map.json").read_text(encoding="utf-8"))

def build_translation_rules(mapping: dict) -> list:
    pairs = sorted(mapping.items(), key=lambda kv: -len(kv[0]))
    return [
        (re.compile(r"(?<![A-Za-z])" + re.escape(k) + r"(?![A-Za-z])"), v)
        for k, v in pairs
    ]

def build_reverse_translation_rules(terms: dict) -> list:
    fictional_titles = set(json.loads(Path("knowledge_base/manifest.json").read_text(encoding="utf-8")).keys())
    by_value: dict[str, list[str]] = {}
    for k, v in terms.items():
        by_value.setdefault(v, []).append(k)

    reverse = {}
    for v, cands in by_value.items():
        titled = [c for c in cands if c in fictional_titles]
        chosen = titled[0] if titled else sorted(cands, key=lambda c: (c.endswith("s") and not c.endswith("'s"), -len(c), c))[0]
        if len(cands) > 1:
            print(f"  [reverse] ambiguous '{v}': {cands} -> '{chosen}'")
        reverse[v] = chosen
    return build_translation_rules(reverse)

TO_FICTION = build_translation_rules(TERMS)
TO_REAL = build_reverse_translation_rules(TERMS)

def translate(text: str, rules: list) -> str:
    for pat, repl in rules:
        text = pat.sub(repl, text)
    return text


QUESTIONS = [
    "Who built the Stargates?",
    "How did Apophis die?",
    "How does the Zero Point Module work?",
    "Where were ion cannons built?",
    "By whom the Destiny was built?",
    "Who is Thor?"
]


def main():
    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_collection(COLLECTION)

    dtype = "float16"
    if USE_FP32:
        dtype = "float32"
        print("FP32 data type was selected manually")
    else:
        print("Checking if BF16 supported...")
        if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
            dtype = "bfloat16"
            print("BF16 supported. Using BF16.")
        else:
            print("BF16 is not supporting. FP16 will be used.")

    model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B", device="cuda", model_kwargs={"dtype": dtype},)

    for n, q in enumerate(QUESTIONS, 1):
        q_internal = translate(q, TO_FICTION)
        print(f"\n{'=' * 72}")
        print(f"[{n}/{len(QUESTIONS)}] REQUEST : {q}")
        print(f"          INTERNAL: {q_internal}")

        qv = model.encode([q_internal], prompt=QUERY_PROMPT, normalize_embeddings=True).tolist()
        res = collection.query(query_embeddings=qv, n_results=TOP_K)

        for i in range(TOP_K):
            meta = res["metadatas"][0][i]
            dist = res["distances"][0][i]
            chunk_internal = res["documents"][0][i]
            chunk_shown = translate(chunk_internal, TO_REAL)
            print(f"\n  ── [{i + 1}] dist={dist:.4f} │ {meta['title']} "
                  f"({meta['source']}, chunk {meta['chunk_id']}/{meta['total_chunks']})")
            shown_flat = " ".join(chunk_shown.split())[:200]
            internal_flat = " ".join(chunk_internal.split())[:200]
            print(f"     shown    : {shown_flat}")
            print(f"     internal : {internal_flat}")


if __name__ == "__main__":
    main()