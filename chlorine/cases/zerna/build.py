"""Собирает deck.html из deck.src.html: вставляет логотип и паттерны."""
import re
from pathlib import Path
here = Path(__file__).parent
src = (here / "deck.src.html").read_text()
logo = (here / "logo.svg").read_text().strip()
inner = logo.replace("<svg ", '<svg width="100%" height="100%" ', 1)

# Паттерн внутри <pattern> не наследует цвет от места применения,
# поэтому на каждый фон — свой вариант с явными цветами.
variants = {
    "grains": ("#2F4DE4", "#2340D9"),       # на кобальте, тон в тон
    "grains-cream": ("#FFF3DC", "#2340D9"), # сливочные зёрна на кобальте
    "grains-ink": ("#1E2A6E", "#10184A"),
    "grains-dark": ("#3A4AA0", "#2B3768"),
}
pats = ""
for pid, (fill, slit) in variants.items():
    pats += (f'<pattern id="{pid}" width="220" height="220" patternUnits="userSpaceOnUse">'
             f'<use href="#bean" x="20" y="18" width="70" height="86" fill="{fill}" style="--slit:{slit}" transform="rotate(-25 55 61)"/>'
             f'<use href="#bean" x="130" y="128" width="70" height="86" fill="{fill}" style="--slit:{slit}" transform="rotate(25 165 171)"/></pattern>')
src = re.sub(r'<pattern id="grains".*?</pattern>', pats, src, flags=re.S)

# на слайде паттерна зёрна сливочные; на фартуке и фасаде — свои тона
src = src.replace('style="color:var(--cream);opacity:.95"><rect width="100%" height="100%" fill="url(#grains)"',
                  'style="opacity:.95"><rect width="100%" height="100%" fill="url(#grains-cream)"')
src = src.replace('fill="url(#grains)"/></g>\n      <rect x="100"', 'fill="url(#grains-ink)"/></g>\n      <rect x="100"')
src = src.replace('fill="url(#grains)" opacity=".6"', 'fill="url(#grains-dark)" opacity=".6"')
src = src.replace("{{LOGO_INNER}}", inner).replace("{{LOGO}}", logo)
(here / "deck.html").write_text(src)
print("deck.html", len(src) // 1024, "КБ")
