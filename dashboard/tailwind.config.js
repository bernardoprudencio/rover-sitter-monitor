/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fff4ec',
          100: '#ffe3cf',
          200: '#ffc499',
          300: '#ffa564',
          400: '#ff8732',
          500: '#ff6b00',
          600: '#e25c00',
          700: '#b94800',
          800: '#8f3700',
          900: '#5e2400',
        },
        neutral: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        success: { 600: '#16a34a', 700: '#15803d' },
        warning: { 600: '#d97706' },
        danger: { 600: '#dc2626', 700: '#b91c1c' },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Inter', 'Roboto', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      fontSize: {
        h1: ['28px', { lineHeight: '34px', fontWeight: '700' }],
        h2: ['20px', { lineHeight: '26px', fontWeight: '600' }],
        h3: ['16px', { lineHeight: '22px', fontWeight: '600' }],
        body: ['14px', { lineHeight: '20px' }],
        caption: ['12px', { lineHeight: '16px' }],
      },
      boxShadow: {
        card: '0 1px 2px rgba(15,23,42,.04), 0 1px 3px rgba(15,23,42,.06)',
        'card-hover': '0 4px 6px rgba(15,23,42,.05), 0 10px 20px rgba(15,23,42,.08)',
        overlay: '0 20px 40px rgba(15,23,42,.18)',
      },
    },
  },
  plugins: [],
};
