import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

GLOSSARY_HINT = ("Use the established English names for in-universe entities, single word where applicable: "
    "'Звёздные врата' -> 'Stargates', 'Звездные врата' -> 'Stargates'. Do not split such names into separate words.")

GLOSSARY_HINT_REVERSE = ("Use the established Russian names for in-universe entities, single word where applicable: "
    "'Stargates' -> 'Звёздные врата', 'ZPM' -> 'МНТ' ('Zero Point Module' -> 'Модуль Нулевой Точки').")

def looks_russian(text: str) -> bool:
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return False
    return sum("а" <= ch.lower() <= "я" or ch.lower() == "ё" for ch in letters) / len(letters) > 0.3


class RuEnTranslator:
    def __init__(self, llm):
        self.llm = llm

    def to_en(self, text: str) -> str:
        messages = [{"role": "user",
            "content": f"Translate the following text from Russian to English. Output only the translation, no explanations. {GLOSSARY_HINT}\n\n{text}"}]
        return self.llm.chat(messages, max_new_tokens=256, temperature=0.0).strip()

    def to_ru(self, text: str) -> str:
        messages = [{"role": "user",
            # "content": (f"Translate the following text from English to Russian. Output only the translation, no explanations:\n\n{text}")}]
            "content": (f"Translate the following text from English to Russian. {GLOSSARY_HINT_REVERSE} Output only the translation, no explanations:\n\n" + text)}]
        return self.llm.chat(messages, max_new_tokens=512, temperature=0.1).strip()