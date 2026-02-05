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
        // Colores de marca FDM
        'fdm-red': '#C41E3A',
        'fdm-red-dark': '#9B1830',
        'fdm-blue': '#1E4380',
        'fdm-blue-dark': '#142D5A',
      },
    },
  },
  plugins: [],
}
