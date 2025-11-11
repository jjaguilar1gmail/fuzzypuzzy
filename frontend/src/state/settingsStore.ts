import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SettingsState {
  theme: 'light' | 'dark' | 'system';
  soundEnabled: boolean;
  pencilModeDefault: boolean;
  
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  toggleSound: () => void;
  togglePencilModeDefault: () => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: 'system',
      soundEnabled: true,
      pencilModeDefault: false,

      setTheme: (theme) => set({ theme }),
      toggleSound: () => set((state) => ({ soundEnabled: !state.soundEnabled })),
      togglePencilModeDefault: () =>
        set((state) => ({ pencilModeDefault: !state.pencilModeDefault })),
    }),
    {
      name: 'hpz-settings',
    }
  )
);
