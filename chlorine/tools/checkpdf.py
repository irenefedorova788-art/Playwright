#!/usr/bin/env python3
"""Проверяет, что PDF действительно отрисовался.

    checkpdf.py <файл.pdf> [папка_для_картинок]

Отчёт по страницам: размер, объём текста и первые слова. С указанной
папкой дополнительно сохраняет страницы картинками для просмотра глазами.

Нужен потому, что headless-браузер молча отдаёт пустой или бесшрифтовой
PDF: файл создаётся, размер выглядит правдоподобно, а текста внутри нет.
Считать признаком исправности наличие строки /FontFile нельзя — шрифты
попадают в сжатые объекты, и поиск по сырым байтам даёт ложную тревогу.
"""

import sys
from pathlib import Path

import pypdfium2 as pdfium


def check(path, out_dir=None):
    pdf = pdfium.PdfDocument(path)
    size_kb = Path(path).stat().st_size // 1024
    print(f"{path}  {len(pdf)} стр.  {size_kb} КБ\n")

    empty = []
    for i, page in enumerate(pdf, 1):
        width, height = page.get_size()
        text = page.get_textpage().get_text_range().strip()
        head = " ".join(text.split())[:70]

        print(f"  стр. {i:>2}  {width:.0f}×{height:.0f}  {len(text):>5} симв.  {head}")
        if not text:
            empty.append(i)

        if out_dir:
            target = Path(out_dir)
            target.mkdir(parents=True, exist_ok=True)
            page.render(scale=1.5).to_pil().save(target / f"page-{i:02d}.png")

    print()
    if empty:
        print(f"  ПУСТЫЕ СТРАНИЦЫ: {empty} — вероятно, печать прошла до загрузки шрифтов.")
        print("  Добавьте --virtual-time-budget=20000 к вызову chrome.")
    else:
        print("  Текст есть на всех страницах.")

    if out_dir:
        print(f"  Картинки страниц: {out_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    check(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
