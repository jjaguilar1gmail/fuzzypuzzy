import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import { useEffect } from 'react';

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

export default function App({ Component, pageProps }: AppProps) {
  useViewportHeightVariable();
  return <Component {...pageProps} />;
}
