/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0a0c12',
          800: '#0f1117',
          700: '#1a1d27',
          600: '#252836',
          500: '#2d3147',
        },
        accent: {
          DEFAULT: '#00d4ff',
          dim: '#0099bb',
        },
        purple: { zna: '#7c3aed' },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
