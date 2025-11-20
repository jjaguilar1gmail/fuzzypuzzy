const colorVar = (token) => ({ opacityValue } = {}) =>
  opacityValue === undefined
    ? `rgb(var(${token}))`
    : `rgb(var(${token}) / ${opacityValue})`;

const palette = (baseToken, variants = {}) => {
  const entries = Object.entries(variants).reduce(
    (acc, [key, token]) => ({ ...acc, [key]: colorVar(token) }),
    {}
  );
  return {
    DEFAULT: colorVar(baseToken),
    ...entries,
  };
};

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class', '[data-theme="dark"]'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: palette('--color-primary', {
          foreground: '--color-primary-foreground',
          muted: '--color-primary-muted',
          strong: '--color-primary-strong',
        }),
        surface: palette('--color-surface', {
          muted: '--color-surface-muted',
          elevated: '--color-surface-elevated',
          inverse: '--color-surface-inverse',
        }),
        disabled: palette('--color-disabled-bg', {
          border: '--color-disabled-border',
          text: '--color-disabled-text',
        }),
        border: colorVar('--color-border'),
        copy: colorVar('--color-text'),
        'copy-muted': colorVar('--color-text-muted'),
        success: palette('--color-success', {
          muted: '--color-success-muted',
        }),
        danger: palette('--color-danger', {
          muted: '--color-danger-muted',
        }),
        warning: colorVar('--color-warning'),
        info: colorVar('--color-info'),
        'grid-anchor': colorVar('--color-grid-anchor'),
        'grid-anchor-stroke': colorVar('--color-grid-anchor-stroke'),
        'grid-given': colorVar('--color-grid-given'),
        'grid-selected': colorVar('--color-grid-selected'),
        'grid-path': colorVar('--color-grid-path'),
        'grid-target': colorVar('--color-grid-target'),
        'grid-mistake-fill': colorVar('--color-grid-mistake-fill'),
        'grid-mistake-stroke': colorVar('--color-grid-mistake-stroke'),
      },
      animation: {
        'fade-in': 'fadeIn 150ms ease-in',
        'scale-in': 'scaleIn 150ms ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
