#!/usr/bin/env python3
"""Вшивает шрифты в HTML, делая страницу самодостаточной.

    embed.py <исходник.html> <результат.html>

Находит в вёрстке ссылки вида url("fonts/X.woff2") и заменяет их на
data-URI с содержимым файла. После этого страницу можно переслать одним
файлом или опубликовать: шрифты не отвалятся ни без папки рядом, ни без
доступа к сети.
"""

import base64
import re
import sys
from pathlib import Path


def embed(src, dst):
    src, dst = Path(src), Path(dst)
    html = src.read_text(encoding="utf-8")
    cache = {}

    def replace(match):
        rel = match.group(1)
        if rel not in cache:
            path = src.parent / rel
            if not path.exists():
                sys.exit(f"Не найден шрифт: {path}")
            data = base64.b64encode(path.read_bytes()).decode("ascii")
            cache[rel] = f"data:font/woff2;base64,{data}"
        return f'url("{cache[rel]}")'

    html = re.sub(r'url\("([^"]+\.woff2)"\)', replace, html)
    dst.write_text(html, encoding="utf-8")

    grew = dst.stat().st_size - src.stat().st_size
    print(f"  вшито шрифтов: {len(cache)}")
    print(f"  {dst}  {dst.stat().st_size // 1024} КБ  (+{grew // 1024} КБ)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    embed(sys.argv[1], sys.argv[2])
