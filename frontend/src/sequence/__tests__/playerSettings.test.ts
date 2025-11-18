import { describe, it, expect, beforeEach } from 'vitest';
import {
  loadSequenceSettings,
  saveSequenceSettings,
  clearSequenceSettings,
} from '../playerSettings';

const STORAGE_KEY = 'hpz:v1:sequence-settings';

describe('playerSettings persistence', () => {
  beforeEach(() => {
    clearSequenceSettings();
    window.localStorage.removeItem(STORAGE_KEY);
  });

  it('saves and loads the last step direction', () => {
    expect(loadSequenceSettings()).toBeNull();
    saveSequenceSettings({ stepDirection: 'backward' });
    expect(loadSequenceSettings()).toEqual({ stepDirection: 'backward' });
  });

  it('returns null for malformed data', () => {
    window.localStorage.setItem(STORAGE_KEY, '{"stepDirection":"invalid"}');
    expect(loadSequenceSettings()).toBeNull();
    window.localStorage.setItem(STORAGE_KEY, '{bad json');
    expect(loadSequenceSettings()).toBeNull();
  });
});
