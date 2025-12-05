export type PipPosition = {
  x: number;
  y: number;
};

const pipAnchors = {
  left: 0.3,
  center: 0.5,
  right: 0.7,
  top: 0.3,
  middle: 0.5,
  bottom: 0.7,
};

const STANDARD_PIP_LAYOUTS: Record<number, PipPosition[]> = {
  1: [{ x: pipAnchors.center, y: pipAnchors.middle }],
  2: [
    { x: pipAnchors.left, y: pipAnchors.top },
    { x: pipAnchors.right, y: pipAnchors.bottom },
  ],
  3: [
    { x: pipAnchors.left, y: pipAnchors.top },
    { x: pipAnchors.center, y: pipAnchors.middle },
    { x: pipAnchors.right, y: pipAnchors.bottom },
  ],
  4: [
    { x: pipAnchors.left, y: pipAnchors.top },
    { x: pipAnchors.right, y: pipAnchors.top },
    { x: pipAnchors.left, y: pipAnchors.bottom },
    { x: pipAnchors.right, y: pipAnchors.bottom },
  ],
  5: [
    { x: pipAnchors.left, y: pipAnchors.top },
    { x: pipAnchors.right, y: pipAnchors.top },
    { x: pipAnchors.center, y: pipAnchors.middle },
    { x: pipAnchors.left, y: pipAnchors.bottom },
    { x: pipAnchors.right, y: pipAnchors.bottom },
  ],
  6: [
    { x: pipAnchors.left, y: pipAnchors.top },
    { x: pipAnchors.right, y: pipAnchors.top },
    { x: pipAnchors.left, y: pipAnchors.middle },
    { x: pipAnchors.right, y: pipAnchors.middle },
    { x: pipAnchors.left, y: pipAnchors.bottom },
    { x: pipAnchors.right, y: pipAnchors.bottom },
  ],
};

const createRadialLayout = (count: number): PipPosition[] => {
  if (count <= 0) {
    return [];
  }

  const positions: PipPosition[] = [];
  let remaining = count;
  const shouldIncludeCenter = count % 2 === 1;

  if (shouldIncludeCenter) {
    positions.push({ x: pipAnchors.center, y: pipAnchors.middle });
    remaining -= 1;
  }

  if (remaining === 0) {
    return positions;
  }

  const radius = 0.35;
  for (let i = 0; i < remaining; i++) {
    const angle = (2 * Math.PI * i) / remaining - Math.PI / 2;
    positions.push({
      x: pipAnchors.center + radius * Math.cos(angle),
      y: pipAnchors.middle + radius * Math.sin(angle),
    });
  }

  return positions;
};

export const getPipLayout = (count: number): PipPosition[] => {
  if (STANDARD_PIP_LAYOUTS[count]) {
    return STANDARD_PIP_LAYOUTS[count];
  }
  return createRadialLayout(count);
};
