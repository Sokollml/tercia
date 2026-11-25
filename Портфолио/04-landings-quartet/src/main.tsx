import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, HashRouter, Routes, Route } from 'react-router-dom'
import { HelmetProvider } from 'react-helmet-async'
import { LanguageProvider } from './i18n/LanguageContext'
import ScrollToTop from './components/ScrollToTop'
import IndexPage from './pages/IndexPage'
import SaasLanding from './landings/saas/SaasLanding'
import CoffeeLanding from './landings/coffee/CoffeeLanding'
import AppLanding from './landings/app/AppLanding'
import CourseLanding from './landings/course/CourseLanding'
import NotFound from './pages/NotFound'
import './index.css'

// VITE_ROUTER=hash — для статического хостинга в подпапке (GitHub Pages): адреса вида /#/saas
const Router = import.meta.env.VITE_ROUTER === 'hash' ? HashRouter : BrowserRouter

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <HelmetProvider>
      <LanguageProvider>
        <Router>
          <ScrollToTop />
          <Routes>
            <Route path="/" element={<IndexPage />} />
            <Route path="/saas" element={<SaasLanding />} />
            <Route path="/coffee" element={<CoffeeLanding />} />
            <Route path="/app" element={<AppLanding />} />
            <Route path="/course" element={<CourseLanding />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Router>
      </LanguageProvider>
    </HelmetProvider>
  </React.StrictMode>,
)
