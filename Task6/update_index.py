import json
import logging
import os
import sys
import time
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

KB_DIR = Path(os.getenv("RAG_KB_DIR", "knowledge_base"))
DB_DIR = Path(os.getenv("RAG_CHROMA_DIR", "index/chroma_db"))
COLLECTION = os.getenv("RAG_COLLECTION", "knowledge_base")
STATE_FILE = Path(os.getenv("RAG_STATE_FILE", str(DB_DIR / "update_state.json")))
LOG_FILE = Path(os.getenv("RAG_UPDATE_LOG", "Task6/update.log"))

CHUNK_SIZE, CHUNK_OVERLAP = 500, 100
BATCH = 32

EMBED_MODEL = os.getenv("RAG_EMBED_MODEL", "Qwen/Qwen3-Embedding-0.6B")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()],)
log = logging.getLogger("update_index")


def load_state() -> dict:
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def file_sig(p: Path) -> dict:
    s = p.stat()
    return {"mtime": s.st_mtime, "size": s.st_size}


def chunk_file(text: str, source: str, title: str) -> tuple[list, list, list]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separators=["\n\n", "\n", ". ", " ", ""])
    pieces = splitter.split_text(text)
    ids, docs, metas = [], [], []
    for i, piece in enumerate(pieces):
        ids.append(f"{source}:{i}")
        docs.append(piece)
        metas.append({"source": source, "title": title, "chunk_id": i, "total_chunks": len(pieces)})
    return ids, docs, metas


def main() -> int:
    t0 = time.perf_counter()
    log.info("update started, kb=%s db=%s", KB_DIR, DB_DIR)

    if "--init-state" in sys.argv:
        sigs = {p.name: file_sig(p) for p in KB_DIR.glob("*.txt")}
        save_state(sigs)
        log.info("state initialized: %d files (no indexing)", len(sigs))
        return 0

    try:
        manifest = json.loads((KB_DIR / "manifest.json").read_text(encoding="utf-8"))
        title_by_file = {v: k for k, v in manifest.items()}
        state = load_state()

        current = {p.name: file_sig(p) for p in KB_DIR.glob("*.txt")}
        added = [f for f in current if f not in state]
        changed = [f for f in current if f in state and state[f] != current[f]]
        deleted = [f for f in state if f not in current]
        log.info("scan: %d files, added=%s changed=%s deleted=%s", len(current), added, changed, deleted)

        client = chromadb.PersistentClient(path=str(DB_DIR))
        col = client.get_collection(COLLECTION)
        model = SentenceTransformer(EMBED_MODEL, device=os.getenv("RAG_DEVICE", "cuda"), model_kwargs={"dtype": os.getenv("RAG_DTYPE_EMBED", "float16")})

        n_new_chunks = 0
        for fname in added + changed:
            ids, docs, metas = chunk_file((KB_DIR / fname).read_text(encoding="utf-8"), fname, title_by_file.get(fname, Path(fname).stem))
            col.delete(where={"source": fname})
            if ids:
                emb = model.encode(docs, batch_size=BATCH, normalize_embeddings=True).tolist()
                col.add(ids=ids, documents=docs, embeddings=emb, metadatas=metas)
                n_new_chunks += len(ids)
                log.info("indexed %s: %d chunks", fname, len(ids))

        for fname in deleted:
            col.delete(where={"source": fname})
            log.info("removed %s", fname)

        save_state(current)
        log.info("update finished in %.1fs: %d new chunks, index size=%d, errors=0", time.perf_counter() - t0, n_new_chunks, col.count())
        return 0
    except Exception:
        log.exception("update failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())