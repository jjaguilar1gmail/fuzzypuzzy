import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import { useEffect } from 'react';
import { useSettingsStore } from '@/state/settingsStore';

function useViewportHeightVariable() {
  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const root = document.documentElement;
    const setViewportHeight = () => {
      const viewportHeight =
        window.visualViewport?.height ?? window.innerHeight ?? 0;
      root.style.setProperty(
        '--app-viewport-height',
        `${Math.round(viewportHeight)}px`
      );
    };

    setViewportHeight();

    window.addEventListener('resize', setViewportHeight);
    window.addEventListener('orientationchange', setViewportHeight);

    const visualViewport = window.visualViewport;
    visualViewport?.addEventListener('resize', setViewportHeight);

    return () => {
      window.removeEventListener('resize', setViewportHeight);
      window.removeEventListener('orientationchange', setViewportHeight);
      visualViewport?.removeEventListener('resize', setViewportHeight);
    };
  }, []);
}

function useThemePreference() {
  const theme = useSettingsStore((state) => state.theme);

  useEffect(() => {
    if (typeof document === 'undefined') {
      return;
    }

    const root = document.documentElement;
    const media = window.matchMedia('(prefers-color-scheme: dark)');

    const applyTheme = () => {
      const resolved =
        theme === 'system' ? (media.matches ? 'dark' : 'light') : theme;
      root.dataset.theme = resolved;
    };

    applyTheme();

    if (theme === 'system') {
      media.addEventListener('change', applyTheme);
      return () => media.removeEventListener('change', applyTheme);
    }
  }, [theme]);
}

export default function App({ Component, pageProps }: AppProps) {
  useViewportHeightVariable();
  useThemePreference();
  return <Component {...pageProps} />;
}
