/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyberpunk: {
          purple: '#6B46C1',
          indigo: '#4F46E5',
          pink: '#EC4899',
          cyan: '#06B6D4',
          dark: '#1E1B4B',
          darker: '#0F0E2E',
        },
      },
      boxShadow: {
        'neon-pink': '0 0 20px rgba(236, 72, 153, 0.6), 0 0 40px rgba(236, 72, 153, 0.4)',
        'neon-cyan': '0 0 20px rgba(6, 182, 212, 0.6), 0 0 40px rgba(6, 182, 212, 0.4)',
        'neon-purple': '0 0 20px rgba(107, 70, 193, 0.6), 0 0 40px rgba(107, 70, 193, 0.4)',
        'neon-intense': '0 0 30px rgba(236, 72, 153, 0.8), 0 0 60px rgba(236, 72, 153, 0.6), 0 0 90px rgba(236, 72, 153, 0.4)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}



