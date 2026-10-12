import os

import chromadb
import torch
from sentence_transformers import SentenceTransformer

from .config import load_text, VALID_DTYPES, Settings

DEFAULT_QUERY_PROMPT = "Instruct: Given a question, retrieve relevant passages that answer the question"

def select_device(model_hint: str, settings: Settings) -> str:
    return os.getenv(f"RAG_DEVICE_{model_hint.upper()}", settings.device)

def select_dtype(model_hint: str = "embed") -> str | None:
    raw = os.getenv(f"RAG_DTYPE_{model_hint.upper()}")
    if raw:
        if raw not in VALID_DTYPES:
            raise ValueError(f"RAG_DTYPE_{model_hint.upper()} must be one of {VALID_DTYPES}, got {raw!r}")
        return raw
    if not torch.cuda.is_available():
        return "float32"
    return "float32" if model_hint == "embed" else "float16"


class Retriever:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.col = chromadb.PersistentClient(
            path=settings.chroma_dir).get_collection(settings.collection)
        self.query_prompt = load_text(settings.query_prompt_path, DEFAULT_QUERY_PROMPT)
        self.model = SentenceTransformer(
            settings.embed_model, device=select_device("embed", settings),
            model_kwargs={"dtype": select_dtype("embed")})

    def search(self, query_internal: str, k: int | None = None) -> list[dict]:
        k = k or self.settings.retrieve_k
        qv = self.model.encode([query_internal], prompt=self.query_prompt, normalize_embeddings=True).tolist()
        res = self.col.query(query_embeddings=qv, n_results=k)
        return [
            {"id": res["ids"][0][i], "text": res["documents"][0][i],
             "meta": res["metadatas"][0][i], "dist": res["distances"][0][i]}
            for i in range(len(res["ids"][0]))
        ]