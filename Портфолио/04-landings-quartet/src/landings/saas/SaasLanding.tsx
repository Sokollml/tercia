import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Seo from '../../components/Seo'
import LangToggle from '../../components/LangToggle'
import Reveal from '../../components/Reveal'
import { useLang } from '../../i18n/LanguageContext'
import { ArrowRight, ArrowUpRight, Layers, Shield, Bell, ChartBar, Lock, Globe, Check, Menu, Close } from '../../components/icons'
import { saasContent } from './content'

const featureIcons = [Layers, ChartBar, Globe, Bell, Lock, Shield]

/** Swiss / International Typographic style: red-black-white, strict modular grid. */
export default function SaasLanding() {
  const { lang } = useLang()
  const t = saasContent[lang]
  const [menuOpen, setMenuOpen] = useState(false)

  // cumulative revenue series for the line chart (12 weeks)
  const series = [8, 11, 10, 14, 19, 23, 22, 28, 34, 39, 47, 61]
  const max = Math.max(...series)
  const w = 640
  const h = 220
  const pts = series.map((v, i) => [(i / (series.length - 1)) * w, h - (v / max) * (h - 20) - 8])
  const linePath = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(' ')
  const areaPath = `${linePath} L${w},${h} L0,${h} Z`

  return (
    <div className="min-h-screen bg-swiss-paper font-sans text-swiss-ink antialiased selection:bg-swiss-red selection:text-white">
      <Seo
        title={{ ru: 'Meridian · Аналитика продукта', en: 'Meridian · Product analytics' }}
        description={{
          ru: 'Meridian — продуктовая аналитика: воронки, удержание и выручка в одной модели данных.',
          en: 'Meridian — product analytics: funnels, retention and revenue in one data model.',
        }}
        path="/saas"
        themeColor="#FFFFFF"
      />

      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-swiss-ink bg-swiss-paper">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4 sm:px-6">
          <div className="flex items-center gap-2">
            <span className="block h-4 w-4 bg-swiss-red" aria-hidden="true" />
            <span className="text-lg font-bold tracking-tight">{t.brand}</span>
          </div>
          <nav className="hidden items-center gap-8 text-sm font-medium md:flex" aria-label="Primary">
            {t.nav.map((n) => (
              <a key={n} href="#" className="hover:text-swiss-red">
                {n}
              </a>
            ))}
          </nav>
          <div className="hidden items-center gap-4 md:flex">
            <LangToggle activeClassName="text-swiss-ink" inactiveClassName="text-swiss-ink/35" />
            <a href="#" className="text-sm font-medium hover:text-swiss-red">
              {t.login}
            </a>
            <a href="#cta" className="bg-swiss-ink px-4 py-2 text-sm font-semibold text-swiss-paper hover:bg-swiss-red">
              {t.cta}
            </a>
          </div>
          <button className="md:hidden" onClick={() => setMenuOpen((v) => !v)} aria-label="Menu" aria-expanded={menuOpen}>
            {menuOpen ? <Close /> : <Menu />}
          </button>
        </div>
        {menuOpen && (
          <div className="border-t border-swiss-ink px-5 py-4 md:hidden">
            <nav className="flex flex-col gap-3 text-sm font-medium" aria-label="Mobile">
              {t.nav.map((n) => (
                <a key={n} href="#" onClick={() => setMenuOpen(false)}>
                  {n}
                </a>
              ))}
            </nav>
            <div className="mt-4 flex items-center justify-between">
              <LangToggle activeClassName="text-swiss-ink" inactiveClassName="text-swiss-ink/35" />
              <a href="#cta" className="bg-swiss-ink px-4 py-2 text-sm font-semibold text-swiss-paper">
                {t.cta}
              </a>
            </div>
          </div>
        )}
      </header>

      {/* Hero — asymmetric modular grid */}
      <section className="border-b border-swiss-ink">
        <div className="mx-auto grid max-w-6xl grid-cols-1 md:grid-cols-12">
          <div className="col-span-12 border-swiss-ink px-5 py-12 sm:px-6 md:col-span-8 md:border-r md:py-20">
            <p className="mb-8 font-mono text-xs uppercase tracking-[0.25em] text-swiss-red">{t.heroKicker}</p>
            <h1 className="max-w-3xl text-[10.5vw] font-black uppercase leading-[0.9] tracking-tight sm:text-6xl md:text-[5.2rem]">
              {t.heroTitle}
            </h1>
            <p className="mt-8 max-w-xl text-lg leading-relaxed text-swiss-ink/75">{t.heroLead}</p>
            <div className="mt-10 flex flex-wrap items-center gap-4">
              <a
                href="#cta"
                className="inline-flex items-center gap-2 bg-swiss-red px-6 py-3 text-sm font-semibold uppercase tracking-wide text-white transition-colors hover:bg-swiss-ink"
              >
                {t.cta}
                <ArrowRight width={18} height={18} />
              </a>
              <a href="#metrics" className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wide hover:text-swiss-red">
                {t.metricsTitle}
                <ArrowUpRight width={16} height={16} />
              </a>
            </div>
          </div>
          {/* stat column */}
          <div className="col-span-12 grid grid-cols-3 md:col-span-4 md:grid-cols-1">
            {[
              ['1.2M', t.heroStat1],
              ['40+', t.heroStat2],
              ['10 ', t.heroStat3],
            ].map(([n, l], i) => (
              <div key={i} className={`border-swiss-ink px-5 py-6 sm:px-6 ${i < 2 ? 'border-r md:border-b md:border-r-0' : ''}`}>
                <div className="font-mono text-3xl font-bold sm:text-4xl">
                  {n}
                  {i === 2 && <span className="text-swiss-red">min</span>}
                </div>
                <div className="mt-1 text-xs uppercase tracking-wide text-swiss-ink/55">{l}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Metrics row */}
      <section id="metrics" className="border-b border-swiss-ink">
        <div className="mx-auto max-w-6xl px-5 py-14 sm:px-6">
          <div className="mb-10 flex items-baseline justify-between border-b border-swiss-grid pb-4">
            <h2 className="text-2xl font-bold uppercase tracking-tight sm:text-3xl">{t.metricsTitle}</h2>
            <span className="hidden font-mono text-xs uppercase tracking-widest text-swiss-ink/40 sm:block">{t.trustLabel}</span>
          </div>
          <div className="grid gap-px bg-swiss-ink sm:grid-cols-3">
            {t.metrics.map((m) => {
              const down = m.delta.trim().startsWith('−')
              return (
                <div key={m.k} className="bg-swiss-paper p-6">
                  <div className="mb-4 font-mono text-xs uppercase tracking-widest text-swiss-ink/55">{m.k}</div>
                  <div className="flex items-baseline gap-1">
                    <span className="text-5xl font-black tracking-tight sm:text-6xl">{m.v}</span>
                    <span className="text-xl font-bold text-swiss-ink/50">{m.unit}</span>
                  </div>
                  <div className="mt-4 flex items-center gap-2 text-sm">
                    <span className={`font-mono font-bold ${down ? 'text-swiss-ink/50' : 'text-swiss-red'}`}>{m.delta}</span>
                    <span className="text-swiss-ink/50">{m.note}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Funnel + line chart */}
      <section className="border-b border-swiss-ink">
        <div className="mx-auto grid max-w-6xl grid-cols-1 md:grid-cols-2">
          {/* Funnel */}
          <div className="border-swiss-ink px-5 py-14 sm:px-6 md:border-r">
            <h2 className="text-xl font-bold uppercase tracking-tight">{t.funnelTitle}</h2>
            <p className="mt-2 max-w-sm text-sm text-swiss-ink/60">{t.funnelNote}</p>
            <div className="mt-8 space-y-3">
              {t.funnel.map((step, i) => (
                <Reveal key={step.label} delay={i * 0.05}>
                  <div>
                    <div className="mb-1 flex items-baseline justify-between font-mono text-xs">
                      <span className="uppercase tracking-wide text-swiss-ink/70">{step.label}</span>
                      <span className="font-bold">{step.value}%</span>
                    </div>
                    <div className="h-7 w-full bg-swiss-grid">
                      <motion.div
                        className={i === t.funnel.length - 1 ? 'h-full bg-swiss-red' : 'h-full bg-swiss-ink'}
                        initial={{ width: 0 }}
                        whileInView={{ width: `${step.value}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8, delay: i * 0.06, ease: [0.22, 1, 0.36, 1] }}
                      />
                    </div>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
          {/* Line chart */}
          <div className="px-5 py-14 sm:px-6">
            <h2 className="text-xl font-bold uppercase tracking-tight">{t.chartTitle}</h2>
            <p className="mt-2 text-sm text-swiss-ink/60">{t.chartNote}</p>
            <div className="mt-8">
              <svg viewBox={`0 0 ${w} ${h}`} className="w-full" role="img" aria-label={t.chartTitle}>
                {[0.25, 0.5, 0.75, 1].map((g) => (
                  <line key={g} x1="0" x2={w} y1={h - g * (h - 20) - 8} y2={h - g * (h - 20) - 8} stroke="#EDEDED" strokeWidth="1" />
                ))}
                <motion.path
                  d={areaPath}
                  fill="#E4002B"
                  opacity="0.08"
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 0.08 }}
                  viewport={{ once: true }}
                  transition={{ duration: 1 }}
                />
                <motion.path
                  d={linePath}
                  fill="none"
                  stroke="#E4002B"
                  strokeWidth="2.5"
                  initial={{ pathLength: 0 }}
                  whileInView={{ pathLength: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 1.2, ease: 'easeInOut' }}
                />
                {pts.map((p, i) => (
                  <circle key={i} cx={p[0]} cy={p[1]} r={i === pts.length - 1 ? 5 : 2.5} fill={i === pts.length - 1 ? '#E4002B' : '#0A0A0A'} />
                ))}
              </svg>
              <div className="mt-2 flex justify-between font-mono text-[10px] uppercase tracking-widest text-swiss-ink/40">
                <span>W1</span>
                <span>W6</span>
                <span>W12</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features grid */}
      <section className="border-b border-swiss-ink">
        <div className="mx-auto max-w-6xl px-5 py-14 sm:px-6">
          <h2 className="mb-10 text-2xl font-bold uppercase tracking-tight sm:text-3xl">{t.featuresTitle}</h2>
          <div className="grid gap-px bg-swiss-ink sm:grid-cols-2 lg:grid-cols-3">
            {t.features.map((f, i) => {
              const Icon = featureIcons[i % featureIcons.length]
              return (
                <div key={f.t} className="group bg-swiss-paper p-6">
                  <div className="mb-5 flex items-center justify-between">
                    <Icon width={26} height={26} className="text-swiss-ink group-hover:text-swiss-red" />
                    <span className="font-mono text-xs text-swiss-ink/30">0{i + 1}</span>
                  </div>
                  <h3 className="text-lg font-bold">{f.t}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-swiss-ink/65">{f.d}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="border-b border-swiss-ink">
        <div className="mx-auto max-w-6xl px-5 py-14 sm:px-6">
          <div className="mb-10 flex flex-col justify-between gap-2 border-b border-swiss-grid pb-4 sm:flex-row sm:items-baseline">
            <h2 className="text-2xl font-bold uppercase tracking-tight sm:text-3xl">{t.pricingTitle}</h2>
            <p className="text-sm text-swiss-ink/60">{t.pricingNote}</p>
          </div>
          <div className="grid gap-px bg-swiss-ink lg:grid-cols-3">
            {t.plans.map((p) => (
              <div key={p.name} className={`flex flex-col p-6 ${p.featured ? 'bg-swiss-ink text-swiss-paper' : 'bg-swiss-paper'}`}>
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold uppercase tracking-widest">{p.name}</h3>
                  {p.featured && <span className="bg-swiss-red px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider">Popular</span>}
                </div>
                <div className="mt-6 flex items-baseline gap-1">
                  <span className="text-4xl font-black tracking-tight">{p.price}</span>
                  {p.period && <span className={`text-sm ${p.featured ? 'text-swiss-paper/60' : 'text-swiss-ink/50'}`}>{p.period}</span>}
                </div>
                <p className={`mt-2 text-sm ${p.featured ? 'text-swiss-paper/70' : 'text-swiss-ink/60'}`}>{p.desc}</p>
                <ul className="mt-6 flex-1 space-y-2.5 text-sm">
                  {p.features.map((f) => (
                    <li key={f} className="flex items-start gap-2">
                      <Check width={18} height={18} className={p.featured ? 'text-swiss-red' : 'text-swiss-red'} />
                      <span className={p.featured ? 'text-swiss-paper/85' : ''}>{f}</span>
                    </li>
                  ))}
                </ul>
                <a
                  href="#cta"
                  className={`mt-8 inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold uppercase tracking-wide transition-colors ${
                    p.featured ? 'bg-swiss-red text-white hover:bg-swiss-paper hover:text-swiss-ink' : 'bg-swiss-ink text-swiss-paper hover:bg-swiss-red'
                  }`}
                >
                  {p.cta}
                  <ArrowRight width={16} height={16} />
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="cta" className="border-b border-swiss-ink bg-swiss-ink text-swiss-paper">
        <div className="mx-auto flex max-w-6xl flex-col items-start gap-8 px-5 py-16 sm:px-6 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="max-w-xl text-3xl font-black uppercase leading-tight tracking-tight sm:text-4xl">{t.ctaTitle}</h2>
            <p className="mt-4 max-w-md text-swiss-paper/70">{t.ctaLead}</p>
          </div>
          <a
            href="#"
            className="inline-flex shrink-0 items-center gap-2 bg-swiss-red px-8 py-4 text-sm font-semibold uppercase tracking-wide text-white transition-colors hover:bg-swiss-paper hover:text-swiss-ink"
          >
            {t.cta}
            <ArrowRight width={18} height={18} />
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="mx-auto max-w-6xl px-5 py-10 sm:px-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <span className="block h-3 w-3 bg-swiss-red" aria-hidden="true" />
            <span className="font-bold">{t.brand}</span>
          </div>
          <p className="max-w-md text-xs text-swiss-ink/50">{t.footerNote}</p>
          <Link to="/" className="inline-flex items-center gap-1 text-xs font-semibold uppercase tracking-widest hover:text-swiss-red">
            <ArrowRight width={14} height={14} className="rotate-180" />
            {t.backHub}
          </Link>
        </div>
      </footer>
    </div>
  )
}
