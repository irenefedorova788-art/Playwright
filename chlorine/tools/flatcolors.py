#!/usr/bin/env python3
"""Находит на референсе участки ровного цвета и снимает с них точный hex.

    flatcolors.py <image> [сколько_цветов]

Сканирует кадр пробами, отбрасывает всё зашумлённое и градиентное,
оставляет только заливки. Именно они несут фирменные цвета: фотофон
и текстуры для палитры бесполезны. Координаты в выводе — чтобы можно
было перепроверить точку глазами.
"""

import sys
from collections import defaultdict

from PIL import Image

PATCH = 14           # сторона пробы
STEP = 10            # шаг сканирования
FLAT = 6             # максимальный разброс канала внутри пробы
MERGE = 10           # ближе этого расстояния цвета считаем одним


def _scan(img):
    """Возвращает средние цвета всех достаточно ровных проб."""
    found = []
    for y in range(0, img.height - PATCH, STEP):
        for x in range(0, img.width - PATCH, STEP):
            pixels = [
                img.getpixel((px, py))
                for py in range(y, y + PATCH, 3)
                for px in range(x, x + PATCH, 3)
            ]
            channels = list(zip(*pixels))
            if max(max(c) - min(c) for c in channels) > FLAT:
                continue
            mean = tuple(round(sum(c) / len(c)) for c in channels)
            found.append((mean, x + PATCH // 2, y + PATCH // 2))
    return found


def _cluster(found):
    """Сводит близкие оттенки в один цвет, чтобы не плодить дубли."""
    clusters = defaultdict(list)
    for color, x, y in found:
        for key in clusters:
            if sum(abs(a - b) for a, b in zip(color, key)) <= MERGE:
                clusters[key].append((color, x, y))
                break
        else:
            clusters[color].append((color, x, y))
    return clusters


def main(path, limit=8):
    img = Image.open(path).convert("RGB")
    found = _scan(img)

    if not found:
        print("Ровных участков нет — кадр целиком зашумлён или в градиентах.")
        return

    clusters = _cluster(found)
    ranked = sorted(clusters.items(), key=lambda kv: len(kv[1]), reverse=True)
    total = len(found)

    print(f"{path}  ({img.width}×{img.height})")
    print(f"ровных проб: {total} из {(img.width // STEP) * (img.height // STEP)}\n")

    for key, members in ranked[:limit]:
        channels = list(zip(*(m[0] for m in members)))
        mean = tuple(round(sum(c) / len(c)) for c in channels)
        hex_value = "#{:02X}{:02X}{:02X}".format(*mean)
        share = len(members) / total * 100
        _, x, y = members[len(members) // 2]
        print(f"  {hex_value}   {share:5.1f}% ровной площади   проба в {x},{y}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8)
