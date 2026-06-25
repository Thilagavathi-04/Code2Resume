import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Plus } from 'lucide-react';

export default function SectionEditor({
  title,
  icon: Icon,
  isOpen: controlledOpen,
  onToggle,
  onAdd,
  addLabel,
  children,
  className = '',
  headerExtra,
}) {
  const [internalOpen, setInternalOpen] = useState(true);
  const isOpen = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const toggle = onToggle || (() => setInternalOpen(!internalOpen));

  return (
    <div className={`border border-gray-100 dark:border-gray-700 rounded-xl overflow-hidden ${className}`}>
      <button
        onClick={toggle}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 dark:bg-slate-900 hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors"
      >
        <div className="flex items-center gap-2">
          {Icon && <Icon className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />}
          <span className="text-sm font-semibold text-gray-900 dark:text-white">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {headerExtra}
          {onAdd && (
            <span
              role="button"
              onClick={(e) => { e.stopPropagation(); onAdd(); }}
              className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-lg transition-colors"
            >
              <Plus className="w-3 h-3" />
              {addLabel || 'Add'}
            </span>
          )}
          <motion.div animate={{ rotate: isOpen ? 180 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronDown className="w-4 h-4 text-gray-400" />
          </motion.div>
        </div>
      </button>
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="p-4 space-y-3">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
