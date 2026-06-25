import { motion } from 'framer-motion';
import { Check, X, Plus, Sparkles } from 'lucide-react';
import Card from '../ui/Card';

export default function SkillComparison({ yourSkills = [], requiredSkills = [] }) {
  const normalize = (s) => (typeof s === 'string' ? s.toLowerCase().trim() : '');
  const yourSet = new Set(yourSkills.map(normalize).filter(Boolean));
  const requiredSet = new Set(requiredSkills.map(normalize).filter(Boolean));

  const matched = [...requiredSet].filter(s => yourSet.has(s));
  const missing = [...requiredSet].filter(s => !yourSet.has(s));
  const extra = [...yourSet].filter(s => !requiredSet.has(s));

  const categories = [
    { label: 'Matching Skills', skills: matched, icon: Check, color: 'text-green-600 dark:text-green-400', bg: 'bg-green-100 dark:bg-green-900/30', barColor: 'bg-green-500' },
    { label: 'Missing Skills', skills: missing, icon: X, color: 'text-red-600 dark:text-red-400', bg: 'bg-red-100 dark:bg-red-900/30', barColor: 'bg-red-500' },
    { label: 'Additional Skills', skills: extra, icon: Plus, color: 'text-blue-600 dark:text-blue-400', bg: 'bg-blue-100 dark:bg-blue-900/30', barColor: 'bg-blue-500' },
  ];

  const totalRequired = requiredSet.size;
  const matchPercentage = totalRequired > 0 ? Math.round((matched.length / totalRequired) * 100) : 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          Skill Comparison
        </h3>
        <span className="text-xs text-gray-500 dark:text-gray-400">{matched.length}/{totalRequired} required skills matched</span>
      </div>

      <div className="w-full h-2.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${matchPercentage}%` }}
          transition={{ duration: 0.8 }}
          className={`h-full rounded-full ${matchPercentage >= 70 ? 'bg-green-500' : matchPercentage >= 40 ? 'bg-amber-500' : 'bg-red-500'}`}
        />
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 text-right">{matchPercentage}% coverage</p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {categories.map((cat, ci) => (
          <Card key={cat.label} className="!p-4">
            <div className="flex items-center gap-2 mb-3">
              <div className={`w-6 h-6 rounded-md ${cat.bg} flex items-center justify-center`}>
                <cat.icon className={`w-3.5 h-3.5 ${cat.color}`} />
              </div>
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{cat.label}</span>
              <span className="text-xs text-gray-400 ml-auto">{cat.skills.length}</span>
            </div>
            <div className="space-y-2">
              {cat.skills.length === 0 && (
                <p className="text-xs text-gray-400 dark:text-gray-500 italic">None</p>
              )}
              {cat.skills.map((skill, si) => (
                <motion.div
                  key={skill}
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: (ci * 0.1) + (si * 0.03) }}
                  className="flex items-center gap-2"
                >
                  <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${cat.barColor}`} />
                  <span className="text-sm text-gray-700 dark:text-gray-300">{skill}</span>
                </motion.div>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
