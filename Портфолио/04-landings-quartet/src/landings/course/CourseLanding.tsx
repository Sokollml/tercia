import { useState } from 'react'
import { Link } from 'react-router-dom'
import Seo from '../../components/Seo'
import LangToggle from '../../components/LangToggle'
import Reveal from '../../components/Reveal'
import { useLang } from '../../i18n/LanguageContext'
import { ArrowRight, Check, Menu, Close, Sparkle } from '../../components/icons'
import { courseContent } from './content'
import CountUp from './CountUp'

/**
 * Maximalist style: bold oversized type, high-contrast colour blocks
 * (lime / pink / electric blue on near-black), huge outcome numbers.
 * Loud on purpose — the opposite of the Swiss and Editorial landings.
 */
export default function CourseLanding() {
  const { lang } = useLang()
  const t = courseContent[lang]
  const [menuOpen, setMenuOpen] = useState(false)
  const [openFaq, setOpenFaq] = useState<number | null>(0)

  // rotate accent colour per block for the maximalist rhythm
  const blockAccents = ['#D8FF3E', '#FF4D8D', '#2B5BFF', '#D8FF3E', '#FF4D8D', '#2B5BFF']

  return (
    <div className="min-h-screen bg-course-bg font-sans text-white antialiased selection:bg-course-lime selection:text-course-bg">
      <Seo
        title={{ ru: 'PROTOCOL · Продуктовый дизайн', en: 'PROTOCOL · Product design' }}
        description={{
          ru: 'PROTOCOL — интенсив по продуктовому дизайну: 12 недель, реальный кейс в портфолио и наставник до оффера.',
          en: 'PROTOCOL — a product design intensive: 12 weeks, a real portfolio case and a mentor all the way to an offer.',
        }}
        path="/course"
        themeColor="#0E0E10"
      />

      {/* Header */}
      <header className="sticky top-0 z-40 border-b-2 border-white/10 bg-course-bg/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4 sm:px-8">
          <span className="text-xl font-black uppercase tracking-tight">
            {t.brand}
            <span className="text-course-lime">.</span>
          </span>
          <nav className="hidden items-center gap-8 text-sm font-bold uppercase tracking-wide text-white/70 md:flex" aria-label="Primary">
            {t.nav.map((n) => (
              <a key={n} href="#" className="transition-colors hover:text-course-lime">
                {n}
              </a>
            ))}
          </nav>
          <div className="hidden items-center gap-5 md:flex">
            <LangToggle activeClassName="text-white" inactiveClassName="text-white/35" />
            <a
              href="#pricing"
              className="rounded-none border-2 border-course-lime bg-course-lime px-5 py-2 text-sm font-black uppercase text-course-bg transition-transform hover:-translate-y-0.5"
            >
              {t.heroCta}
            </a>
          </div>
          <button className="md:hidden" onClick={() => setMenuOpen((v) => !v)} aria-label="Menu" aria-expanded={menuOpen}>
            {menuOpen ? <Close /> : <Menu />}
          </button>
        </div>
        {menuOpen && (
          <div className="border-t-2 border-white/10 px-5 py-4 md:hidden">
            <nav className="flex flex-col gap-3 text-sm font-bold uppercase text-white/80" aria-label="Mobile">
              {t.nav.map((n) => (
                <a key={n} href="#" onClick={() => setMenuOpen(false)}>
                  {n}
                </a>
              ))}
            </nav>
            <div className="mt-4">
              <LangToggle activeClassName="text-white" inactiveClassName="text-white/35" />
            </div>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden border-b-2 border-white/10">
        <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
          <p className="mb-8 inline-flex items-center gap-2 border-2 border-course-pink px-4 py-1.5 text-xs font-black uppercase tracking-widest text-course-pink">
            <span className="h-2 w-2 bg-course-pink" aria-hidden="true" />
            {t.heroBadge}
          </p>
          <h1 className="text-[15vw] font-black uppercase leading-[0.85] tracking-tighter sm:text-8xl md:text-[8.5rem]">
            <span className="block">{t.heroTitleA}</span>
            <span className="block text-course-lime">{t.heroTitleB}</span>
            <span className="block italic">{t.heroTitleC}</span>
          </h1>
          <div className="mt-10 grid gap-8 md:grid-cols-[1.4fr_1fr] md:items-end">
            <p className="max-w-xl text-lg leading-relaxed text-white/70 sm:text-xl">{t.heroLead}</p>
            <div className="flex flex-col items-start gap-4">
              <a
                href="#pricing"
                className="inline-flex items-center gap-3 bg-course-lime px-8 py-4 text-base font-black uppercase text-course-bg transition-transform hover:-translate-y-1"
              >
                {t.heroCta}
                <ArrowRight width={20} height={20} />
              </a>
              <span className="inline-flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-course-pink">
                <Sparkle width={16} height={16} />
                {t.heroSeats}
              </span>
            </div>
          </div>
        </div>

        {/* Marquee */}
        <div className="overflow-hidden border-y-2 border-white/10 bg-course-lime py-3">
          <div className="flex w-max animate-marquee whitespace-nowrap">
            {[0, 1].map((dup) => (
              <div key={dup} className="flex items-center" aria-hidden={dup === 1}>
                {t.marquee.map((m) => (
                  <span key={m} className="mx-6 text-lg font-black uppercase tracking-tight text-course-bg">
                    {m}
                    <span className="ml-6 text-course-bg/40">/</span>
                  </span>
                ))}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section id="outcomes" className="border-b-2 border-white/10">
        <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-20">
          <h2 className="mb-12 max-w-lg text-4xl font-black uppercase leading-none tracking-tight sm:text-5xl">{t.statsTitle}</h2>
          <div className="grid gap-px overflow-hidden border-2 border-white/10 bg-white/10 sm:grid-cols-2 lg:grid-cols-4">
            {t.stats.map((s, i) => (
              <Reveal key={s.label} delay={i * 0.06} className="bg-course-bg p-7">
                <div
                  className="text-6xl font-black leading-none tracking-tighter sm:text-7xl"
                  style={{ color: blockAccents[i % 3] }}
                >
                  <CountUp to={s.value} />
                  <span className="text-3xl align-top">{s.suffix}</span>
                </div>
                <p className="mt-4 text-sm leading-relaxed text-white/60">{s.label}</p>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Program */}
      <section id="program" className="border-b-2 border-white/10">
        <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-20">
          <div className="mb-12 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <h2 className="text-4xl font-black uppercase leading-none tracking-tight sm:text-5xl">{t.programTitle}</h2>
            <p className="max-w-sm text-sm leading-relaxed text-white/60">{t.programNote}</p>
          </div>
          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {t.modules.map((m, i) => (
              <Reveal key={m.n} delay={i * 0.05}>
                <div
                  className="group h-full border-2 border-white/10 p-7 transition-colors hover:border-white/30"
                  style={{ borderTopWidth: 6, borderTopColor: blockAccents[i % 3] }}
                >
                  <span className="text-5xl font-black tracking-tighter text-white/15">{m.n}</span>
                  <h3 className="mt-4 text-xl font-black uppercase tracking-tight">{m.t}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-white/60">{m.d}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Result block */}
      <section className="border-b-2 border-white/10 bg-course-pink text-course-bg">
        <div className="mx-auto grid max-w-6xl gap-10 px-5 py-16 sm:px-8 sm:py-20 md:grid-cols-2 md:items-center">
          <div>
            <h2 className="text-4xl font-black uppercase leading-[0.9] tracking-tight sm:text-6xl">{t.resultTitle}</h2>
            <p className="mt-5 max-w-md text-lg font-semibold leading-relaxed">{t.resultLead}</p>
          </div>
          <ul className="grid gap-3">
            {t.outcomes.map((o) => (
              <li key={o} className="flex items-center gap-4 border-2 border-course-bg bg-course-bg/5 px-5 py-4 text-base font-bold uppercase tracking-tight">
                <span className="grid h-8 w-8 shrink-0 place-items-center bg-course-bg text-course-pink">
                  <Check width={18} height={18} />
                </span>
                {o}
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Mentors */}
      <section id="mentors" className="border-b-2 border-white/10">
        <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-20">
          <h2 className="mb-12 text-4xl font-black uppercase leading-none tracking-tight sm:text-5xl">{t.mentorsTitle}</h2>
          <div className="grid gap-5 md:grid-cols-3">
            {t.mentors.map((m, i) => (
              <Reveal key={m.name} delay={i * 0.06}>
                <div className="h-full border-2 border-white/10 p-7">
                  <div
                    className="mb-6 flex aspect-square w-full items-end justify-start p-4"
                    style={{ background: `linear-gradient(135deg, ${blockAccents[i % 3]}, ${blockAccents[(i + 1) % 3]})` }}
                    aria-hidden="true"
                  >
                    <span className="text-7xl font-black uppercase text-course-bg/80">{m.name.charAt(0)}</span>
                  </div>
                  <h3 className="text-xl font-black uppercase tracking-tight">{m.name}</h3>
                  <p className="mt-1 text-sm font-bold uppercase tracking-wide" style={{ color: blockAccents[i % 3] }}>
                    {m.role}
                  </p>
                  <p className="mt-3 text-sm leading-relaxed text-white/60">{m.bio}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="border-b-2 border-white/10">
        <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-20">
          <div className="border-4 border-course-lime bg-course-lime/5">
            <div className="grid gap-10 p-8 sm:p-12 md:grid-cols-[1fr_1.1fr] md:items-center">
              <div>
                <h2 className="text-3xl font-black uppercase leading-none tracking-tight sm:text-4xl">{t.pricingTitle}</h2>
                <div className="mt-8 flex items-end gap-4">
                  <span className="text-6xl font-black tracking-tighter text-course-lime sm:text-7xl">{t.priceNew}</span>
                  <span className="pb-3 text-2xl font-bold text-white/30 line-through">{t.priceOld}</span>
                </div>
                <p className="mt-3 text-sm text-white/60">{t.priceNote}</p>
                <div className="mt-6 border-l-4 border-course-pink pl-4 text-sm font-semibold text-white/80">{t.guarantee}</div>
              </div>
              <div>
                <ul className="grid gap-3">
                  {t.priceFeatures.map((f) => (
                    <li key={f} className="flex items-center gap-3 text-base font-bold uppercase tracking-tight">
                      <span className="grid h-7 w-7 shrink-0 place-items-center bg-course-lime text-course-bg">
                        <Check width={16} height={16} />
                      </span>
                      {f}
                    </li>
                  ))}
                </ul>
                <a
                  href="#"
                  className="mt-8 inline-flex w-full items-center justify-center gap-3 bg-course-lime px-8 py-4 text-base font-black uppercase text-course-bg transition-transform hover:-translate-y-1"
                >
                  {t.heroCta}
                  <ArrowRight width={20} height={20} />
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="border-b-2 border-white/10">
        <div className="mx-auto max-w-3xl px-5 py-16 sm:px-8 sm:py-20">
          <h2 className="mb-10 text-4xl font-black uppercase leading-none tracking-tight sm:text-5xl">{t.faqTitle}</h2>
          <div className="divide-y-2 divide-white/10 border-y-2 border-white/10">
            {t.faq.map((item, i) => {
              const open = openFaq === i
              return (
                <div key={item.q}>
                  <button
                    type="button"
                    onClick={() => setOpenFaq(open ? null : i)}
                    aria-expanded={open}
                    className="flex w-full items-center justify-between gap-4 py-5 text-left"
                  >
                    <span className="text-lg font-black uppercase tracking-tight">{item.q}</span>
                    <span
                      className="grid h-8 w-8 shrink-0 place-items-center border-2 text-2xl leading-none transition-transform"
                      style={{
                        borderColor: open ? '#D8FF3E' : 'rgba(255,255,255,0.2)',
                        color: open ? '#D8FF3E' : '#fff',
                        transform: open ? 'rotate(45deg)' : 'none',
                      }}
                      aria-hidden="true"
                    >
                      +
                    </span>
                  </button>
                  {open && <p className="pb-6 text-base leading-relaxed text-white/65">{item.a}</p>}
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="border-b-2 border-white/10 bg-course-blue">
        <div className="mx-auto max-w-4xl px-5 py-20 text-center sm:px-8">
          <h2 className="mx-auto max-w-2xl text-4xl font-black uppercase leading-[0.9] tracking-tight sm:text-6xl">{t.ctaTitle}</h2>
          <p className="mx-auto mt-6 max-w-lg text-lg font-semibold text-white/80">{t.ctaLead}</p>
          <a
            href="#pricing"
            className="mt-10 inline-flex items-center gap-3 bg-course-lime px-10 py-5 text-lg font-black uppercase text-course-bg transition-transform hover:-translate-y-1"
          >
            {t.ctaButton}
            <ArrowRight width={22} height={22} />
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer>
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-5 py-10 sm:flex-row sm:items-center sm:justify-between sm:px-8">
          <span className="text-xl font-black uppercase tracking-tight">
            {t.brand}
            <span className="text-course-lime">.</span>
          </span>
          <p className="max-w-sm text-xs text-white/40">{t.footerNote}</p>
          <Link
            to="/"
            className="inline-flex items-center gap-1 text-xs font-black uppercase tracking-widest text-white/70 hover:text-course-lime"
          >
            <ArrowRight width={14} height={14} className="rotate-180" />
            {t.backHub}
          </Link>
        </div>
      </footer>
    </div>
  )
}
