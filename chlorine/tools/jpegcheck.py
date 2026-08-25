#!/usr/bin/env python3
"""Оценивает, насколько сжатие испортило цвет на референсе.

    jpegcheck.py <image> <x> <y> [размер_пробы]

Берёт квадратную пробу вокруг точки и считает разброс канала. На чистом
плоском цвете разброс близок к нулю, и hex можно брать как есть. Большой
разброс означает, что сжатие размазало цвет и точное значение потеряно.
"""

import sys

from PIL import Image


def check(path, x, y, size=12):
    img = Image.open(path).convert("RGB")
    half = size // 2
    pixels = [
        img.getpixel((px, py))
        for py in range(max(0, y - half), min(img.height, y + half))
        for px in range(max(0, x - half), min(img.width, x + half))
    ]

    channels = list(zip(*pixels))
    means = [sum(c) / len(c) for c in channels]
    spreads = [max(c) - min(c) for c in channels]
    worst = max(spreads)

    mean_hex = "#{:02X}{:02X}{:02X}".format(*(round(m) for m in means))

    if worst <= 4:
        verdict = "чисто — hex можно брать как есть"
    elif worst <= 12:
        verdict = "лёгкий шум — среднее по пробе надёжно"
    else:
        verdict = "сильное искажение — точное значение потеряно"

    print(f"  проба {size}×{size} в {x},{y}")
    print(f"  средний цвет   {mean_hex}")
    print(f"  разброс R/G/B  {spreads[0]} / {spreads[1]} / {spreads[2]}")
    print(f"  вывод          {verdict}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    check(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]),
          int(sys.argv[4]) if len(sys.argv) > 4 else 12)
