# Баннеры услуг для фриланс-площадок

Стиль сайта: фон `#0A0A0F`, акцент `#D3FB52`, фиолетовое свечение `#7C3AED`,
шрифты Space Grotesk + Manrope + JetBrains Mono.

Композиция минимальная: логотип, короткий заголовок, одна строка пояснения,
строка со стеком внизу. Без скриншотов работ, цифр и отзывов.

## Готовые файлы

`kwork/` — шесть баннеров 1320×880. Kwork сжимает обложку до 600×400,
поэтому заголовки крупные. PNG, около 0.6 МБ при лимите площадки 4 МБ.

| Файл | Услуга |
|---|---|
| 01-site | Сайт и лендинг под ключ |
| 02-bot | Telegram-бот под ключ |
| 03-miniapp | Mini-app в Telegram |
| 04-automation | Автоматизация на n8n |
| 05-ai | ИИ-поддержка по базе знаний |
| 06-landings | Лендинг в вашем стиле |

## Как пересобрать

```
cd исходники
python3 gen.py services-ru.json kwork        # пресеты: kwork, fiverr, square, wide
"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" --headless=new \
  --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --virtual-time-budget=5000 --window-size=1320,880 \
  --screenshot=02-bot.png "file://$PWD/02-bot--kwork.html"
```

Тексты — в `services-ru.json`: `h1` (можно `<br>` и `<em>` для акцента),
`sub` — одна строка, `foot` — стек внизу.

Размеры площадок: Kwork 1320×880 (минимум 640×440, до 4 МБ),
Fiverr 1280×769 (5:3, до 5 МБ, важный текст не ближе 70 px к краям).
