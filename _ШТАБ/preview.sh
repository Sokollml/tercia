#!/bin/bash
# Готовит локальный предпросмотр сайта, редизайнов и соцсетей.
#
#   bash _ШТАБ/preview.sh
#
# Зачем копии: сервер предпросмотра в Claude Code не имеет доступа к внешнему
# диску (/Volumes), поэтому файлы зеркалятся в ~/tercia-preview на диск Mac.
# После правок запусти скрипт снова — копии обновятся.
set -e
SRC="/Volumes/Z Slim/tercia"
DST="$HOME/tercia-preview"
EX=(--exclude '._*' --exclude '.DS_Store')

mkdir -p "$DST"/{redesign,site,social}
rsync -a --delete "${EX[@]}" "$SRC/redesign/" "$DST/redesign/"
rsync -a --delete "${EX[@]}" "$SRC/index.html" "$SRC/styles.css" "$SRC/script.js" "$SRC/assets" "$DST/site/"
rsync -a --delete "${EX[@]}" "$SRC/_ШТАБ/соцсети/" "$DST/social/"
cp "$DST/social/редактор.html" "$DST/social/editor.html"   # латинское имя для адресной строки

# боевой сайт — рабочая копия публичного репозитория
if [ -d "$DST/landing/.git" ]; then
  git -C "$DST/landing" pull -q --ff-only || echo "landing: подтяни изменения вручную"
else
  ~/.local/bin/gh repo clone sokolclimb/tercia-landing "$DST/landing" >/dev/null
fi

cat <<TXT
Готово. Запусти нужный сервер командой preview_start (имя из .claude/launch.json):
  redesign → http://localhost:8707   направления 01–08
  site     → http://localhost:8708   прежний лендинг (index.html в корне)
  landing  → http://localhost:8709   то, что сейчас на tercia.dev, плюс /portfolio
  social   → http://localhost:8710/editor.html   редактор постов
TXT
