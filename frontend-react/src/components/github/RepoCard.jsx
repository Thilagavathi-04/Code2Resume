import { motion } from 'framer-motion';
import { Star, Code2 } from 'lucide-react';
import Badge from '../ui/Badge';

export default function RepoCard({ repo, isSelected, onClick, className = '' }) {
  const techCount = Array.isArray(repo.tech_stack)
    ? repo.tech_stack.length
    : typeof repo.tech_stack === 'string'
    ? repo.tech_stack.split(',').filter(Boolean).length
    : 0;

  const description = repo.description || 'No description available';

  return (
    <motion.button
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
      onClick={onClick}
      className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
        isSelected
          ? 'bg-indigo-50 border-indigo-300 dark:bg-indigo-900/20 dark:border-indigo-700'
          : 'bg-white border-gray-100 hover:border-indigo-200 dark:bg-slate-800 dark:border-gray-700 dark:hover:border-indigo-800'
      } ${className}`}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <h4 className="text-sm font-semibold text-gray-900 dark:text-white truncate">
          {repo.name || 'Unnamed'}
        </h4>
        {repo.stars > 0 && (
          <span className="inline-flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400 flex-shrink-0">
            <Star className="w-3 h-3" />
            {repo.stars}
          </span>
        )}
      </div>

      <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">
        {description}
      </p>

      <div className="flex items-center gap-2 flex-wrap">
        {repo.language && (
          <Badge color="indigo" size="sm">
            <Code2 className="w-3 h-3" />
            {repo.language}
          </Badge>
        )}
        {repo.domain && (
          <Badge color="purple" size="sm">{repo.domain}</Badge>
        )}
        {techCount > 0 && (
          <Badge color="gray" size="sm">{techCount} tech</Badge>
        )}
      </div>
    </motion.button>
  );
}
