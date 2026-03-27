/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sepia: {
          50:  '#f5f0e8',
          100: '#ede8df',
          200: '#ddd5c6',
          300: '#c9bca8',
          400: '#b09a80',
          500: '#8b6914',
          600: '#7a5c10',
          700: '#5c430c',
          800: '#3d2b1f',
          900: '#2a1c12',
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
