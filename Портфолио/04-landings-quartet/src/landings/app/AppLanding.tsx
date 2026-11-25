import { useState } from 'react'
import { Link } from 'react-router-dom'
import Seo from '../../components/Seo'
import LangToggle from '../../components/LangToggle'
import Reveal from '../../components/Reveal'
import { useLang } from '../../i18n/LanguageContext'
import { ArrowRight, Play, Sparkle, Bell, Target, Lock, Check, Menu, Close } from '../../components/icons'
import { appContent } from './content'
import PhoneMockup from './PhoneMockup'

const featureIcons = [Sparkle, Bell, Target, Lock]

/** Tactile style: premium dark UI, depth from soft shadows and glow (no glass cards). */
export default function AppLanding() {
  const { lang } = useLang()
  const t = appContent[lang]
  const [menuOpen, setMenuOpen] = useState(false)

  const surface = {
    background: 'linear-gradient(160deg,#1a1f2b,#12151d)',
    boxShadow: '0 24px 48px -24px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.05)',
  }

  return (
    <div className="min-h-screen bg-app-bg font-sans text-white antialiased selection:bg-app-glow selection:text-app-bg">
      <Seo
        title={{ ru: 'Tempo · Деньги под контролем', en: 'Tempo · Money under control' }}
        description={{
          ru: 'Tempo — приложение личных финансов: связывает счета, раскладывает траты и тихо подсказывает.',
          en: 'Tempo — a personal finance app that links accounts, sorts spending and nudges you quietly.',
        }}
        path="/app"
        themeColor="#0B0D12"
      />

      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-white/5 bg-app-bg/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4 sm:px-8">
          <div className="flex items-center gap-2.5">
            <span
              className="grid h-8 w-8 place-items-center rounded-xl text-app-bg"
              style={{ background: 'linear-gradient(180deg,#7bf0c5,#3fcfa0)', boxShadow: '0 6px 14px -6px rgba(94,230,181,0.7)' }}
            >
              <Play width={16} height={16} />
            </span>
            <span className="text-lg font-bold tracking-tight">{t.brand}</span>
          </div>
          <nav className="hidden items-center gap-8 text-sm text-white/70 md:flex" aria-label="Primary">
            {t.nav.map((n) => (
              <a key={n} href="#" className="transition-colors hover:text-white">
                {n}
              </a>
            ))}
          </nav>
          <div className="hidden items-center gap-4 md:flex">
            <LangToggle activeClassName="text-white" inactiveClassName="text-white/35" />
            <a
              href="#get"
              className="rounded-full px-5 py-2 text-sm font-semibold text-app-bg transition-transform hover:-translate-y-0.5"
              style={{ background: 'linear-gradient(180deg,#7bf0c5,#3fcfa0)', boxShadow: '0 10px 20px -8px rgba(94,230,181,0.6)' }}
            >
              {t.ctaPrimary}
            </a>
          </div>
          <button className="md:hidden" onClick={() => setMenuOpen((v) => !v)} aria-label="Menu" aria-expanded={menuOpen}>
            {menuOpen ? <Close /> : <Menu />}
          </button>
        </div>
        {menuOpen && (
          <div className="border-t border-white/5 px-5 py-4 md:hidden">
            <nav className="flex flex-col gap-3 text-sm text-white/80" aria-label="Mobile">
              {t.nav.map((n) => (
                <a key={n} href="#" onClick={() => setMenuOpen(false)}>
                  {n}
                </a>
              ))}
            </nav>
            <div className="mt-4"><LangToggle activeClassName="text-white" inactiveClassName="text-white/35" /></div>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute -right-40 -top-40 h-96 w-96 rounded-full bg-app-glow/10 blur-3xl" aria-hidden="true" />
        <div className="pointer-events-none absolute -left-40 top-40 h-96 w-96 rounded-full bg-app-glow2/10 blur-3xl" aria-hidden="true" />
        <div className="mx-auto grid max-w-6xl items-center gap-12 px-5 py-14 sm:px-8 md:grid-cols-2 md:py-20">
          <div>
            <p className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/10 px-3 py-1 text-xs uppercase tracking-widest text-app-glow">
              <span className="h-1.5 w-1.5 rounded-full bg-app-glow" />
              {t.heroKicker}
            </p>
            <h1 className="text-4xl font-bold leading-[1.05] tracking-tight sm:text-5xl md:text-[3.4rem]">{t.heroTitle}</h1>
            <p className="mt-6 max-w-md text-lg leading-relaxed text-white/65">{t.heroLead}</p>
            <div className="mt-9 flex flex-wrap items-center gap-4">
              <a
                href="#get"
                className="inline-flex items-center gap-2 rounded-2xl px-7 py-3.5 text-sm font-semibold text-app-bg transition-transform hover:-translate-y-0.5 active:translate-y-0"
                style={{ background: 'linear-gradient(180deg,#7bf0c5,#3fcfa0)', boxShadow: '0 16px 30px -12px rgba(94,230,181,0.7), inset 0 1px 0 rgba(255,255,255,0.5)' }}
              >
                {t.ctaPrimary}
                <ArrowRight width={18} height={18} />
              </a>
              <a
                href="#how"
                className="inline-flex items-center gap-2 rounded-2xl px-6 py-3.5 text-sm font-semibold text-white transition-colors"
                style={surface}
              >
                <Play width={16} height={16} className="text-app-glow" />
                {t.ctaSecondary}
              </a>
            </div>
            <div className="mt-8 flex items-center gap-3 text-sm text-white/55">
              <div className="flex gap-0.5 text-app-glow" aria-hidden="true">
                {Array.from({ length: 5 }).map((_, i) => (
                  <svg key={i} width={16} height={16} viewBox="0 0 24 24" fill="currentColor">
                    <path d="m12 3 2.6 5.5 6 .8-4.4 4.2 1.1 6-5.3-2.9L6.7 19.5l1.1-6L3.4 9.3l6-.8L12 3Z" />
                  </svg>
                ))}
              </div>
              {t.ratingNote}
            </div>
          </div>

          <Reveal delay={0.1}>
            <PhoneMockup phone={t.phone} />
          </Reveal>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-5 py-16 sm:px-8">
        <h2 className="mb-10 max-w-lg text-3xl font-bold tracking-tight sm:text-4xl">{t.featuresTitle}</h2>
        <div className="grid gap-5 sm:grid-cols-2">
          {t.features.map((f, i) => {
            const Icon = featureIcons[i]
            return (
              <Reveal key={f.t} delay={i * 0.06}>
                <div className="h-full rounded-3xl p-7" style={surface}>
                  <span
                    className="mb-5 grid h-12 w-12 place-items-center rounded-2xl text-app-glow"
                    style={{ background: 'radial-gradient(circle at 30% 30%,#1f2836,#141821)', boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.08), 0 8px 18px -10px rgba(94,230,181,0.4)' }}
                  >
                    <Icon width={24} height={24} />
                  </span>
                  <h3 className="text-xl font-semibold">{f.t}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-white/60">{f.d}</p>
                </div>
              </Reveal>
            )
          })}
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="mx-auto max-w-6xl px-5 py-16 sm:px-8">
        <h2 className="mb-12 text-3xl font-bold tracking-tight sm:text-4xl">{t.stepsTitle}</h2>
        <div className="grid gap-6 md:grid-cols-3">
          {t.steps.map((s, i) => (
            <Reveal key={s.n} delay={i * 0.08}>
              <div className="relative h-full rounded-3xl p-7" style={surface}>
                <span
                  className="mb-5 grid h-11 w-11 place-items-center rounded-full text-lg font-bold text-app-bg"
                  style={{ background: 'linear-gradient(180deg,#7bf0c5,#3fcfa0)', boxShadow: '0 10px 20px -8px rgba(94,230,181,0.6)' }}
                >
                  {s.n}
                </span>
                <h3 className="text-xl font-semibold">{s.t}</h3>
                <p className="mt-2 text-sm leading-relaxed text-white/60">{s.d}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* Testimonials */}
      <section className="mx-auto max-w-6xl px-5 py-16 sm:px-8">
        <h2 className="mb-10 text-3xl font-bold tracking-tight sm:text-4xl">{t.testimonialsTitle}</h2>
        <div className="grid gap-5 md:grid-cols-3">
          {t.testimonials.map((tm, i) => (
            <Reveal key={tm.name} delay={i * 0.06}>
              <figure className="flex h-full flex-col rounded-3xl p-7" style={surface}>
                <div className="mb-4 flex gap-0.5 text-app-glow" aria-hidden="true">
                  {Array.from({ length: 5 }).map((_, j) => (
                    <svg key={j} width={15} height={15} viewBox="0 0 24 24" fill="currentColor">
                      <path d="m12 3 2.6 5.5 6 .8-4.4 4.2 1.1 6-5.3-2.9L6.7 19.5l1.1-6L3.4 9.3l6-.8L12 3Z" />
                    </svg>
                  ))}
                </div>
                <blockquote className="flex-1 text-base leading-relaxed text-white/80">{tm.quote}</blockquote>
                <figcaption className="mt-5 text-sm font-medium text-white/50">{tm.name}</figcaption>
              </figure>
            </Reveal>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="get" className="mx-auto max-w-6xl px-5 py-16 sm:px-8">
        <div className="mx-auto max-w-md rounded-[2rem] p-8 text-center" style={surface}>
          <h2 className="text-2xl font-bold">{t.pricingTitle}</h2>
          <div className="mt-6 flex items-end justify-center gap-1">
            <span className="text-5xl font-black tracking-tight">{t.priceValue}</span>
            <span className="pb-2 text-white/50">{t.pricePeriod}</span>
          </div>
          <p className="mt-2 text-sm text-white/55">{t.priceNote}</p>
          <ul className="mt-7 space-y-3 text-left">
            {t.priceFeatures.map((f) => (
              <li key={f} className="flex items-center gap-3 text-sm text-white/80">
                <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-app-glow/15 text-app-glow">
                  <Check width={15} height={15} />
                </span>
                {f}
              </li>
            ))}
          </ul>
          <a
            href="#"
            className="mt-8 inline-flex w-full items-center justify-center gap-2 rounded-2xl py-3.5 text-sm font-semibold text-app-bg transition-transform hover:-translate-y-0.5 active:translate-y-0"
            style={{ background: 'linear-gradient(180deg,#7bf0c5,#3fcfa0)', boxShadow: '0 16px 30px -12px rgba(94,230,181,0.7), inset 0 1px 0 rgba(255,255,255,0.5)' }}
          >
            {t.ctaPrimary}
            <ArrowRight width={18} height={18} />
          </a>
        </div>
      </section>

      {/* Final CTA */}
      <section className="mx-auto max-w-6xl px-5 pb-20 sm:px-8">
        <div
          className="relative overflow-hidden rounded-[2rem] px-8 py-14 text-center"
          style={{ background: 'linear-gradient(160deg,#15303a,#101722)', boxShadow: '0 30px 60px -30px rgba(94,230,181,0.4), inset 0 1px 0 rgba(255,255,255,0.06)' }}
        >
          <div className="pointer-events-none absolute -top-20 left-1/2 h-64 w-64 -translate-x-1/2 rounded-full bg-app-glow/20 blur-3xl" aria-hidden="true" />
          <h2 className="relative mx-auto max-w-xl text-3xl font-bold tracking-tight sm:text-4xl">{t.ctaTitle}</h2>
          <p className="relative mx-auto mt-4 max-w-md text-white/65">{t.ctaLead}</p>
          <a
            href="#"
            className="relative mt-8 inline-flex items-center gap-2 rounded-2xl px-8 py-4 text-sm font-semibold text-app-bg transition-transform hover:-translate-y-0.5"
            style={{ background: 'linear-gradient(180deg,#7bf0c5,#3fcfa0)', boxShadow: '0 16px 30px -12px rgba(94,230,181,0.7), inset 0 1px 0 rgba(255,255,255,0.5)' }}
          >
            {t.ctaPrimary}
            <ArrowRight width={18} height={18} />
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-5 py-10 sm:flex-row sm:items-center sm:justify-between sm:px-8">
          <span className="text-lg font-bold tracking-tight">{t.brand}</span>
          <p className="max-w-sm text-xs text-white/40">{t.footerNote}</p>
          <Link to="/" className="inline-flex items-center gap-1 text-xs font-semibold uppercase tracking-widest text-white/70 hover:text-app-glow">
            <ArrowRight width={14} height={14} className="rotate-180" />
            {t.backHub}
          </Link>
        </div>
      </footer>
    </div>
  )
}
