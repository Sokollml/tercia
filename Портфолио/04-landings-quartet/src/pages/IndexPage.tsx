import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Seo from '../components/Seo'
import LangToggle from '../components/LangToggle'
import Reveal from '../components/Reveal'
import { useLang } from '../i18n/LanguageContext'
import { ArrowUpRight, ChartBar, Cup, Phone, Bolt } from '../components/icons'

const copy = {
  ru: {
    kicker: 'Портфолио · Квартет лендингов',
    title: 'Четыре лендинга.',
    titleAccent: 'Четыре студии.',
    lead: 'Один проект на Vite + React + TypeScript, но каждый лендинг выглядит так, будто его сделала отдельная команда с собственным почерком. Разные сетки, шрифты, цвет и ритм.',
    demoNote: 'Демо-сайт для портфолио. Тексты вымышлены, но реалистичны.',
    open: 'Открыть лендинг',
    stackTitle: 'Как это устроено',
    stack: [
      ['01', 'Один Vite-проект', 'React Router разводит четыре лендинга по маршрутам. Общий контекст языка RU / EN.'],
      ['02', 'Изолированные стили', 'Палитра, типографика и сетка каждого лендинга живут в своей папке src/landings.'],
      ['03', 'Готово к Vercel', 'SPA-rewrite в vercel.json — все маршруты работают как отдельные демо-ссылки.'],
    ],
    cardsTitle: 'Лендинги',
    footer: 'Сборка для портфолио · не коммерческий продукт',
  },
  en: {
    kicker: 'Portfolio · Landing quartet',
    title: 'Four landings.',
    titleAccent: 'Four studios.',
    lead: 'A single Vite + React + TypeScript project, yet every landing looks as if a different team built it — its own grid, type, colour and rhythm.',
    demoNote: 'Demo concept for a portfolio. Copy is fictional but realistic.',
    open: 'Open landing',
    stackTitle: 'How it works',
    stack: [
      ['01', 'One Vite project', 'React Router splits four landings across routes. A shared RU / EN language context.'],
      ['02', 'Isolated styles', "Each landing's palette, type and grid live in their own src/landings folder."],
      ['03', 'Vercel-ready', 'An SPA rewrite in vercel.json keeps every route working as a standalone demo link.'],
    ],
    cardsTitle: 'The landings',
    footer: 'Portfolio build · not a commercial product',
  },
}

interface CardDef {
  to: string
  index: string
  style: string
  name: { ru: string; en: string }
  desc: { ru: string; en: string }
  Icon: typeof ChartBar
  accent: string
  bg: string
  preview: React.ReactNode
}

const cards: CardDef[] = [
  {
    to: '/saas',
    index: '01',
    style: 'Swiss',
    name: { ru: 'SaaS · Аналитика', en: 'SaaS · Analytics' },
    desc: {
      ru: 'Модульная сетка, гротеск, красный акцент. Данные как инфографика.',
      en: 'Modular grid, grotesque type, red accent. Data as infographics.',
    },
    Icon: ChartBar,
    accent: '#E4002B',
    bg: '#FFFFFF',
    preview: (
      <div className="flex h-full w-full items-end gap-1.5 p-5">
        {[30, 52, 40, 68, 84, 60, 96].map((h, i) => (
          <div key={i} className="flex-1 rounded-sm" style={{ height: `${h}%`, background: i === 6 ? '#E4002B' : '#111' }} />
        ))}
      </div>
    ),
  },
  {
    to: '/coffee',
    index: '02',
    style: 'Editorial',
    name: { ru: 'Кофейня', en: 'Coffee house' },
    desc: {
      ru: 'Крупный serif, много воздуха, кремовый фон и один тёплый акцент.',
      en: 'Large serif, generous whitespace, cream ground and one warm accent.',
    },
    Icon: Cup,
    accent: '#B8552E',
    bg: '#F6F1E7',
    preview: (
      <div className="flex h-full w-full flex-col justify-center gap-2 p-5" style={{ color: '#2A2320' }}>
        <span className="font-serif text-4xl leading-none">Roast</span>
        <span className="font-serif text-4xl italic leading-none" style={{ color: '#B8552E' }}>
          &amp; Rest
        </span>
      </div>
    ),
  },
  {
    to: '/app',
    index: '03',
    style: 'Tactile',
    name: { ru: 'Мобильное приложение', en: 'Mobile app' },
    desc: {
      ru: 'Тёмный премиум-интерфейс, глубина через тени и подсветку, CSS-мокап.',
      en: 'Dark premium UI, depth from shadow and glow, a CSS phone mockup.',
    },
    Icon: Phone,
    accent: '#5EE6B5',
    bg: '#0B0D12',
    preview: (
      <div className="flex h-full w-full items-center justify-center p-4">
        <div
          className="h-full w-16 rounded-[14px] border border-white/10"
          style={{ background: 'linear-gradient(160deg,#1C212D,#10131a)', boxShadow: '0 18px 40px -12px #5EE6B570, inset 0 1px 0 rgba(255,255,255,.08)' }}
        >
          <div className="mx-auto mt-2 h-1 w-6 rounded-full bg-white/20" />
          <div className="mt-3 space-y-1.5 px-2">
            <div className="h-1.5 rounded bg-app-glow/70" />
            <div className="h-1.5 w-3/4 rounded bg-white/15" />
            <div className="h-1.5 w-1/2 rounded bg-white/15" />
          </div>
        </div>
      </div>
    ),
  },
  {
    to: '/course',
    index: '04',
    style: 'Maximalist',
    name: { ru: 'Онлайн-курс', en: 'Online course' },
    desc: {
      ru: 'Смелая крупная типографика, контрастные блоки, огромные цифры результатов.',
      en: 'Bold oversized type, high-contrast blocks, huge outcome numbers.',
    },
    Icon: Bolt,
    accent: '#D8FF3E',
    bg: '#0E0E10',
    preview: (
      <div className="flex h-full w-full flex-col justify-center p-5" style={{ color: '#D8FF3E' }}>
        <span className="text-6xl font-black leading-none tracking-tighter">+240%</span>
        <span className="mt-1 text-xs font-bold uppercase tracking-widest text-white/60">outcome</span>
      </div>
    ),
  },
]

export default function IndexPage() {
  const { lang } = useLang()
  const t = copy[lang]

  return (
    <div className="min-h-screen bg-[#0c0c0d] text-white font-sans selection:bg-white selection:text-black">
      <Seo
        title={{ ru: 'Квартет лендингов', en: 'Landing quartet' }}
        description={{
          ru: 'Четыре лендинга в разных визуальных стилях: Swiss, Editorial, Tactile, Maximalist. Один Vite + React + TypeScript проект.',
          en: 'Four landings in distinct visual styles: Swiss, Editorial, Tactile, Maximalist. One Vite + React + TypeScript project.',
        }}
        path="/"
        themeColor="#0c0c0d"
      />

      {/* Top bar */}
      <header className="mx-auto flex max-w-6xl items-center justify-between px-5 py-6 sm:px-8">
        <div className="flex items-center gap-2.5">
          <span className="grid grid-cols-2 gap-0.5" aria-hidden="true">
            <span className="h-2.5 w-2.5 bg-swiss-red" />
            <span className="h-2.5 w-2.5 bg-course-lime" />
            <span className="h-2.5 w-2.5 bg-app-glow" />
            <span className="h-2.5 w-2.5 bg-coffee-accent" />
          </span>
          <span className="text-sm font-semibold tracking-tight">Landings Quartet</span>
        </div>
        <LangToggle activeClassName="text-white" inactiveClassName="text-white/35" />
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-6xl px-5 pb-8 pt-8 sm:px-8 sm:pt-16">
        <p className="mb-6 font-mono text-xs uppercase tracking-[0.2em] text-white/45">{t.kicker}</p>
        <h1 className="max-w-4xl text-[13vw] font-black leading-[0.92] tracking-tighter sm:text-7xl md:text-8xl">
          {t.title}
          <br />
          <span className="text-white/40">{t.titleAccent}</span>
        </h1>
        <p className="mt-8 max-w-2xl text-lg leading-relaxed text-white/70 sm:text-xl">{t.lead}</p>
        <p className="mt-5 inline-flex items-center gap-2 rounded-full border border-white/15 px-4 py-1.5 text-xs text-white/55">
          <span className="h-1.5 w-1.5 rounded-full bg-course-lime" aria-hidden="true" />
          {t.demoNote}
        </p>
      </section>

      {/* Cards */}
      <section className="mx-auto max-w-6xl px-5 pb-6 pt-10 sm:px-8" aria-label={t.cardsTitle}>
        <div className="grid gap-5 sm:grid-cols-2">
          {cards.map((c, i) => (
            <Reveal key={c.to} delay={i * 0.06}>
              <Link
                to={c.to}
                className="group block overflow-hidden rounded-2xl border border-white/10 bg-white/[0.02] transition-colors duration-300 hover:border-white/25 focus-visible:border-white/40"
              >
                {/* preview */}
                <div className="relative h-40 overflow-hidden border-b border-white/10" style={{ background: c.bg }}>
                  {c.preview}
                  <span className="absolute right-3 top-3 font-mono text-[11px] tracking-widest" style={{ color: c.accent }}>
                    {c.style.toUpperCase()}
                  </span>
                </div>
                {/* body */}
                <div className="flex items-start justify-between gap-4 p-5">
                  <div>
                    <div className="mb-2 flex items-center gap-2 text-white/40">
                      <c.Icon width={18} height={18} style={{ color: c.accent }} />
                      <span className="font-mono text-xs">{c.index}</span>
                    </div>
                    <h2 className="text-xl font-bold tracking-tight">{c.name[lang]}</h2>
                    <p className="mt-1.5 text-sm leading-relaxed text-white/55">{c.desc[lang]}</p>
                  </div>
                  <motion.span
                    className="mt-1 shrink-0 text-white/40 transition-colors group-hover:text-white"
                    aria-hidden="true"
                  >
                    <ArrowUpRight width={22} height={22} />
                  </motion.span>
                </div>
                <span className="sr-only">{t.open}: {c.name[lang]}</span>
              </Link>
            </Reveal>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-6xl px-5 py-20 sm:px-8">
        <h2 className="mb-10 text-sm font-mono uppercase tracking-[0.2em] text-white/45">{t.stackTitle}</h2>
        <div className="grid gap-8 border-t border-white/10 pt-10 sm:grid-cols-3">
          {t.stack.map(([n, h, d]) => (
            <div key={n}>
              <div className="mb-3 font-mono text-2xl text-white/25">{n}</div>
              <h3 className="mb-2 text-lg font-semibold">{h}</h3>
              <p className="text-sm leading-relaxed text-white/55">{d}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-white/10">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-5 py-8 text-xs text-white/40 sm:flex-row sm:items-center sm:justify-between sm:px-8">
          <span>© {new Date().getFullYear()} Landings Quartet</span>
          <span>{t.footer}</span>
        </div>
      </footer>
    </div>
  )
}
