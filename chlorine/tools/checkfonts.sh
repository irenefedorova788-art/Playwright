#!/usr/bin/env bash
# Проверяет по ответу Google Fonts, есть ли у гарнитуры кириллица.
# Google отдаёт @font-face отдельным блоком на каждый набор символов,
# поэтому наличие блока cyrillic — факт, а не предположение.
#
#   ./checkfonts.sh "Anton" "Oswald" "Archivo Black"

UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'

for family in "$@"; do
  url="https://fonts.googleapis.com/css2?family=${family// /+}:wght@400..900&display=swap"
  css=$(curl -sS --max-time 20 -A "$UA" "$url")

  # Без диапазона весов гарнитура может не отдаться — пробуем простой запрос.
  if [ -z "$css" ] || echo "$css" | grep -qi "error"; then
    css=$(curl -sS --max-time 20 -A "$UA" \
      "https://fonts.googleapis.com/css2?family=${family// /+}&display=swap")
  fi

  if [ -z "$css" ]; then
    printf '  %-22s недоступна\n' "$family"
    continue
  fi

  if echo "$css" | grep -q 'cyrillic'; then
    weights=$(echo "$css" | grep -o 'font-weight: [0-9 ]*' | head -1 | sed 's/font-weight: //')
    printf '  %-22s кириллица есть    веса: %s\n' "$family" "${weights:-400}"
  else
    printf '  %-22s КИРИЛЛИЦЫ НЕТ\n' "$family"
  fi
done
