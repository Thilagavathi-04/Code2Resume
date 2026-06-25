import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lightbulb, ChevronDown, AlertCircle } from 'lucide-react';
import Badge from '../ui/Badge';

const priorityColors = {
  high: 'red',
  medium: 'amber',
  low: 'green',
};

export default function OptimizationSuggestions({ suggestions = [] }) {
  const [expanded, setExpanded] = useState(null);

  if (suggestions.length === 0) return null;

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Optimization Suggestions</h3>
      <div className="space-y-2">
        {suggestions.map((s, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <button
              onClick={() => setExpanded(expanded === i ? null : i)}
              className="w-full text-left p-3 rounded-xl border border-gray-100 dark:border-gray-700 hover:border-indigo-200 dark:hover:border-indigo-800 bg-white dark:bg-slate-800 transition-all"
            >
              <div className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Lightbulb className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-gray-400 dark:text-gray-500">#{i + 1}</span>
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{s.title}</p>
                  </div>
                  {s.priority && (
                    <Badge color={priorityColors[s.priority] || 'gray'} size="sm" className="mt-1">
                      {s.priority}
                    </Badge>
                  )}
                </div>
                <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform flex-shrink-0 ${expanded === i ? 'rotate-180' : ''}`} />
              </div>
              <AnimatePresence>
                {expanded === i && s.description && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 pl-10">{s.description}</p>
                    {s.category && (
                      <div className="flex items-center gap-1 mt-2 pl-10">
                        <AlertCircle className="w-3 h-3 text-gray-400" />
                        <span className="text-xs text-gray-500 dark:text-gray-400">{s.category}</span>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
