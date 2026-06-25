import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bookmark, BookmarkCheck, CheckCircle, ChevronDown, Lightbulb } from 'lucide-react';
import DifficultyBadge from './DifficultyBadge';
import Badge from '../ui/Badge';

export default function QuestionCard({
  question,
  completed = false,
  saved = false,
  onToggleComplete,
  onToggleSave,
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`group rounded-2xl border p-5 transition-all duration-200 ${
        completed
          ? 'bg-green-50/50 dark:bg-green-900/10 border-green-200 dark:border-green-800/50'
          : 'bg-white dark:bg-slate-800 border-gray-100 dark:border-gray-700 hover:border-indigo-200 dark:hover:border-indigo-800 hover:shadow-md'
      }`}
    >
      <div className="flex items-start gap-4">
        <button
          onClick={onToggleComplete}
          className={`mt-0.5 flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${
            completed
              ? 'bg-green-500 border-green-500 text-white'
              : 'border-gray-300 dark:border-gray-600 hover:border-indigo-400 dark:hover:border-indigo-500'
          }`}
        >
          {completed && <CheckCircle className="w-4 h-4" />}
        </button>

        <div className="flex-1 min-w-0">
          <p
            className={`text-sm font-medium leading-relaxed ${
              completed
                ? 'line-through text-gray-400 dark:text-gray-500'
                : 'text-gray-900 dark:text-white'
            }`}
          >
            {question.text}
          </p>

          <div className="flex items-center gap-2 mt-3 flex-wrap">
            <DifficultyBadge difficulty={question.difficulty} size="sm" />
            <Badge color="purple" size="sm">{question.category}</Badge>
          </div>

          <div className="flex items-center gap-1 mt-3">
            <button
              onClick={() => setExpanded(!expanded)}
              className="inline-flex items-center gap-1.5 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
            >
              <Lightbulb className="w-3.5 h-3.5" />
              {expanded ? 'Hide hint' : 'Show hint'}
              <ChevronDown
                className={`w-3.5 h-3.5 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}
              />
            </button>

            <button
              onClick={onToggleSave}
              className={`ml-auto p-1.5 rounded-lg transition-colors ${
                saved
                  ? 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30'
                  : 'text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              {saved ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
            </button>
          </div>

          <AnimatePresence>
            {expanded && question.hint && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="mt-3 p-3 rounded-xl bg-indigo-50/80 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
                  <p className="text-xs text-indigo-700 dark:text-indigo-300 leading-relaxed">
                    {question.hint}
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
}
