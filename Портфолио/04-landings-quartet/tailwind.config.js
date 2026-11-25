/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'Helvetica', 'Arial', 'sans-serif'],
        serif: ['"Playfair Display"', 'Georgia', 'ui-serif', 'serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      colors: {
        swiss: {
          red: '#E4002B',
          ink: '#0A0A0A',
          paper: '#FFFFFF',
          grid: '#EDEDED',
        },
        coffee: {
          cream: '#F6F1E7',
          ink: '#2A2320',
          accent: '#B8552E',
          muted: '#8A7E70',
        },
        app: {
          bg: '#0B0D12',
          surface: '#151922',
          raised: '#1C212D',
          glow: '#5EE6B5',
          glow2: '#7C9BFF',
        },
        course: {
          bg: '#0E0E10',
          lime: '#D8FF3E',
          pink: '#FF4D8D',
          blue: '#2B5BFF',
        },
      },
    },
  },
  plugins: [],
}
