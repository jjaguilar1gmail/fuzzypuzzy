import type { SequenceDirection } from './types';

const SETTINGS_STORAGE_KEY = 'hpz:v1:sequence-settings';

export interface SequenceSettings {
  stepDirection: SequenceDirection;
}

function getStorage(): Storage | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    return window.localStorage ?? null;
  } catch {
    return null;
  }
}

export function loadSequenceSettings(): SequenceSettings | null {
  const storage = getStorage();
  if (!storage) {
    return null;
  }

  try {
    const raw = storage.getItem(SETTINGS_STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw);
    if (
      parsed &&
      (parsed.stepDirection === 'forward' || parsed.stepDirection === 'backward')
    ) {
      return { stepDirection: parsed.stepDirection };
    }
  } catch {
    return null;
  }

  return null;
}

export function saveSequenceSettings(settings: SequenceSettings): void {
  const storage = getStorage();
  if (!storage) {
    return;
  }

  try {
    storage.setItem(
      SETTINGS_STORAGE_KEY,
      JSON.stringify(settings)
    );
  } catch {
    // Swallow errors – persistence is best-effort.
  }
}

export function clearSequenceSettings(): void {
  const storage = getStorage();
  if (!storage) {
    return;
  }
  try {
    storage.removeItem(SETTINGS_STORAGE_KEY);
  } catch {
    // Ignore
  }
}
