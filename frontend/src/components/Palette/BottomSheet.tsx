import { ReactNode, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface BottomSheetProps {
  children: ReactNode;
  defaultOpen?: boolean;
  className?: string;
}

/**
 * BottomSheet component for mobile palette interaction (US4).
 * Provides a slide-up panel for touch-friendly number input on mobile devices.
 */
export default function BottomSheet({
  children,
  defaultOpen = false,
  className = '',
}: BottomSheetProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const toggleSheet = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Toggle button (visible on mobile) */}
      <button
        onClick={toggleSheet}
        className="fixed bottom-4 right-4 z-40 md:hidden w-14 h-14 rounded-full bg-primary text-white shadow-lg flex items-center justify-center"
        aria-label={isOpen ? 'Close palette' : 'Open palette'}
        aria-expanded={isOpen}
      >
        <svg
          className="w-6 h-6 transition-transform duration-200"
          style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)' }}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {/* Backdrop */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/50 z-40 md:hidden"
            onClick={toggleSheet}
            aria-hidden="true"
          />
        )}
      </AnimatePresence>

      {/* Bottom sheet */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className={`fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 rounded-t-2xl shadow-2xl z-50 md:hidden ${className}`}
            role="dialog"
            aria-modal="true"
            aria-label="Number palette"
          >
            {/* Drag handle */}
            <div className="flex justify-center pt-3 pb-2">
              <div className="w-12 h-1 bg-gray-300 dark:bg-gray-600 rounded-full" />
            </div>

            {/* Content */}
            <div className="px-4 pb-6 pt-2 max-h-[70vh] overflow-y-auto">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Desktop view (always visible) */}
      <div className="hidden md:block">
        {children}
      </div>
    </>
  );
}
