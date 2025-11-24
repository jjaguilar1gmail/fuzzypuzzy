export const cssVar = (token: string, alpha?: number): string => {
  if (alpha !== undefined) {
    return `rgb(var(${token}) / ${alpha})`;
  }
  return `rgb(var(${token}))`;
};

export const gridPalette = {
  cellSurface: cssVar('--color-grid-path'),
  given: cssVar('--color-grid-given'),
  selected: cssVar('--color-grid-selected'),
  target: cssVar('--color-grid-target'),
  anchorFill: cssVar('--color-grid-anchor'),
  anchorStroke: cssVar('--color-grid-anchor-stroke'),
  mistakeFill: cssVar('--color-grid-mistake-fill'),
  mistakeStroke: cssVar('--color-grid-mistake-stroke'),
  holdStroke: cssVar('--color-grid-hold-stroke'),
};

export const statusPalette = {
  primary: cssVar('--color-primary'),
  primaryForeground: cssVar('--color-primary-foreground'),
  primaryMuted: cssVar('--color-primary-muted'),
  success: cssVar('--color-success'),
  successMuted: cssVar('--color-success-muted'),
  danger: cssVar('--color-danger'),
  dangerMuted: cssVar('--color-danger-muted'),
  warning: cssVar('--color-warning'),
  text: cssVar('--color-text'),
  textMuted: cssVar('--color-text-muted'),
  border: cssVar('--color-border'),
};

export const paletteB = [
  cssVar('--color-symbol-b0'),
  cssVar('--color-symbol-b1'),
  cssVar('--color-symbol-b2'),
  cssVar('--color-symbol-b3'),
  cssVar('--color-symbol-b4'),
];

export const symbolAccent = {
  anchorHighlight: cssVar('--color-symbol-anchor-highlight'),
  anchorHighlightStroke: cssVar('--color-symbol-anchor-highlight-stroke'),
};
