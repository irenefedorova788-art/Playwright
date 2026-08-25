#!/usr/bin/env python3
"""Скачивает кириллические начертания гарнитур с Google Fonts.

    getfonts.py <папка> "Oswald:400..700" "Unbounded:400..900" ...

Google отдаёт отдельный файл на каждый набор символов. Нужен тот, что
идёт за комментарием cyrillic — латинский нам бесполезен, в нём нет
русских букв. Файлы кладутся локально, чтобы вёрстка рендерилась без сети.
"""

import re
import subprocess
import sys
from pathlib import Path

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")


def fetch(url):
    result = subprocess.run(
        ["curl", "-sS", "--max-time", "30", "-A", UA, url],
        capture_output=True, text=True,
    )
    return result.stdout


def subset_source(css, subset):
    """Возвращает ссылку на woff2 из блока нужного набора символов."""
    # Блоки идут как: /* cyrillic */ @font-face { ... url(...) ... }
    for match in re.finditer(rf"/\*\s*{subset}\s*\*/(.*?)\}}", css, re.S):
        url = re.search(r"url\((https://[^)]+)\)", match.group(1))
        if url:
            return url.group(1)
    return None


def main(out_dir, specs):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    for spec in specs:
        family, _, weights = spec.partition(":")
        query = family.replace(" ", "+")
        if weights:
            query += f":wght@{weights}"

        css = fetch(f"https://fonts.googleapis.com/css2?family={query}&display=swap")
        stem = family.replace(" ", "")
        saved = []

        # Латиница нужна не меньше кириллицы: в текстах встречаются
        # названия брендов и гарнитур, иначе они выпадут в запасной шрифт.
        for subset in ("cyrillic", "latin"):
            source = subset_source(css, subset)
            if not source:
                continue
            target = out / f"{stem}-{subset}.woff2"
            subprocess.run(["curl", "-sS", "--max-time", "30", "-A", UA,
                            "-o", str(target), source], check=True)
            saved.append(f"{subset} {target.stat().st_size // 1024} КБ")

        print(f"  {family:<20} {', '.join(saved) if saved else 'не найдена'}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
