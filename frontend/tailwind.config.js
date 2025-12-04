import defaultTheme from "tailwindcss/defaultTheme";

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Outfit"', ...defaultTheme.fontFamily.sans],
      },
      colors: {
        accent: "#2563eb",
        surface: {
          dark: "#0a0a0a",
          dim: "#121212",
          light: "#eff6ff",
        },
      },
      boxShadow: {
        soft: "0 10px 40px rgba(0,0,0,0.25)",
      },
      keyframes: {
        "fade-slide": {
          "0%": { opacity: 0, transform: "translateY(12px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-slide": "fade-slide 450ms ease-out",
      },
    },
  },
  plugins: [],
};
