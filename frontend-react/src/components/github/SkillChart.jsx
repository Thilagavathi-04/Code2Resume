import { motion } from 'framer-motion';

export default function SkillChart({ skills = [], className = '' }) {
  const maxCount = Math.max(...skills.map(s => s.count || 1), 1);

  return (
    <div className={`space-y-3 ${className}`}>
      {skills.slice(0, 10).map((skill, i) => (
        <div key={skill.name || i}>
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {skill.name}
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {skill.count || 0} repos
            </span>
          </div>
          <div className="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${((skill.count || 1) / maxCount) * 100}%` }}
              transition={{ duration: 0.5, delay: i * 0.05 }}
              className="h-full bg-indigo-600 dark:bg-indigo-500 rounded-full"
            />
          </div>
        </div>
      ))}
    </div>
  );
}
