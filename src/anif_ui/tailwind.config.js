/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#1e3a8a",
          950: "#172554",
        },
        // Semantic status tokens.
        // Foreground values must hold >= 4.5:1 (WCAG 1.4.3) on their paired
        // -bg tints AND on chrome-100 (the app shell background), including
        // through the Alert body's 90% opacity.
        status: {
          success: "#166534",
          "success-bg": "#f0fdf4",
          "success-border": "#bbf7d0",
          warning: "#92400e",
          "warning-bg": "#fffbeb",
          "warning-border": "#fde68a",
          danger: "#b91c1c",
          "danger-bg": "#fef2f2",
          "danger-border": "#fecaca",
          info: "#075985",
          "info-bg": "#f0f9ff",
          "info-border": "#bae6fd",
        },
        // Intent/ticket lifecycle states (same contrast rule as status)
        intent: {
          pending: "#4b5563",
          running: "#2563eb",
          success: "#166534",
          failed: "#b91c1c",
          blocked: "#9a3412",
          escalated: "#7c3aed",
          cancelled: "#52525b",
        },
        // Risk threshold bands (ANIF-304; same contrast rule as status)
        risk: {
          low: "#166534",
          "low-bg": "#f0fdf4",
          medium: "#92400e",
          "medium-bg": "#fffbeb",
          high: "#b91c1c",
          "high-bg": "#fef2f2",
        },
        // Sidebar / chrome
        chrome: {
          50: "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
          800: "#1e293b",
          900: "#0f172a",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "sans-serif",
        ],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "monospace"],
      },
      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "0.875rem" }],
      },
      boxShadow: {
        card: "0 1px 3px 0 rgb(0 0 0 / 0.08), 0 1px 2px -1px rgb(0 0 0 / 0.06)",
        "card-md": "0 4px 6px -1px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.06)",
      },
    },
  },
  plugins: [],
};
