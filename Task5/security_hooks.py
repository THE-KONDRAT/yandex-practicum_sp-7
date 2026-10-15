import re

MALICIOUS_RE = re.compile(
    r"ignore all instructions|disregard previous|"
    r"пароль|password:|root:\s*\S+|system prompt|"
    r"pin code|pin:|пин-код|card number|\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b|"
    r"system info leak|gpu model|cuda version|vram|"
    r"running processes|environment variables|system compromised",
    re.I)


def filter_chunks(chunks: list) -> list:
    return [c for c in chunks if not MALICIOUS_RE.search(c["text"])]


def check_answer(answer: str) -> bool:
    return not MALICIOUS_RE.search(answer)