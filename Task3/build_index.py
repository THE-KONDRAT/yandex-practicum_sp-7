import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import json
import time
from pathlib import Path
import torch

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


KB_DIR = Path("knowledge_base")
DB_DIR = Path("index/chroma_db")
COLLECTION = "knowledge_base"

EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
USE_FP32 = True                                 # for GTX 1080 Ti fp16 was way more slowly than fp32
BATCH = 32                                      # optimal batch size for GTX 1080 Ti was measured during 1st task execution

def elapsed_since(start_time):
    return time.perf_counter() - start_time

def time_format(x):
    return f"{x:.1f}"

def main():
    manifest = json.loads((KB_DIR / "manifest.json").read_text(encoding="utf-8"))
    title_by_file = {v: k for k, v in manifest.items()}
    total_start = time.perf_counter()

    # Stage 1. Chunk generation
    stage_start = time.perf_counter()
    files = sorted(KB_DIR.glob("*.txt"))
    print(f"• STAGE 1 • Chunk generation started. Documents {len(files)}")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    ids, docs, metas = [], [], []
    for f in files:
        pieces = splitter.split_text(f.read_text(encoding="utf-8"))
        for i, piece in enumerate(pieces):
            ids.append(f"{f.name}:{i}")
            docs.append(piece)
            metas.append({
                "source": f.name,
                "title": title_by_file.get(f.name, f.stem),
                "chunk_id": i,
                "total_chunks": len(pieces),
            })
    t = elapsed_since(stage_start)
    print(f"• STAGE 1 • Chunk generation finished. Chunks: {len(docs)} "
          f"Elapsed: {time_format(t)} s ({len(docs)/t:.0f} chunks/s).\n"
          f"Total elapsed: {time_format(elapsed_since(total_start))} s")

    # Stage 2. Embeddings generation
    dtype = "float16"
    if USE_FP32:
        dtype = "float32"
        print("FP32 data type was selected manually")
    else:
        print("Checking if BF16 supported...")
        if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
            dtype = "bfloat16"
            print("BF16 not supported. using FP16.")
        else:
            print("BF16 is not supporting. FP16 will be used.")

    model = SentenceTransformer(
        EMBEDDING_MODEL, device="cuda",
        model_kwargs={"dtype": dtype},
    )

    stage_start = time.perf_counter()
    print(f"• STAGE 2 • Embeddings generation started. Chunks: [{len(docs)}] Model: [{EMBEDDING_MODEL}] Device: cuda, dtype: {dtype} Batch: [{BATCH}]")
    embeddings = model.encode(docs, batch_size=BATCH, show_progress_bar=True,
        normalize_embeddings=True,).tolist()
    t = elapsed_since(stage_start)
    print(f"• STAGE 2 • Embeddings generation ended. Embeddings: {len(embeddings)} x {len(embeddings[0])} "
          f"Elapsed: {time_format(t)} s ({len(docs)/t:.1f} chunks/s).\n"
          f"Total elapsed: {time_format(elapsed_since(total_start))} s")

    # Stage 3. Making collection in ChromaDb
    stage_start = time.perf_counter()
    print("• STAGE 3 • Index creation started.")
    client = chromadb.PersistentClient(path=str(DB_DIR))
    if COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION)
    collection = client.create_collection(
        COLLECTION,
        metadata={"hnsw:space": "cosine", "embedding_model": EMBEDDING_MODEL},
    )
    collection.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)
    print(f"• STAGE 3 • Index creation finished. Saved to {DB_DIR}/ Collection: [{COLLECTION}] Chunks: [{collection.count()}]"
          f"Elapsed: {time_format(elapsed_since(stage_start))} s\n"
          f"Total elapsed: {time_format(elapsed_since(total_start))} s")

if __name__ == "__main__":
    main()
