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
        // Semantic status tokens
        status: {
          success: "#16a34a",
          "success-bg": "#f0fdf4",
          "success-border": "#bbf7d0",
          warning: "#d97706",
          "warning-bg": "#fffbeb",
          "warning-border": "#fde68a",
          danger: "#dc2626",
          "danger-bg": "#fef2f2",
          "danger-border": "#fecaca",
          info: "#0284c7",
          "info-bg": "#f0f9ff",
          "info-border": "#bae6fd",
        },
        // Intent/ticket lifecycle states
        intent: {
          pending: "#6b7280",
          running: "#2563eb",
          success: "#16a34a",
          failed: "#dc2626",
          blocked: "#ea580c",
          escalated: "#7c3aed",
          cancelled: "#9ca3af",
        },
        // Risk threshold bands (ANIF-304)
        risk: {
          low: "#16a34a",
          "low-bg": "#f0fdf4",
          medium: "#d97706",
          "medium-bg": "#fffbeb",
          high: "#dc2626",
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
