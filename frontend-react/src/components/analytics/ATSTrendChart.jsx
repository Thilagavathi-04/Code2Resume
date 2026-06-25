import { useEffect, useState } from 'react';

const SAMPLE_DATA = [
  { date: 'Jun 1', score: 62 },
  { date: 'Jun 3', score: 65 },
  { date: 'Jun 5', score: 58 },
  { date: 'Jun 7', score: 70 },
  { date: 'Jun 9', score: 68 },
  { date: 'Jun 11', score: 74 },
  { date: 'Jun 13', score: 72 },
  { date: 'Jun 15', score: 78 },
  { date: 'Jun 17', score: 80 },
  { date: 'Jun 19', score: 85 },
];

export default function ATSTrendChart({ data = SAMPLE_DATA, height = 200 }) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setAnimated(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const padding = { top: 20, right: 20, bottom: 30, left: 40 };
  const chartWidth = 600;
  const chartHeight = height;

  const xScale = (i) => padding.left + (i / (data.length - 1)) * (chartWidth - padding.left - padding.right);
  const yScale = (v) => padding.top + (1 - v / 100) * (chartHeight - padding.top - padding.bottom);

  const linePoints = data.map((d, i) => `${xScale(i)},${yScale(d.score)}`).join(' ');
  const areaPoints = `${xScale(0)},${chartHeight - padding.bottom} ${linePoints} ${xScale(data.length - 1)},${chartHeight - padding.bottom}`;

  const yLabels = [0, 25, 50, 75, 100];

  return (
    <div className="w-full overflow-x-auto">
      <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full" style={{ minWidth: 300 }}>
        <defs>
          <linearGradient id="atsGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#4F46E5" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#4F46E5" stopOpacity="0.02" />
          </linearGradient>
        </defs>

        {yLabels.map((v) => (
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

        <polygon
          points={areaPoints}
          fill="url(#atsGradient)"
          className={`transition-all duration-1000 ${animated ? 'opacity-100' : 'opacity-0'}`}
        />

        <polyline
          points={linePoints}
          fill="none"
          stroke="#4F46E5"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={`transition-all duration-1000 ${animated ? 'opacity-100' : 'opacity-0'}`}
        />

        {data.map((d, i) => (
          <g key={i}>
            <circle
              cx={xScale(i)}
              cy={yScale(d.score)}
              r="4"
              fill="#4F46E5"
              stroke="white"
              strokeWidth="2"
              className={`transition-all duration-500 dark:stroke-slate-800 ${
                animated ? 'opacity-100' : 'opacity-0'
              }`}
              style={{ transitionDelay: `${i * 50}ms` }}
            />
            <text
              x={xScale(i)}
              y={chartHeight - 8}
              textAnchor="middle"
              className="fill-gray-400 dark:fill-gray-500"
              fontSize="10"
            >
              {d.date}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}
