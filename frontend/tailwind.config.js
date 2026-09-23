/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // CAT brand yellow
        cat: {
          50:  '#fffde7',
          100: '#fff9c4',
          200: '#fff176',
          300: '#ffee58',
          400: '#ffca28',
          500: '#FFCD11', // CAT primary yellow
          600: '#e6b800',
          700: '#c49a00',
          800: '#9a7800',
          900: '#6b5400',
        },
        // Dark industrial background
        surface: {
          900: '#0a0c10',
          800: '#10131a',
          700: '#161b24',
          600: '#1c2230',
          500: '#232b3a',
          400: '#2c3547',
          300: '#384055',
          200: '#4a5568',
          100: '#718096',
        },
        status: {
          normal:   '#22c55e',
          caution:  '#f59e0b',
          critical: '#ef4444',
          info:     '#3b82f6',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
