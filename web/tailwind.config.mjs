/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        sb: {
          canvas: '#090A0F',
          sidebar: '#0D0E12',
          card: '#121318',
          elevated: '#171920',
          border: '#252832',
          'border-focus': '#32B8F4',
          'text-primary': '#F4F5F7',
          'text-secondary': '#9299A8',
          'text-muted': '#626B7B',
          phosphor: '#18D69A',
          cyan: '#32B8F4',
          amber: '#E5A93C',
        },
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0284c7',
          600: '#0369a1',
          700: '#075985',
          800: '#0c4a6e',
          900: '#082f49',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'SF Mono', 'ui-monospace', 'monospace'],
        editorial: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
