import { useEffect, useState } from 'react';

const SAMPLE_LINES = [
  {
    label: 'Frontend Engineer',
    color: '#4F46E5',
    data: [45, 52, 58, 55, 62, 68, 72, 75, 78, 82],
  },
  {
    label: 'Full Stack Developer',
    color: '#7C3AED',
    data: [38, 42, 48, 50, 55, 58, 60, 65, 70, 73],
  },
  {
    label: 'React Engineer',
    color: '#059669',
    data: [60, 62, 65, 68, 70, 72, 75, 78, 80, 85],
  },
];

const X_LABELS = ['Jun 1', 'Jun 3', 'Jun 5', 'Jun 7', 'Jun 9', 'Jun 11', 'Jun 13', 'Jun 15', 'Jun 17', 'Jun 19'];

export default function MatchTrendChart({ lines = SAMPLE_LINES, height = 200 }) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const chartWidth = 600;
  const chartHeight = height;
  const padding = { top: 10, right: 20, bottom: 30, left: 40 };

  const allValues = lines.flatMap((l) => l.data);
  const maxVal = Math.max(...allValues);
  const minVal = Math.max(0, Math.min(...allValues) - 10);

  const xScale = (i) => padding.left + (i / (X_LABELS.length - 1)) * (chartWidth - padding.left - padding.right);
  const yScale = (v) => padding.top + (1 - (v - minVal) / (maxVal - minVal)) * (chartHeight - padding.top - padding.bottom);

  const yTicks = 5;
  const yTickValues = Array.from({ length: yTicks + 1 }, (_, i) =>
    Math.round(minVal + (i / yTicks) * (maxVal - minVal))
  );

  return (
    <div className="space-y-3">
      <div className="w-full overflow-x-auto">
        <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full" style={{ minWidth: 300 }}>
          {yTickValues.map((v) => (
            <g key={v}>
              <line
                x1={padding.left}
                y1={yScale(v)}
                x2={chartWidth - padding.right}
                y2={yScale(v)}
                stroke="currentColor"
                className="text-gray-100 dark:text-gray-700"
                strokeDasharray="4 4"
              />
              <text
                x={padding.left - 8}
                y={yScale(v) + 4}
                textAnchor="end"
                className="fill-gray-400 dark:fill-gray-500"
                fontSize="11"
              >
                {v}
              </text>
            </g>
          ))}

          {X_LABELS.map((label, i) => (
            <text
              key={i}
              x={xScale(i)}
              y={chartHeight - 8}
              textAnchor="middle"
              className="fill-gray-400 dark:fill-gray-500"
              fontSize="10"
            >
              {label}
            </text>
          ))}

          {lines.map((line, li) => {
            const points = line.data.map((v, i) => `${xScale(i)},${yScale(v)}`).join(' ');
            return (
              <g key={li}>
                <polyline
                  points={points}
                  fill="none"
                  stroke={line.color}
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className={`transition-all duration-1000 ${animated ? 'opacity-100' : 'opacity-0'}`}
                />
                {line.data.map((v, i) => (
                  <circle
                    key={i}
                    cx={xScale(i)}
                    cy={yScale(v)}
                    r="3"
                    fill={line.color}
                    stroke="white"
                    strokeWidth="1.5"
                    className={`dark:stroke-slate-800 transition-all duration-500 ${
                      animated ? 'opacity-100' : 'opacity-0'
                    }`}
                    style={{ transitionDelay: `${i * 40 + li * 100}ms` }}
                  />
                ))}
              </g>
            );
          })}
        </svg>
      </div>

      <div className="flex flex-wrap gap-4 justify-center">
        {lines.map((line) => (
          <div key={line.label} className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: line.color }} />
            <span className="text-xs font-medium text-gray-600 dark:text-gray-400">{line.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
