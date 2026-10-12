import os
import time
import re

from .config import SETTINGS, Settings, load_few_shot, load_text
from .lang_translation import looks_russian
from .llm import LocalLLM
from .retriever import Retriever, select_dtype
from .translator import to_fiction, to_real

DONT_KNOW = "Я не знаю"

SYSTEM_PROMPT_FALLBACK = """You are an assistant of a corporate knowledge base.
Rules:
1. Answer ONLY using the information from the provided context.
2. If the context does not contain the answer, reply exactly: "Я не знаю".
3. First write 1-2 sentences of reasoning: which fragment the answer is based on. Then give the final answer after "Answer:".
Answer in the language of the user's question."""

FEW_SHOT_FALLBACK = [
    ("Who built the Kestrels?",
     "Reasoning: the first fragment says Kestrels are devices built by the Xanvoss.\n"
     "Answer: The Kestrels were built by the Xanvoss."),
    ("How does the Torlynn work?",
     "Reasoning: the fragment describes the Torlynn as orange crystals that extract "
     "zero-point energy from subspace.\n"
     "Answer: The Torlynn is a crystal module that extracts zero-point energy "
     "from subspace and outputs it as electrical power."),
]

def _extract_answer_block(raw: str) -> str:
    parts = re.split(r"(?:Reasoning|Рассуждение):", raw, maxsplit=2)
    text = ("Reasoning:" + parts[1]) if len(parts) >= 2 else raw.strip()

    for cut in ("Я не знаю", "Plain text only", "To:", "To continue", "following the given structure",
                "Sources:", "Assistant:", "Reasoning:", "Рассуждение:"):
        idx = text.find(cut)
        if idx > 0:
            text = text[:idx]
    return text.strip()

def _format_answer_block(text: str) -> str:
    m = re.match(r"\s*Reasoning:\s*(.*?)\s*(?:Answer|Ответ):\s*(.*?)\s*$", text, re.S)
    if not m:
        return text.strip()
    return f"Reasoning:\n{m.group(1).strip()}\n\nAnswer:\n{m.group(2).strip()}"

def _translate_answer_block(translator, text: str) -> str:
    m = re.match(r"\s*Reasoning:\s*(.*?)\s*(?:Answer|Ответ):\s*(.*?)\s*$", text, re.S)
    if not m:
        return translator.to_ru(text)
    reasoning = translator.to_ru(m.group(1).strip())
    ans = translator.to_ru(m.group(2).strip())
    return f"Рассуждение:\n{reasoning}\n\nОтвет:\n{ans}"

def _answer_is_empty(text: str) -> bool:
    m = re.search(r"(?:Answer|Ответ):\s*(.*)$", text, re.S)
    return (not m) or (not m.group(1).strip())

class RagPipeline:
    def __init__(self, settings: Settings = SETTINGS):
        self.settings = settings
        self.translator = None
        self.retriever = Retriever(settings)
        self.llm = LocalLLM(settings.llm_model, device=settings.device, dtype=select_dtype("llm"))
        self.stop_strings = settings.stop_strings
        self.few_shot = load_few_shot(settings.few_shot_path, FEW_SHOT_FALLBACK)

        self.role = load_text(settings.role_path, "")
        self.behavior = load_text(settings.behavior_path, "")
        loaded = load_few_shot(settings.few_shot_path, FEW_SHOT_FALLBACK)
        self.few_shot = [(to_fiction(q), to_fiction(a)) for q, a in loaded]

        self.system_prompt = load_text(settings.system_prompt_path, SYSTEM_PROMPT_FALLBACK)

    def answer(self, question: str, use_term_translation: bool = True, use_lang_translation: bool = True) -> dict:
        t0 = time.perf_counter()
        stages = {}

        answer_lang = ""
        if use_lang_translation and self.settings.translation_enabled and looks_russian(question):
            if self.translator is None:
                from .lang_translation import RuEnTranslator
                self.translator = RuEnTranslator(self.llm)
            question = self.translator.to_en(question)
            answer_lang = "Russian"
            stages["lang_translation"] = time.perf_counter() - t0

        t = time.perf_counter()
        def get_elapsed():
            return time.perf_counter() - t

        q_internal = to_fiction(question) if use_term_translation else question
        stages["term_translation"] = get_elapsed()

        t = time.perf_counter()
        chunks = self.retriever.search(q_internal)
        stages["retrieval"] = get_elapsed()

        seen_titles, sources = set(), []
        for c in chunks:
            title = to_real(c["meta"]["title"]) if use_term_translation else c["meta"]["title"]
            if title in seen_titles:
                continue
            seen_titles.add(title)
            sources.append({"title": title, "source": c["meta"]["source"],
                            "chunk_id": c["meta"]["chunk_id"], "dist": round(c["dist"], 4)})

        result = {"translation": use_term_translation, "question": question, "internal_query": q_internal, "dist_top1": round(chunks[0]["dist"], 4),
                  "sources": sources, "stages": {k: round(v, 2) for k, v in stages.items()}}

        if chunks[0]["dist"] > self.settings.dist_threshold:
            result.update(answer=DONT_KNOW, internal_answer=DONT_KNOW, sources=[])
            return result

        examples = "\n\n".join(f"Q: {q}\nA: {a}" for q, a in self.few_shot)
        context = "\n\n".join(f"[{i + 1}] {c['text']}" for i, c in enumerate(chunks[: self.settings.context_chunks]))
        # user_block = f"Question: {q_internal}"
        # if answer_lang:
        #     user_block += f"\nRespond in {answer_lang}. Keep entity names exactly as written in CONTEXT (English), do not translate them."

        prompt_text = self.system_prompt.format(role=self.role, behavior=self.behavior, examples=examples, context=context, question=q_internal)

        t = time.perf_counter()
        if "{context}" in prompt_text or "{question}" in prompt_text:
            raise RuntimeError("prompt template not rendered: check system_prompt file has {placeholders}")

        if os.getenv("RAG_DEBUG_PROMPT", "false").lower() == "true":
            print(f"----- PROMPT -----\n{prompt_text}\n------------------")

        raw = self.llm.complete(prompt_text, max_new_tokens=self.settings.max_new_tokens,
                                temperature=self.settings.temperature, top_p=self.settings.top_p, stop_strings=self.stop_strings)
        stages["llm"] = get_elapsed()

        t = time.perf_counter()
        answer = _extract_answer_block(to_real(raw) if use_term_translation else raw)
        answer = _format_answer_block(answer)
        if answer_lang:
            answer = _translate_answer_block(self.translator, answer)

        if _answer_is_empty(answer):
            result.update(answer=DONT_KNOW, internal_answer=raw, sources=[])
            result["stages"]["total"] = round(time.perf_counter() - t0, 2)
            return result

        stages["postprocess"] = get_elapsed()
        result.update(answer=answer, internal_answer=raw)
        result["stages"]["total"] = round(time.perf_counter() - t0, 2)
        return result