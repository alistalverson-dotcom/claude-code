/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Wrestling-inspired color palette
        'wwe-red': '#e50914',
        'gold': '#ffd700',
      },
      fontFamily: {
        'bebas': ['Bebas Neue', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
