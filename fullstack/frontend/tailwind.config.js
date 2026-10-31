/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "IBM Plex Sans",
          "ui-sans-serif",
          "system-ui",
          "Segoe UI",
          "sans-serif",
        ],
        mono: [
          "IBM Plex Mono",
          "ui-monospace",
          "SFMono-Regular",
          "Consolas",
          "monospace",
        ],
      },
      colors: {
        canvas: "#f5f4ef",
        surface: "#ffffff",
        "surface-muted": "#faf9f6",
        line: "#dedbd2",
        "line-strong": "#c9c5ba",
        ink: "#1c2523",
        "ink-soft": "#34423f",
        muted: "#67736f",
        brand: {
          50: "#edf7f4",
          100: "#d5eee7",
          200: "#aeddd1",
          300: "#7bc4b3",
          400: "#45a593",
          500: "#238578",
          600: "#146a60",
          700: "#12554f",
          800: "#12443f",
          900: "#113936",
        },
      },
      boxShadow: {
        card: "0 1px 2px rgba(28, 37, 35, 0.04), 0 18px 40px -32px rgba(28, 37, 35, 0.35)",
        lift: "0 1px 2px rgba(28, 37, 35, 0.05), 0 24px 50px -36px rgba(28, 37, 35, 0.45)",
      },
    },
  },
  plugins: [],
};
