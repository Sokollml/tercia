# Landings Quartet — четыре лендинга, четыре стиля

<!--
  ┌───────────────────────────────────────────────────────────────┐
  │  МЕСТО ПОД GIF / ПРЕВЬЮ                                        │
  │  Запишите короткую прокрутку всех четырёх лендингов и          │
  │  положите файл рядом, например docs/preview.gif, затем         │
  │  раскомментируйте строку ниже.                                 │
  └───────────────────────────────────────────────────────────────┘
-->
<!-- ![Превью четырёх лендингов](docs/preview.gif) -->

> **Демо для портфолио.** Один проект на Vite + React + TypeScript, в котором живут четыре лендинга — и каждый выглядит так, будто его сделала отдельная студия со своим почерком: своя сетка, шрифты, палитра и ритм. Все тексты и цифры вымышлены, но реалистичны (никакого lorem ipsum). Не коммерческий продукт.

---

## Четыре стиля

| Маршрут | Тема | Стиль | Чем отличается |
| --- | --- | --- | --- |
| `/saas` | SaaS-аналитика (Meridian) | **Swiss / International Typographic** | Строгая модульная сетка, гротеск (Inter), палитра красный / чёрный / белый, данные поданы как инфографика — воронка, линейный график, метрики. |
| `/coffee` | Кофейня (Roast & Rest) | **Editorial** | Крупный serif (Playfair Display), много воздуха, кремовый фон и один тёплый терракотовый акцент, журнальная вёрстка с фотографиями (CC0). |
| `/app` | Мобильное приложение (Tempo) | **Tactile** | Тёмный премиум-интерфейс, глубина через мягкие тени и подсветку (без стеклянных карточек), CSS-мокап телефона с анимированным UI. |
| `/course` | Онлайн-курс (PROTOCOL) | **Maximalist** | Смелая крупная типографика, контрастные цветные блоки (лайм / розовый / электрик-синий), огромные цифры результатов с анимацией счёта, бегущая строка. |

Главная `/` — индекс со ссылками на все четыре лендинга.

Каждый лендинг изолирован в своей папке `src/landings/<имя>/`: компонент, локальный `content.ts` с текстами RU + EN и, где нужно, свои вспомогательные компоненты. Общие вещи (переключатель языка, SEO-теги, иконки, анимация появления) лежат в `src/components/`.

## Особенности

- **Два языка RU / EN** с переключателем в шапке каждого лендинга; выбор запоминается в `localStorage`, начальный язык берётся из языка браузера.
- **SEO на каждый маршрут** — свои `title`, `description`, Open Graph и Twitter-теги (через `react-helmet-async`), реагируют на язык.
- **Иконки — только inline SVG** (`src/components/icons.tsx`), без эмодзи и иконочных шрифтов.
- **Адаптив от 375px**, плавные анимации появления на скролле (`framer-motion`), уважается `prefers-reduced-motion`.
- **Готово к деплою на Vercel** — SPA-rewrite в `vercel.json`, чтобы прямые ссылки на `/saas`, `/coffee`, `/app`, `/course` работали.

## Стек

Vite · React 18 · TypeScript · Tailwind CSS · React Router · Framer Motion · react-helmet-async.

Шрифты подключаются через Google Fonts в `index.html`: Inter, Playfair Display, JetBrains Mono.

## Запуск

```bash
npm install
npm run dev
```

Откроется на `http://localhost:5173`. Маршруты:

- `/` — индекс
- `/saas` — Swiss
- `/coffee` — Editorial
- `/app` — Tactile
- `/course` — Maximalist

## Сборка и проверки

```bash
npm run build      # tsc -b + vite build → dist/
npm run preview    # локальный предпросмотр собранной версии
npm run typecheck  # проверка типов без сборки (tsc --noEmit)
```

## Деплой на Vercel

1. Залейте репозиторий на GitHub и импортируйте его в [Vercel](https://vercel.com/new).
2. Vercel сам определит Vite. Настройки по умолчанию:
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
3. Файл `vercel.json` уже содержит SPA-rewrite — все маршруты будут отдавать `index.html`, поэтому прямые ссылки на лендинги работают.

Либо через CLI:

```bash
npm i -g vercel
vercel        # превью-деплой
vercel --prod # прод
```

## Структура

```
src/
  components/        общие: LangToggle, Seo, Reveal, ScrollToTop, icons
  i18n/              контекст языка (RU / EN)
  pages/             IndexPage, NotFound
  landings/
    saas/            Swiss     — SaasLanding + content
    coffee/          Editorial — CoffeeLanding + content
    app/             Tactile   — AppLanding + PhoneMockup + content
    course/          Maximalist— CourseLanding + CountUp + content
  main.tsx           роутинг
```

---

*Демо-сайт для портфолио. Названия компаний, цифры и отзывы вымышлены; фотографии в «Кофейне» — стоковые под лицензией CC0, остальные изображения — градиентные заглушки.*
