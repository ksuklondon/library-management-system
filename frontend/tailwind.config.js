/**
 * Tailwind CSS configuration.
 *
 * Zgodność z wymaganiami:
 * - NF10: Responsywny design
 * - NF11: Dark mode support
 */

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class", // Enable dark mode with class strategy (NF11)
  theme: {
    extend: {
      colors: {
        // Custom color palette
        primary: {
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
      },
      fontFamily: {
        // Custom fonts
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["Fira Code", "monospace"],
      },
      spacing: {
        // Custom spacing
        128: "32rem",
        144: "36rem",
      },
      borderRadius: {
        // Custom border radius
        "4xl": "2rem",
      },
      boxShadow: {
        // Custom shadows
        "inner-lg": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.1)",
      },
      animation: {
        // Custom animations
        "fade-in": "fadeIn 0.3s ease-in",
        "slide-up": "slideUp 0.3s ease-out",
        "slide-down": "slideDown 0.3s ease-out",
        "spin-slow": "spin 3s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        slideDown: {
          "0%": { transform: "translateY(-10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
      },
      screens: {
        // Custom breakpoints (NF10)
        xs: "475px",
        "3xl": "1920px",
      },
      maxWidth: {
        // Custom max widths
        "8xl": "88rem",
        "9xl": "96rem",
      },
    },
  },
  plugins: [
    // Add official Tailwind plugins if needed
    // require('@tailwindcss/forms'),
    // require('@tailwindcss/typography'),
    // require('@tailwindcss/aspect-ratio'),
  ],
};
