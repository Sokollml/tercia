import { Helmet } from 'react-helmet-async'
import { useLang } from '../i18n/LanguageContext'

interface SeoProps {
  title: { ru: string; en: string }
  description: { ru: string; en: string }
  path: string
  themeColor?: string
  ogType?: string
}

const SITE = 'Landings Quartet'

/** Per-route meta + Open Graph / Twitter tags, language-aware. */
export default function Seo({ title, description, path, themeColor = '#0A0A0A', ogType = 'website' }: SeoProps) {
  const { lang } = useLang()
  const t = title[lang]
  const d = description[lang]
  const fullTitle = `${t} — ${SITE}`
  const url = `https://landings-quartet.vercel.app${path}`

  return (
    <Helmet>
      <html lang={lang} />
      <title>{fullTitle}</title>
      <meta name="description" content={d} />
      <meta name="theme-color" content={themeColor} />
      <link rel="canonical" href={url} />

      <meta property="og:type" content={ogType} />
      <meta property="og:site_name" content={SITE} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={d} />
      <meta property="og:url" content={url} />
      <meta property="og:locale" content={lang === 'ru' ? 'ru_RU' : 'en_US'} />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={d} />
    </Helmet>
  )
}
