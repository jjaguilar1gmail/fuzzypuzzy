import { motion } from 'framer-motion';
import { useSettingsStore } from '@/state/settingsStore';
import { useState } from 'react';

export default function SettingsMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const theme = useSettingsStore((state) => state.theme);
  const setTheme = useSettingsStore((state) => state.setTheme);

  return (
    <div className="relative">
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="p-3 min-w-[44px] min-h-[44px] rounded-lg bg-gray-200 hover:bg-gray-300 transition-colors flex items-center justify-center"
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
                      className={`flex-1 px-3 py-3 min-h-[44px] rounded-lg text-sm font-medium transition-colors ${
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

            </div>
          </motion.div>
        </>
      )}
    </div>
  );
}
