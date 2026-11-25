import { Link } from 'react-router-dom'
import { useLang } from '../i18n/LanguageContext'
import Seo from '../components/Seo'
import { ArrowRight } from '../components/icons'

export default function NotFound() {
  const { lang } = useLang()
  const t = {
    ru: { title: 'Страница не найдена', lead: 'Такого маршрута здесь нет. Вернитесь на главную к четырём лендингам.', back: 'На главную' },
    en: { title: 'Page not found', lead: 'This route does not exist. Head back to the four landings.', back: 'Back home' },
  }[lang]
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#0c0c0d] px-6 text-center text-white">
      <Seo title={{ ru: '404', en: '404' }} description={{ ru: t.lead, en: t.lead }} path="/404" themeColor="#0c0c0d" />
      <p className="font-mono text-7xl font-black tracking-tighter text-white/15">404</p>
      <h1 className="mt-4 text-2xl font-bold">{t.title}</h1>
      <p className="mt-3 max-w-sm text-white/55">{t.lead}</p>
      <Link
        to="/"
        className="mt-8 inline-flex items-center gap-2 rounded-full bg-white px-6 py-3 text-sm font-semibold text-black transition-transform hover:-translate-y-0.5"
      >
        {t.back}
        <ArrowRight width={18} height={18} />
      </Link>
    </div>
  )
}
