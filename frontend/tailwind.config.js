/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brutalist: {
          black: '#000000',
          white: '#FFFFFF',
          gray: '#808080',
          yellow: '#FFD700',
          blue: '#0000FF',
          red: '#FF0000',
          green: '#00FF00',
        }
      },
      fontFamily: {
        mono: ['Courier New', 'monospace'],
        sans: ['Arial', 'Helvetica', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
