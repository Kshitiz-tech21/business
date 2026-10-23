/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f5f7ff',
          100: '#ebf0fe',
          200: '#ced9fd',
          300: '#a1b8f9',
          400: '#6b8df5',
          500: '#3b62e9',
          600: '#2a4dcb',
          700: '#223da8',
          800: '#1d338b',
          900: '#182b75',
        },
      },
    },
  },
  plugins: [],
}