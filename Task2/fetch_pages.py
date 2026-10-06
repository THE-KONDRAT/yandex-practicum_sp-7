# Загрузка и очистка исходных данных базы знаний (страницы Stargate Wiki).
import json
import re
import time
from pathlib import Path

import requests

API = "https://stargate.fandom.com/api.php"
HEADERS = {"User-Agent": "RAG-project-bot/1.0 (educational)"}
OUT_DIR = Path("raw_pages")
OUT_DIR.mkdir(exist_ok=True)

# Ключевые страницы: общее, кино (1994), SG-1, Atlantis, Universe
PAGES = [
    # --- Общее / кино ---
    "Stargate (movie)", "Stargate", "Earth",
    # --- SG-1: персонажи ---
    "Jack O'Neill", "Daniel Jackson", "Samantha Carter", "Teal'c",
    "George Hammond", "Janet Fraiser", "Apophis",
    # --- SG-1: расы и фракции ---
    "Goa'uld", "Jaffa", "Tok'ra", "Asgard", "Ancients",
    "Replicators", "Ori", "Nox", "Tollan", "SG-1",
    # --- SG-1: технологии и локации ---
    "Stargate Command", "Dial Home Device", "Puddle Jumper", "Milky Way",
    # --- Atlantis ---
    "John Sheppard", "Rodney McKay", "Teyla Emmagan", "Ronon Dex", "Elizabeth Weir",
    "Wraith", "Atlantis", "Lantean", "Zero Point Module", "Pegasus",
    # --- Universe ---
    "Nicholas Rush", "Everett Young", "Eli Wallace", "Destiny", "Lucian Alliance",
]

# Секции, начиная с которых текст обрезается до конца страницы
TRUNCATE_AT = re.compile(
    r"^\s*=+\s*(Appearances|Behind the scenes|References|Links and navigation|"
    r"Notes|See also)\s*=+\s*$",
    re.M,
)


def fetch_wikitext(title: str) -> str | None:
    # Получить исходный wikitext страницы через action=parse.
    params = {
        "action": "parse",
        "page": title,
        "prop": "wikitext",
        "redirects": 1,
        "format": "json",
    }
    r = requests.get(API, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        print(f"  !! ошибка API для '{title}': {data['error'].get('info')}")
        return None
    return data["parse"]["wikitext"]["*"]


def drop_service_sections(text: str) -> str:
    m = TRUNCATE_AT.search(text)
    return text[: m.start()] if m else text


def remove_links(text: str) -> str:
    prev = None
    while prev != text:
        prev = text
        text = re.sub(
            r"\[\[([^\[\]]*)\]\]",
            lambda m: m.group(1).split("|")[-1],
            text,
        )
    # остатки незакрытых ссылок
    return re.sub(r"\[\[|\]\]", " ", text)


def clean_wikitext(text: str) -> str:
    # Превратить wikitext в чистый plain text.
    text = drop_service_sections(text)

    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"\{\{[^{}]*\}\}", " ", text)

    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)

    # внешние ссылки
    text = re.sub(r"\[https?://[^\s\]]+\s+([^\]]*)\]", r"\1", text)
    text = re.sub(r"\[https?://[^\s\]]+\]", " ", text)

    # жирный/курсив
    text = re.sub(r"'{2,5}", "", text)

    # ставшиеся ссылки
    text = remove_links(text)


    text = re.sub(r"^={2,6}\s*(.*?)\s*={2,6}$", r"\n\1\n", text, flags=re.M)

    # остатки HTML-тегов
    text = re.sub(r"<[^>]+>", " ", text)

    lines_out = []
    for line in text.splitlines():
        s = line.strip()
        if re.match(r"^(thumb\||\||!|\}|\{)", s):
            continue
        if 'class="' in s or "mw-collapsible" in s:
            continue
        if re.match(r"^[a-z]{2,3}:[^\s].*$", s):
            continue
        if re.match(r"^(\*\s*)?Category:", s):
            continue
        lines_out.append(re.sub(r"^:\s*", "", line))

    text = "\n".join(lines_out)

    text = re.sub(r"\s*:?\s*To be added\.?", "", text)
    text = re.sub(r"\([^)]*Weblog\)", "", text)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")


def main():
    manifest = {}
    for title in PAGES:
        wikitext = fetch_wikitext(title)
        if not wikitext:
            continue
        text = clean_wikitext(wikitext)
        if len(text) < 200:
            print(f"  -- пропуск (после очистки документ короче 200 символов): {title}")
            continue
        fname = f"{slugify(title)}.txt"
        (OUT_DIR / fname).write_text(text, encoding="utf-8")
        manifest[title] = fname
        print(f"  ok: {title} -> {fname} ({len(text)} символов)")
        time.sleep(1)

    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nСбор завершён. Загружено {len(manifest)} страниц в {OUT_DIR}/")


if __name__ == "__main__":
    main()