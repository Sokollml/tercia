import { useEffect, useRef, useState } from 'react'
import { useReducedMotion } from 'framer-motion'

/** Counts from 0 to `to` when scrolled into view. Preserves a leading sign. */
export default function CountUp({ to, duration = 1400 }: { to: string; duration?: number }) {
  const reduce = useReducedMotion()
  const sign = to.trim().startsWith('+') ? '+' : ''
  const target = parseInt(to.replace(/[^0-9]/g, ''), 10) || 0
  const [value, setValue] = useState(reduce ? target : 0)
  const ref = useRef<HTMLSpanElement>(null)
  const started = useRef(false)

  useEffect(() => {
    if (reduce) return
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !started.current) {
          started.current = true
          const start = performance.now()
          const tick = (now: number) => {
            const p = Math.min((now - start) / duration, 1)
            const eased = 1 - Math.pow(1 - p, 3)
            setValue(Math.round(eased * target))
            if (p < 1) requestAnimationFrame(tick)
          }
          requestAnimationFrame(tick)
        }
      },
      { threshold: 0.4 },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [target, duration, reduce])

  return (
    <span ref={ref}>
      {sign}
      {value}
    </span>
  )
}
