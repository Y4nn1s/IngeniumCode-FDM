/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#2563eb', // Blue-600
        'danger': '#dc2626',  // Red-600
        'navy': '#1e3a8a',    // Blue-900
      },
    },
  },
  plugins: [],
}
