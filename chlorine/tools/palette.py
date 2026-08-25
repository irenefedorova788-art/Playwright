#!/usr/bin/env python3
"""Снимает точные цвета с референсных скриншотов.

    palette.py colors <image> [N]      — N доминирующих цветов с долей площади
    palette.py pick <image> <x> <y>    — точный цвет пикселя
    palette.py grid <image> [N]        — сетка N×N проб по всему кадру

Нужен, чтобы цвета брендбука брались замером, а не на глаз.
"""

import sys
from collections import Counter

from PIL import Image


def _hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb[:3])


def _load(path):
    img = Image.open(path).convert("RGB")
    # Скриншоты бывают огромные — для подсчёта частот хватает уменьшенной копии.
    if max(img.size) > 1200:
        img.thumbnail((1200, 1200), Image.LANCZOS)
    return img


def colors(path, count=8):
    img = _load(path)
    # Квантование сводит близкие оттенки JPEG-сжатия в один цвет.
    quantized = img.quantize(colors=count, method=Image.MEDIANCUT).convert("RGB")
    total = quantized.width * quantized.height
    ranked = Counter(quantized.getpixel((x, y))
                     for y in range(quantized.height)
                     for x in range(quantized.width)).most_common(count)

    print(f"{path}  ({img.width}×{img.height})\n")
    for rgb, n in ranked:
        share = n / total * 100
        bar = "█" * max(1, round(share / 2))
        print(f"  {_hex(rgb):<9} {share:5.1f}%  {bar}")


def pick(path, x, y):
    img = Image.open(path).convert("RGB")
    if not (0 <= x < img.width and 0 <= y < img.height):
        sys.exit(f"Точка {x},{y} вне кадра {img.width}×{img.height}")
    print(f"{_hex(img.getpixel((x, y)))}  в точке {x},{y}")


def grid(path, n=5):
    img = Image.open(path).convert("RGB")
    print(f"{path}  ({img.width}×{img.height})\n")
    for row in range(n):
        y = round(img.height * (row + 0.5) / n)
        cells = []
        for col in range(n):
            x = round(img.width * (col + 0.5) / n)
            cells.append(_hex(img.getpixel((x, y))))
        print("  " + "  ".join(cells))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)

    command, path = sys.argv[1], sys.argv[2]
    rest = sys.argv[3:]

    if command == "colors":
        colors(path, int(rest[0]) if rest else 8)
    elif command == "pick":
        if len(rest) < 2:
            sys.exit("pick требует координаты: pick <image> <x> <y>")
        pick(path, int(rest[0]), int(rest[1]))
    elif command == "grid":
        grid(path, int(rest[0]) if rest else 5)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
