import { motion } from 'framer-motion';
import { Clock, BookOpen, Award, Code } from 'lucide-react';
import Badge from '../ui/Badge';

const priorityColors = {
  high: 'red',
  medium: 'amber',
  low: 'green',
};

const typeIcons = {
  course: BookOpen,
  tutorial: Code,
  certification: Award,
};

const typeColors = {
  course: 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400',
  tutorial: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
  certification: 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400',
};

export default function LearningRoadmap({ steps = [] }) {
  if (steps.length === 0) return null;

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Learning Roadmap</h3>
      <div className="relative">
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />

        <div className="space-y-1">
          {steps.map((step, i) => {
            const Icon = typeIcons[step.type] || BookOpen;
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="relative pl-10"
              >
                <div className={`absolute left-2.5 top-4 w-3 h-3 rounded-full border-2 border-white dark:border-slate-800 ${
                  step.priority === 'high' ? 'bg-red-500' : step.priority === 'medium' ? 'bg-amber-500' : 'bg-green-500'
                }`} />

                <div className="p-3 rounded-xl border border-gray-100 dark:border-gray-700 bg-white dark:bg-slate-800 hover:border-indigo-200 dark:hover:border-indigo-800 transition-colors">
                  <div className="flex items-start gap-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${typeColors[step.type] || typeColors.course}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">{step.title}</p>
                        {step.priority && (
                          <Badge color={priorityColors[step.priority] || 'gray'} size="sm">{step.priority}</Badge>
                        )}
                      </div>
                      {step.description && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{step.description}</p>
                      )}
                      <div className="flex items-center gap-3 mt-2">
                        {step.estimatedTime && (
                          <div className="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
                            <Clock className="w-3 h-3" />
                            {step.estimatedTime}
                          </div>
                        )}
                        {step.difficulty && (
                          <Badge color="gray" size="sm">{step.difficulty}</Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
