import { motion } from 'framer-motion';
import { AlertTriangle, Lightbulb, CheckCircle2, Target } from 'lucide-react';
import CircularScore from '../ui/CircularScore';
import Badge from '../ui/Badge';

const scoreColor = (score) => {
  if (score <= 30) return '#EF4444';
  if (score <= 50) return '#F97316';
  if (score <= 70) return '#F59E0B';
  return '#22C55E';
};

const scoreLabel = (score) => {
  if (score <= 30) return 'Poor ATS Compatibility';
  if (score <= 50) return 'Needs Significant Improvement';
  if (score <= 70) return 'Good ATS Compatibility';
  return 'Excellent ATS Compatibility';
};

const scoreDescription = (score) => {
  if (score <= 30) return 'Your resume may be filtered out by most ATS systems. Major improvements needed.';
  if (score <= 50) return 'Your resume has some ATS issues that should be addressed for better results.';
  if (score <= 70) return 'Your resume is reasonably ATS-friendly, but there\'s room for optimization.';
  return 'Your resume is well-optimized for ATS systems. Great job!';
};

const scoreBadgeColor = (score) => {
  if (score <= 30) return 'red';
  if (score <= 50) return 'amber';
  if (score <= 70) return 'amber';
  return 'green';
};

export default function ATSScoreDisplay({ score = 0, keywordsFound = 0, totalKeywords = 0, issues = 0, suggestions = 0 }) {
  const keywordPct = totalKeywords > 0 ? Math.round((keywordsFound / totalKeywords) * 100) : 0;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="flex flex-col items-center text-center py-4"
    >
      <div className="relative">
        <CircularScore score={score} size={220} color={scoreColor(score)} label="ATS Score" />
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 0.3 }}
          className="absolute -bottom-2 left-1/2 -translate-x-1/2"
        >
          <Badge color={scoreBadgeColor(score)} size="md">
            {scoreLabel(score)}
          </Badge>
        </motion.div>
      </div>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="text-sm text-gray-500 dark:text-gray-400 mt-6 max-w-md"
      >
        {scoreDescription(score)}
      </motion.p>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.4 }}
        className="grid grid-cols-3 gap-8 mt-8 w-full max-w-lg"
      >
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-green-50 dark:bg-green-900/10"
        >
          <div className="w-11 h-11 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
            <Target className="w-5 h-5 text-green-600 dark:text-green-400" />
          </div>
          <span className="text-2xl font-bold text-gray-900 dark:text-white">{keywordsFound}/{totalKeywords}</span>
          <span className="text-xs text-gray-500 dark:text-gray-400">Keywords Found</span>
          <div className="w-full h-1.5 bg-green-200 dark:bg-green-800 rounded-full overflow-hidden mt-1">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${keywordPct}%` }}
              transition={{ delay: 0.8, duration: 0.6 }}
              className="h-full bg-green-500 rounded-full"
            />
          </div>
          <span className="text-[10px] text-green-600 dark:text-green-400 font-medium">{keywordPct}% coverage</span>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-red-50 dark:bg-red-900/10"
        >
          <div className="w-11 h-11 rounded-xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
          </div>
          <span className="text-2xl font-bold text-gray-900 dark:text-white">{issues}</span>
          <span className="text-xs text-gray-500 dark:text-gray-400">Issues Found</span>
          <span className={`text-[10px] font-medium mt-1 ${issues === 0 ? 'text-green-600 dark:text-green-400' : 'text-red-500 dark:text-red-400'}`}>
            {issues === 0 ? 'All clear!' : 'Needs attention'}
          </span>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-amber-50 dark:bg-amber-900/10"
        >
          <div className="w-11 h-11 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
            <Lightbulb className="w-5 h-5 text-amber-600 dark:text-amber-400" />
          </div>
          <span className="text-2xl font-bold text-gray-900 dark:text-white">{suggestions}</span>
          <span className="text-xs text-gray-500 dark:text-gray-400">Suggestions</span>
          <span className="text-[10px] text-amber-600 dark:text-amber-400 font-medium mt-1">
            {suggestions > 0 ? 'Review below' : 'Looking good!'}
          </span>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
