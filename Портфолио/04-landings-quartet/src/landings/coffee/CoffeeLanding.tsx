import { useState } from 'react'
import { Link } from 'react-router-dom'
import Seo from '../../components/Seo'
import LangToggle from '../../components/LangToggle'
import Reveal from '../../components/Reveal'
import { useLang } from '../../i18n/LanguageContext'
import { ArrowRight, Bean, Clock, Leaf, Menu, Close } from '../../components/icons'
import { coffeeContent } from './content'
import roastPhoto from './roast.jpg'
import roomPhoto from './room.jpg'

/**
 * Editorial style: large Playfair serif, generous whitespace, cream ground,
 * one warm terracotta accent, magazine layout. Photos are CC0 stock with
 * captions; the gradient stays as the colour behind a loading image.
 */

function Photo({
  gradient,
  src,
  alt,
  caption,
  className = '',
  ratio = 'aspect-[4/5]',
}: {
  gradient: string
  src?: string
  alt?: string
  caption?: string
  className?: string
  ratio?: string
}) {
  return (
    <figure className={className}>
      <div
        className={`relative ${ratio} w-full overflow-hidden rounded-sm`}
        style={{ background: gradient }}
      >
        {src ? (
          <img
            src={src}
            alt={alt ?? caption ?? ''}
            loading="lazy"
            decoding="async"
            className="absolute inset-0 h-full w-full object-cover"
          />
        ) : (
          <>
            {/* subtle glossy sheen */}
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-tr from-black/15 via-transparent to-white/25" />
            <div className="pointer-events-none absolute inset-0 opacity-[0.06] mix-blend-multiply" style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, #000 1px, transparent 0)', backgroundSize: '4px 4px' }} />
            <span className="absolute bottom-3 left-3 rounded-full bg-black/25 px-3 py-1 text-[11px] font-medium tracking-wide text-white backdrop-blur-sm">
              photo placeholder
            </span>
          </>
        )}
      </div>
      {caption && <figcaption className="mt-3 font-serif text-sm italic text-coffee-muted">{caption}</figcaption>}
    </figure>
  )
}

export default function CoffeeLanding() {
  const { lang } = useLang()
  const t = coffeeContent[lang]
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-coffee-cream font-serif text-coffee-ink antialiased selection:bg-coffee-accent selection:text-coffee-cream">
      <Seo
        title={{ ru: 'Roast & Rest · Кофейня и обжарка', en: 'Roast & Rest · Café & roastery' }}
        description={{
          ru: 'Roast & Rest — маленькая обжарочная в центре. Кофе малыми партиями, медленные утра.',
          en: 'Roast & Rest — a small downtown roastery. Small-batch coffee, slow mornings.',
        }}
        path="/coffee"
        themeColor="#F6F1E7"
      />

      {/* Header */}
      <header className="sticky top-0 z-40 bg-coffee-cream/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-5 py-5 sm:px-8">
          <div className="flex items-center gap-2">
            <Bean width={22} height={22} className="text-coffee-accent" />
            <span className="font-sans text-sm font-semibold uppercase tracking-[0.2em]">{t.brand}</span>
          </div>
          <nav className="hidden items-center gap-8 font-sans text-sm md:flex" aria-label="Primary">
            {t.nav.map((n) => (
              <a key={n} href="#" className="text-coffee-ink/75 transition-colors hover:text-coffee-accent">
                {n}
              </a>
            ))}
          </nav>
          <div className="hidden items-center gap-5 md:flex">
            <LangToggle className="font-sans" activeClassName="text-coffee-ink" inactiveClassName="text-coffee-ink/35" />
            <a href="#book" className="font-sans text-sm font-semibold text-coffee-accent underline-offset-4 hover:underline">
              {t.heroCta}
            </a>
          </div>
          <button className="md:hidden" onClick={() => setMenuOpen((v) => !v)} aria-label="Menu" aria-expanded={menuOpen}>
            {menuOpen ? <Close /> : <Menu />}
          </button>
        </div>
        {menuOpen && (
          <div className="px-5 pb-5 md:hidden">
            <nav className="flex flex-col gap-3 font-sans text-sm" aria-label="Mobile">
              {t.nav.map((n) => (
                <a key={n} href="#" onClick={() => setMenuOpen(false)} className="text-coffee-ink/80">
                  {n}
                </a>
              ))}
            </nav>
            <div className="mt-4"><LangToggle className="font-sans" activeClassName="text-coffee-ink" inactiveClassName="text-coffee-ink/35" /></div>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-5xl px-5 pb-10 pt-8 sm:px-8 sm:pt-14">
        <p className="mb-8 font-sans text-xs uppercase tracking-[0.3em] text-coffee-accent">{t.heroKicker}</p>
        <div className="grid grid-cols-1 gap-10 md:grid-cols-12 md:items-end">
          <div className="md:col-span-7">
            <h1 className="text-[15vw] font-medium leading-[0.95] tracking-tight sm:text-7xl md:text-[5.5rem]">
              {t.heroTitleA}
              <br />
              <span className="italic text-coffee-accent">{t.heroTitleB}</span>
              <br />
              {t.heroTitleC}
            </h1>
            <p className="mt-8 max-w-md font-sans text-lg leading-relaxed text-coffee-ink/75">{t.heroLead}</p>
            <div className="mt-8 flex flex-wrap items-center gap-6 font-sans">
              <a
                href="#book"
                className="inline-flex items-center gap-2 rounded-full bg-coffee-accent px-7 py-3.5 text-sm font-semibold text-coffee-cream transition-transform hover:-translate-y-0.5"
              >
                {t.heroCta}
                <ArrowRight width={18} height={18} />
              </a>
              <a href="#menu" className="text-sm font-semibold text-coffee-ink underline decoration-coffee-accent decoration-1 underline-offset-4">
                {t.heroLink}
              </a>
            </div>
          </div>
          <div className="md:col-span-5">
            <Photo
              gradient="linear-gradient(150deg,#c98a5a 0%,#a9542c 45%,#5f2f1c 100%)"
              src={roastPhoto}
              caption={t.imageCaption1}
              ratio="aspect-[4/5]"
            />
          </div>
        </div>
      </section>

      {/* Intro / pull quote spread */}
      <section className="border-y border-coffee-ink/10">
        <div className="mx-auto max-w-5xl px-5 py-16 sm:px-8">
          <div className="grid gap-10 md:grid-cols-12">
            <Reveal className="md:col-span-7" as="div">
              <p className="text-3xl leading-snug sm:text-4xl">{t.introLead}</p>
            </Reveal>
            <Reveal className="md:col-span-4 md:col-start-9" delay={0.1} as="div">
              <p className="font-sans text-base leading-relaxed text-coffee-ink/70">{t.introBody}</p>
              <div className="mt-6 flex items-center gap-2 font-sans text-sm text-coffee-accent">
                <Clock width={18} height={18} />
                {t.hoursShort}
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      {/* Menu */}
      <section id="menu" className="mx-auto max-w-5xl px-5 py-16 sm:px-8">
        <div className="mb-10 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <h2 className="text-4xl tracking-tight sm:text-5xl">{t.menuTitle}</h2>
          <p className="max-w-xs font-sans text-sm text-coffee-muted">{t.menuNote}</p>
        </div>
        <ul className="divide-y divide-coffee-ink/10 border-y border-coffee-ink/10">
          {t.menu.map((item, i) => (
            <Reveal as="li" key={item.name} delay={i * 0.04}>
              <div className="flex items-baseline gap-4 py-5">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-baseline gap-x-3">
                    <h3 className="text-2xl">{item.name}</h3>
                    <span className="font-sans text-xs uppercase tracking-widest text-coffee-accent">{item.origin}</span>
                  </div>
                  <p className="mt-1 font-sans text-sm italic text-coffee-muted">{item.notes}</p>
                </div>
                <div className="shrink-0 font-sans text-lg font-semibold tabular-nums">
                  {item.price} <span className="text-sm text-coffee-muted">{t.priceUnit}</span>
                </div>
              </div>
            </Reveal>
          ))}
        </ul>
      </section>

      {/* Quote band */}
      <section className="bg-coffee-accent text-coffee-cream">
        <div className="mx-auto max-w-4xl px-5 py-20 text-center sm:px-8">
          <Leaf width={32} height={32} className="mx-auto mb-6 opacity-80" />
          <blockquote className="text-3xl leading-snug sm:text-5xl">{t.quote}</blockquote>
          <cite className="mt-6 block font-sans text-sm not-italic uppercase tracking-[0.2em] text-coffee-cream/70">{t.quoteAuthor}</cite>
        </div>
      </section>

      {/* Roasting process */}
      <section className="mx-auto max-w-5xl px-5 py-16 sm:px-8">
        <h2 className="mb-12 max-w-xl text-4xl tracking-tight sm:text-5xl">{t.roastTitle}</h2>
        <div className="grid gap-x-8 gap-y-10 sm:grid-cols-2 lg:grid-cols-4">
          {t.roastSteps.map((s, i) => (
            <Reveal key={s.n} delay={i * 0.06}>
              <div className="border-t border-coffee-ink/20 pt-5">
                <span className="font-sans text-sm font-semibold tracking-widest text-coffee-accent">{s.n}</span>
                <h3 className="mt-3 text-2xl">{s.t}</h3>
                <p className="mt-2 font-sans text-sm leading-relaxed text-coffee-ink/70">{s.d}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* The room */}
      <section className="border-t border-coffee-ink/10">
        <div className="mx-auto grid max-w-5xl gap-10 px-5 py-16 sm:px-8 md:grid-cols-12 md:items-center">
          <div className="md:col-span-6">
            <Photo gradient="linear-gradient(160deg,#e9d9bf 0%,#c69a6d 55%,#8a5a34 100%)" src={roomPhoto} caption={t.imageCaption2} ratio="aspect-[5/4]" />
          </div>
          <div className="md:col-span-5 md:col-start-8">
            <h2 className="text-4xl tracking-tight sm:text-5xl">{t.placeTitle}</h2>
            <p className="mt-5 font-sans text-lg leading-relaxed text-coffee-ink/75">{t.placeBody}</p>
            <dl className="mt-8 space-y-3 font-sans text-sm">
              <div className="flex items-center gap-3">
                <Leaf width={18} height={18} className="text-coffee-accent" />
                <dt className="sr-only">Address</dt>
                <dd>{t.placeAddress}</dd>
              </div>
              <div className="flex items-center gap-3">
                <Clock width={18} height={18} className="text-coffee-accent" />
                <dt className="sr-only">Hours</dt>
                <dd>{t.placeHours}</dd>
              </div>
            </dl>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="book" className="mx-auto max-w-5xl px-5 py-20 text-center sm:px-8">
        <h2 className="mx-auto max-w-2xl text-4xl leading-tight tracking-tight sm:text-6xl">{t.ctaTitle}</h2>
        <p className="mx-auto mt-6 max-w-md font-sans text-lg text-coffee-ink/70">{t.ctaLead}</p>
        <a
          href="#"
          className="mt-10 inline-flex items-center gap-2 rounded-full bg-coffee-ink px-8 py-4 font-sans text-sm font-semibold text-coffee-cream transition-transform hover:-translate-y-0.5"
        >
          {t.ctaButton}
          <ArrowRight width={18} height={18} />
        </a>
      </section>

      {/* Footer */}
      <footer className="border-t border-coffee-ink/10">
        <div className="mx-auto flex max-w-5xl flex-col gap-4 px-5 py-10 font-sans text-sm sm:flex-row sm:items-center sm:justify-between sm:px-8">
          <div className="flex items-center gap-2">
            <Bean width={18} height={18} className="text-coffee-accent" />
            <span className="font-semibold uppercase tracking-[0.2em]">{t.brand}</span>
          </div>
          <p className="max-w-sm text-xs text-coffee-muted">{t.footerNote}</p>
          <Link to="/" className="inline-flex items-center gap-1 text-xs font-semibold uppercase tracking-widest text-coffee-ink hover:text-coffee-accent">
            <ArrowRight width={14} height={14} className="rotate-180" />
            {t.backHub}
          </Link>
        </div>
      </footer>
    </div>
  )
}
