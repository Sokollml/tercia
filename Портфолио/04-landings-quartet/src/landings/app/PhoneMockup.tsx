import { motion } from 'framer-motion'
import { Wallet, Sparkle, ArrowUpRight } from '../../components/icons'
import type { appContent } from './content'

type Phone = (typeof appContent)[keyof typeof appContent]['phone']

const toneMap: Record<string, string> = {
  glow: '#5EE6B5',
  blue: '#7C9BFF',
  muted: '#8892a6',
}

/** Pure-CSS phone mockup with a soft, layered UI (depth via shadow + glow). */
export default function PhoneMockup({ phone }: { phone: Phone }) {
  return (
    <div className="relative mx-auto w-full max-w-[300px]">
      {/* ambient glow behind the device */}
      <div className="pointer-events-none absolute -inset-10 -z-10 rounded-full bg-app-glow/20 blur-3xl" aria-hidden="true" />
      <div
        className="relative rounded-[2.6rem] border border-white/10 p-2.5"
        style={{
          background: 'linear-gradient(160deg,#20242f,#0d1017)',
          boxShadow: '0 40px 80px -30px rgba(0,0,0,0.9), 0 0 0 1px rgba(255,255,255,0.04), inset 0 1px 0 rgba(255,255,255,0.08)',
        }}
      >
        {/* screen */}
        <div className="relative overflow-hidden rounded-[2.1rem] bg-app-bg px-5 pb-6 pt-8" style={{ boxShadow: 'inset 0 0 30px rgba(0,0,0,0.6)' }}>
          {/* notch */}
          <div className="absolute left-1/2 top-2.5 h-1.5 w-16 -translate-x-1/2 rounded-full bg-white/15" aria-hidden="true" />

          <p className="mt-2 text-sm text-white/50">{phone.greeting}</p>

          {/* balance card */}
          <div
            className="mt-4 rounded-2xl p-5"
            style={{
              background: 'linear-gradient(155deg,#1d2431,#141824)',
              boxShadow: '0 18px 30px -18px rgba(94,230,181,0.35), inset 0 1px 0 rgba(255,255,255,0.06)',
            }}
          >
            <div className="flex items-center gap-2 text-xs text-white/45">
              <Wallet width={15} height={15} className="text-app-glow" />
              {phone.balanceLabel}
            </div>
            <div className="mt-1.5 text-3xl font-bold tracking-tight text-white">{phone.balance}</div>
            <div className="mt-1 text-xs font-medium text-app-glow">{phone.trend}</div>
          </div>

          {/* categories */}
          <div className="mt-4 space-y-3">
            {phone.categories.map((c, i) => (
              <div key={c.label}>
                <div className="mb-1.5 flex items-center justify-between text-xs">
                  <span className="text-white/70">{c.label}</span>
                  <span className="font-semibold text-white/90">{c.value}</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-white/[0.06]">
                  <motion.div
                    className="h-full rounded-full"
                    style={{ background: toneMap[c.tone], boxShadow: `0 0 12px ${toneMap[c.tone]}80` }}
                    initial={{ width: 0 }}
                    whileInView={{ width: `${c.pct}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.9, delay: 0.2 + i * 0.12, ease: [0.22, 1, 0.36, 1] }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* insight pill */}
          <div
            className="mt-5 flex items-start gap-2.5 rounded-xl p-3.5"
            style={{ background: 'linear-gradient(160deg,#1a2130,#12161f)', boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.05)' }}
          >
            <Sparkle width={18} height={18} className="mt-0.5 shrink-0 text-app-glow2" />
            <p className="text-xs leading-relaxed text-white/70">{phone.insight}</p>
          </div>

          {/* tactile action button */}
          <button
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold text-app-bg transition-transform active:translate-y-px"
            style={{
              background: 'linear-gradient(180deg,#7bf0c5,#3fcfa0)',
              boxShadow: '0 12px 24px -10px rgba(94,230,181,0.6), inset 0 1px 0 rgba(255,255,255,0.5)',
            }}
          >
            {phone.action}
            <ArrowUpRight width={16} height={16} />
          </button>
        </div>
      </div>
    </div>
  )
}
