/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,html}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        slate: {
          850: "#151e2e",
          950: "#0b0f17",
        },
        primary: {
          DEFAULT: "#7c3aed",
          light: "#a78bfa",
          dark: "#6d28d9",
        },
      },
    },
  },
  plugins: [],
};
