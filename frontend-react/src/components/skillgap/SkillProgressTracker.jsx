import { motion } from 'framer-motion';
import { CheckCircle2, Clock } from 'lucide-react';
import ProgressBar from '../ui/ProgressBar';
import Badge from '../ui/Badge';
import Button from '../ui/Button';

export default function SkillProgressTracker({ skills = [], onMarkComplete }) {
  if (skills.length === 0) return null;

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Skill Progress</h3>
      <div className="space-y-3">
        {skills.map((skill, i) => {
          const progress = skill.currentLevel && skill.targetLevel
            ? Math.round((skill.currentLevel / skill.targetLevel) * 100)
            : skill.progress || 0;
          const color = progress >= 80 ? 'green' : progress >= 40 ? 'indigo' : 'amber';

          return (
            <motion.div
              key={skill.name}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="p-3 rounded-xl border border-gray-100 dark:border-gray-700 bg-white dark:bg-slate-800"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {skill.completed ? (
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border-2 border-gray-300 dark:border-gray-600" />
                  )}
                  <span className={`text-sm font-medium ${skill.completed ? 'text-green-600 dark:text-green-400 line-through' : 'text-gray-900 dark:text-white'}`}>
                    {skill.name}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {skill.estimatedTime && (
                    <div className="flex items-center gap-1 text-xs text-gray-400">
                      <Clock className="w-3 h-3" />
                      {skill.estimatedTime}
                    </div>
                  )}
                  {skill.currentLevel !== undefined && skill.targetLevel !== undefined && (
                    <Badge color={color} size="sm">{skill.currentLevel}/{skill.targetLevel}</Badge>
                  )}
                </div>
              </div>
              <ProgressBar value={progress} color={color} />
              {!skill.completed && onMarkComplete && (
                <div className="mt-2 flex justify-end">
                  <Button variant="ghost" size="sm" onClick={() => onMarkComplete(skill.name)}>
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Mark Complete
                  </Button>
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
