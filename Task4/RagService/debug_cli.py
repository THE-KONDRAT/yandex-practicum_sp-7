import os

_prev_debug = os.environ.get("RAG_DEBUG_PROMPT")
os.environ["RAG_DEBUG_PROMPT"] = "true"

try:
    from rag.config import SETTINGS
    from rag.pipeline import RagPipeline

    bot = RagPipeline(SETTINGS)

    print("RAG-bot (debug). Enter to exit.")
    while True:
        q = input("\nQ: ").strip()
        if not q:
            break
        r = bot.answer(q)
        print(f"[internal query]: {r['internal_query']}")
        print(f"[dist_top1={r['dist_top1']}]")
        print(f"A: {r['answer']}")
        print(f"[internal answer]: {r['internal_answer']}")
        for s in r["sources"][:3]:
            print(f"  src: {s['title']} ({s['source']}:{s['chunk_id']}) dist={s['dist']}")

        print(f"[stages]: {r['stages']}")

finally:
    if _prev_debug is None:
        os.environ.pop("RAG_DEBUG_PROMPT", None)
    else:
        os.environ["RAG_DEBUG_PROMPT"] = _prev_debug