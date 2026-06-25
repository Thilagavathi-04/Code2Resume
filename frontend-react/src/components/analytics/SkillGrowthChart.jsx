import { useEffect, useState } from 'react';

const SAMPLE_DATA = [
  { category: 'JavaScript', count: 12, color: '#4F46E5' },
  { category: 'React', count: 9, color: '#7C3AED' },
  { category: 'Node.js', count: 7, color: '#2563EB' },
  { category: 'Python', count: 6, color: '#059669' },
  { category: 'TypeScript', count: 5, color: '#0891B2' },
  { category: 'DevOps', count: 3, color: '#D97706' },
];

export default function SkillGrowthChart({ data = SAMPLE_DATA, height = 200 }) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const maxCount = Math.max(...data.map((d) => d.count));
  const gap = 12;

  return (
    <div className="space-y-0" style={{ height }}>
      {data.map((d, i) => {
        const widthPercent = maxCount > 0 ? (d.count / maxCount) * 100 : 0;
        return (
          <div key={d.category} className="flex items-center gap-3" style={{ marginBottom: gap }}>
            <span className="w-24 text-xs font-medium text-gray-600 dark:text-gray-400 text-right flex-shrink-0 truncate">
              {d.category}
            </span>
            <div className="flex-1 h-6 bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
              <div
                className="h-full rounded-lg transition-all duration-700 ease-out flex items-center justify-end pr-2"
                style={{
                  width: animated ? `${widthPercent}%` : '0%',
                  backgroundColor: d.color,
                  transitionDelay: `${i * 80}ms`,
                }}
              >
                {widthPercent > 20 && (
                  <span className="text-xs font-semibold text-white">{d.count}</span>
                )}
              </div>
            </div>
            {widthPercent <= 20 && (
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400 w-6 text-right">
                {d.count}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
