import type { SVGProps } from 'react'

/**
 * Inline stroke icons used across the landings — no emoji, no icon fonts.
 * All inherit `currentColor` and accept standard SVG props.
 */
type IconProps = SVGProps<SVGSVGElement>

const base = (props: IconProps) => ({
  width: 24,
  height: 24,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.75,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  'aria-hidden': true,
  ...props,
})

export const ArrowRight = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M5 12h14" />
    <path d="m13 5 7 7-7 7" />
  </svg>
)

export const ArrowUpRight = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M7 17 17 7" />
    <path d="M8 7h9v9" />
  </svg>
)

export const ChartBar = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M3 3v18h18" />
    <rect x="7" y="11" width="3" height="6" />
    <rect x="12" y="7" width="3" height="10" />
    <rect x="17" y="13" width="3" height="4" />
  </svg>
)

export const Bolt = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M13 2 4 14h7l-1 8 9-12h-7z" />
  </svg>
)

export const Layers = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="m12 3 9 5-9 5-9-5 9-5Z" />
    <path d="m3 13 9 5 9-5" />
  </svg>
)

export const Shield = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M12 3 5 6v6c0 4 3 6.5 7 8 4-1.5 7-4 7-8V6l-7-3Z" />
    <path d="m9 12 2 2 4-4" />
  </svg>
)

export const Globe = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="12" cy="12" r="9" />
    <path d="M3 12h18" />
    <path d="M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18" />
  </svg>
)

export const Bean = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M6 18C3 15 3 8 8 5s10-1 11 3-1 9-6 11-6 1-7-1Z" />
    <path d="M8.5 15.5c2-1 3.5-3 4-6" />
  </svg>
)

export const Clock = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5l3 2" />
  </svg>
)

export const Leaf = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M4 20c0-8 6-14 16-14 0 10-6 16-16 14Z" />
    <path d="M4 20c4-6 8-8 12-9" />
  </svg>
)

export const Heart = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M12 20s-7-4.5-9-9c-1.5-3.5 1-6.5 4-6.5 2 0 3.5 1.5 5 3.5 1.5-2 3-3.5 5-3.5 3 0 5.5 3 4 6.5-2 4.5-9 9-9 9Z" />
  </svg>
)

export const Bell = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" />
    <path d="M10 20a2 2 0 0 0 4 0" />
  </svg>
)

export const Sparkle = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M12 3v6M12 15v6M3 12h6M15 12h6" />
    <path d="m6 6 3 3M15 15l3 3M18 6l-3 3M9 15l-3 3" />
  </svg>
)

export const Wallet = (p: IconProps) => (
  <svg {...base(p)}>
    <rect x="3" y="6" width="18" height="13" rx="2" />
    <path d="M3 9h18" />
    <circle cx="16" cy="14" r="1.4" />
  </svg>
)

export const Lock = (p: IconProps) => (
  <svg {...base(p)}>
    <rect x="4" y="10" width="16" height="10" rx="2" />
    <path d="M8 10V7a4 4 0 0 1 8 0v3" />
  </svg>
)

export const Play = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="m8 5 12 7-12 7V5Z" />
  </svg>
)

export const Check = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="m5 12 5 5 9-11" />
  </svg>
)

export const Cup = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M4 8h13v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5V8Z" />
    <path d="M17 9h2a2 2 0 0 1 0 4h-2" />
    <path d="M8 3c-.5 1 .5 2 0 3M12 3c-.5 1 .5 2 0 3" />
  </svg>
)

export const Users = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="9" cy="8" r="3" />
    <path d="M3 20c0-3 3-5 6-5s6 2 6 5" />
    <path d="M16 6a3 3 0 0 1 0 6M21 20c0-2.5-1.5-4-4-4.5" />
  </svg>
)

export const Target = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="12" cy="12" r="9" />
    <circle cx="12" cy="12" r="5" />
    <circle cx="12" cy="12" r="1.4" />
  </svg>
)

export const Certificate = (p: IconProps) => (
  <svg {...base(p)}>
    <rect x="3" y="4" width="18" height="12" rx="2" />
    <circle cx="12" cy="10" r="2.5" />
    <path d="m9.5 15-1 5 3.5-2 3.5 2-1-5" />
  </svg>
)

export const Menu = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M3 6h18M3 12h18M3 18h18" />
  </svg>
)

export const Close = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M6 6l12 12M18 6 6 18" />
  </svg>
)

export const Phone = (p: IconProps) => (
  <svg {...base(p)}>
    <rect x="7" y="2" width="10" height="20" rx="2.5" />
    <path d="M11 18h2" />
  </svg>
)
