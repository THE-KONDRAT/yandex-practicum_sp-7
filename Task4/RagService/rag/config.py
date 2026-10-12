import json
import os
from dataclasses import dataclass, field
from pathlib import Path

RAG_SERVICE_DIR = Path(__file__).resolve().parent.parent

def _resolve(path: str) -> Path:
    p = Path(path)
    return p if p.exists() else RAG_SERVICE_DIR / p

def _bool_env(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes")


def load_text(path: str, fallback: str) -> str:
    p = _resolve(path)
    return p.read_text(encoding="utf-8") if p.exists() else fallback


def load_few_shot(path: str, fallback: list) -> list:
    p = _resolve(path)
    if not p.exists():
        return fallback
    data = json.loads(p.read_text(encoding="utf-8"))
    return [(item["q"], item["a"]) for item in data]


VALID_DTYPES = {"float32", "float16", "bfloat16"}
VALID_TTS = ("none", "piper", "silero")


@dataclass
class Settings:
    # retrieval
    chroma_dir: str = os.getenv("RAG_CHROMA_DIR", "index/chroma_db")
    collection: str = os.getenv("RAG_COLLECTION", "knowledge_base")
    embed_model: str = os.getenv("RAG_EMBED_MODEL", "Qwen/Qwen3-Embedding-0.6B")
    query_prompt_path: str = os.getenv("RAG_QUERY_PROMPT", "prompts/query.txt")
    device: str = os.getenv("RAG_DEVICE", "cuda")
    retrieve_k: int = int(os.getenv("RAG_RETRIEVE_K", "5"))
    context_chunks: int = int(os.getenv("RAG_CONTEXT_CHUNKS", "3"))
    dist_threshold: float = float(os.getenv("RAG_DIST_THRESHOLD", "0.45"))

    # llm
    llm_model: str = os.getenv("RAG_LLM_MODEL", "Qwen/Qwen2.5-3B-Instruct")
    max_new_tokens: int = int(os.getenv("RAG_MAX_NEW_TOKENS", "400"))
    temperature: float = float(os.getenv("RAG_TEMPERATURE", "0.3"))
    top_p: float = float(os.getenv("RAG_TOP_P", "0.9"))
    stop_strings: tuple = ("[User]", "[CONTEXT]", "[Examples]", "[System]", "\nQ:", "[Known Bugs]", "To elaborate", "To summarize", "Let me know")

    # prompts
    system_prompt_path: str = os.getenv("RAG_SYSTEM_PROMPT", "prompts/system.txt")
    few_shot_path: str = os.getenv("RAG_FEW_SHOT", "prompts/few_shot.json")
    role_path: str = os.getenv("RAG_ROLE", "prompts/role.txt")
    behavior_path: str = os.getenv("RAG_BEHAVIOR", "prompts/behavior.txt")

    # translation (optional)
    translation_enabled: bool = _bool_env("RAG_TRANSLATION_ENABLE", False)

    # voice (optional)
    tts_engine: str = os.getenv("RAG_TTS", "none")

    def __post_init__(self):
        raw = os.getenv("RAG_STOP_STRINGS")
        if raw:
            parsed = json.loads(raw)
            if not isinstance(parsed, list) or not all(isinstance(s, str) for s in parsed):
                raise ValueError("RAG_STOP_STRINGS must be a JSON array of strings")
            self.stop_strings = tuple(parsed)

    def validate(self) -> None:
        if self.tts_engine not in VALID_TTS:
            raise ValueError(f"RAG_TTS must be one of {VALID_TTS}, got {self.tts_engine!r}")
        if self.retrieve_k < 1 or self.context_chunks < 1:
            raise ValueError("retrieve_k and context_chunks must be >= 1")
        if not self.stop_strings:
            raise ValueError("stop_strings must be non-empty")


SETTINGS = Settings()
SETTINGS.validate()