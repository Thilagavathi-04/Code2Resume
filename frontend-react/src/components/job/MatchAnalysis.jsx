import { motion } from 'framer-motion';
import { CheckCircle2, AlertTriangle, XCircle, TrendingUp } from 'lucide-react';
import CircularScore from '../ui/CircularScore';
import Badge from '../ui/Badge';
import Card from '../ui/Card';

const scoreColor = (score) => {
  if (score <= 30) return '#EF4444';
  if (score <= 50) return '#F97316';
  if (score <= 70) return '#F59E0B';
  return '#22C55E';
};

const scoreLabel = (score) => {
  if (score <= 30) return 'Poor Match';
  if (score <= 50) return 'Below Average';
  if (score <= 70) return 'Good Match';
  return 'Excellent Match';
};

const categoryIcons = {
  skills: CheckCircle2,
  experience: AlertTriangle,
  education: XCircle,
  'keyword match': CheckCircle2,
  'section coverage': AlertTriangle,
};

const categoryColors = {
  skills: 'green',
  experience: 'amber',
  education: 'indigo',
  'keyword match': 'green',
  'section coverage': 'amber',
};

export default function MatchAnalysis({ analysis }) {
  if (!analysis) return null;

  const { score = 0, breakdown = [], recommendation = '' } = analysis;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="flex flex-col items-center text-center">
        <CircularScore score={score} size={160} color={scoreColor(score)} label="Match Score" />
        <Badge color={score <= 30 ? 'red' : score <= 50 ? 'amber' : score <= 70 ? 'amber' : 'green'} size="md" className="mt-3">
          {scoreLabel(score)}
        </Badge>
        {recommendation && (
          <p className="mt-3 text-sm text-gray-600 dark:text-gray-400 max-w-md">{recommendation}</p>
        )}
      </div>

      {breakdown.length > 0 && (
        <Card>
          <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-indigo-600" />
            Match Breakdown
          </h4>
          <div className="space-y-3">
            {breakdown.map((item, i) => {
              const Icon = categoryIcons[item.category] || CheckCircle2;
              return (
                <motion.div
                  key={item.category}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="flex items-center gap-3"
                >
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    item.score >= 70 ? 'bg-green-100 dark:bg-green-900/30' : item.score >= 40 ? 'bg-amber-100 dark:bg-amber-900/30' : 'bg-red-100 dark:bg-red-900/30'
                  }`}>
                    <Icon className={`w-4 h-4 ${
                      item.score >= 70 ? 'text-green-600 dark:text-green-400' : item.score >= 40 ? 'text-amber-600 dark:text-amber-400' : 'text-red-600 dark:text-red-400'
                    }`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">{item.category}</span>
                      <Badge color={categoryColors[item.category] || 'gray'} size="sm">{item.score}%</Badge>
                    </div>
                    <div className="w-full h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${item.score}%` }}
                        transition={{ duration: 0.8, delay: 0.2 + i * 0.1 }}
                        className={`h-full rounded-full ${
                          item.score >= 70 ? 'bg-green-500' : item.score >= 40 ? 'bg-amber-500' : 'bg-red-500'
                        }`}
                      />
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </Card>
      )}
    </motion.div>
  );
}
