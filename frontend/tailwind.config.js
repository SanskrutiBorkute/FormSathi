/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: '#F7F3ED',
        'paper-dark': '#EFE9E0',
        'paper-darker': '#E5DDD1',
        teal: '#0D5C63',
        'teal-dark': '#0A4A50',
        'teal-light': '#E3F2F3',
        'teal-medium': '#1A7A83',
        saffron: '#F4A024',
        'saffron-light': '#FEF5E7',
        'saffron-dark': '#D4841A',
        ink: '#1A1208',
        'ink-medium': '#4A3F30',
        'ink-light': '#8A7D6A',
        'ink-pale': '#C4B8A8',
        red: '#C0392B',
        'red-light': '#FDECEA',
        green: '#1E7B3A',
        'green-light': '#EBF7EE',
      },
      fontFamily: {
        sans: ['"DM Sans"', 'sans-serif'],
        serif: ['Fraunces', 'serif'],
        mono: ['"DM Mono"', 'monospace'],
      },
      boxShadow: {
        'sm-custom': '0 1px 3px rgba(26,18,8,0.08)',
        'custom': '0 3px 14px rgba(26,18,8,0.10)',
        'lg-custom': '0 8px 32px rgba(26,18,8,0.14)',
      }
    },
  },
  plugins: [],
}
