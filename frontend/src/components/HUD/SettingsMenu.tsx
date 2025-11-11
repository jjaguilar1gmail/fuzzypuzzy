import { motion } from 'framer-motion';
import { useSettingsStore } from '@/state/settingsStore';
import { useState } from 'react';

export default function SettingsMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const theme = useSettingsStore((state) => state.theme);
  const soundEnabled = useSettingsStore((state) => state.soundEnabled);
  const pencilModeDefault = useSettingsStore((state) => state.pencilModeDefault);
  const setTheme = useSettingsStore((state) => state.setTheme);
  const toggleSound = useSettingsStore((state) => state.toggleSound);
  const togglePencilModeDefault = useSettingsStore((state) => state.togglePencilModeDefault);

  return (
    <div className="relative">
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-lg bg-gray-200 hover:bg-gray-300 transition-colors"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        aria-label="Settings"
        aria-expanded={isOpen}
      >
        ⚙️
      </motion.button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Settings dropdown */}
          <motion.div
            className="absolute right-0 mt-2 w-72 bg-white rounded-lg shadow-xl border border-gray-200 p-4 z-20"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.15 }}
            role="menu"
            aria-label="Settings menu"
          >
            <h3 className="text-lg font-semibold mb-4">Settings</h3>

            <div className="space-y-4">
              {/* Theme */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Theme
                </label>
                <div className="flex gap-2">
                  {(['light', 'dark', 'system'] as const).map((t) => (
                    <button
                      key={t}
                      onClick={() => setTheme(t)}
                      className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        theme === t
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {t.charAt(0).toUpperCase() + t.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Sound */}
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700">
                  Sound Effects
                </label>
                <button
                  onClick={toggleSound}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    soundEnabled ? 'bg-blue-500' : 'bg-gray-300'
                  }`}
                  role="switch"
                  aria-checked={soundEnabled}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      soundEnabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              {/* Pencil mode default */}
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-gray-700">
                  Start with Pencil Mode
                </label>
                <button
                  onClick={togglePencilModeDefault}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    pencilModeDefault ? 'bg-blue-500' : 'bg-gray-300'
                  }`}
                  role="switch"
                  aria-checked={pencilModeDefault}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      pencilModeDefault ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </div>
  );
}
