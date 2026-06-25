import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export default function SkillRadarChart({ categories = [], currentCoverage = [], targetCoverage = [] }) {
  const [mounted, setMounted] = useState(false);
  const size = 280;
  const center = size / 2;
  const maxRadius = (size / 2) - 40;
  const sides = categories.length;
  const angleStep = (2 * Math.PI) / sides;

  useEffect(() => {
    const t = setTimeout(() => setMounted(true), 100);
    return () => clearTimeout(t);
  }, []);

  if (categories.length === 0) return null;

  const getPoint = (index, value) => {
    const angle = angleStep * index - Math.PI / 2;
    const r = (value / 100) * maxRadius;
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle),
    };
  };

  const toPath = (values) => {
    return values.map((v, i) => {
      const p = getPoint(i, v);
      return `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`;
    }).join(' ') + ' Z';
  };

  const getLabelPos = (index) => {
    const angle = angleStep * index - Math.PI / 2;
    const r = maxRadius + 24;
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle),
    };
  };

  const gridLevels = [20, 40, 60, 80, 100];

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {gridLevels.map((level) => (
          <polygon
            key={level}
            points={categories.map((_, i) => {
              const p = getPoint(i, level);
              return `${p.x},${p.y}`;
            }).join(' ')}
            fill="none"
            stroke="#E5E7EB"
            strokeWidth="1"
            className="dark:stroke-gray-700"
          />
        ))}

        {categories.map((_, i) => {
          const p = getPoint(i, 100);
          return (
            <line key={i} x1={center} y1={center} x2={p.x} y2={p.y} stroke="#E5E7EB" strokeWidth="1" className="dark:stroke-gray-700" />
          );
        })}

        {targetCoverage.length > 0 && (
          <motion.path
            d={toPath(targetCoverage)}
            fill="rgba(139, 92, 246, 0.1)"
            stroke="#8B5CF6"
            strokeWidth="2"
            strokeDasharray="6 3"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: mounted ? 1 : 0, scale: mounted ? 1 : 0.5 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            style={{ transformOrigin: `${center}px ${center}px` }}
          />
        )}

        <motion.path
          d={toPath(currentCoverage)}
          fill="rgba(79, 70, 229, 0.15)"
          stroke="#4F46E5"
          strokeWidth="2"
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: mounted ? 1 : 0, scale: mounted ? 1 : 0.5 }}
          transition={{ duration: 0.8 }}
          style={{ transformOrigin: `${center}px ${center}px` }}
        />

        {categories.map((_, i) => {
          const p = getPoint(i, currentCoverage[i] || 0);
          return (
            <motion.circle
              key={i}
              cx={p.x}
              cy={p.y}
              r="4"
              fill="#4F46E5"
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: mounted ? 1 : 0, scale: mounted ? 1 : 0 }}
              transition={{ duration: 0.3, delay: 0.5 + i * 0.08 }}
            />
          );
        })}

        {categories.map((cat, i) => {
          const pos = getLabelPos(i);
          return (
            <text
              key={i}
              x={pos.x}
              y={pos.y}
              textAnchor="middle"
              dominantBaseline="middle"
              className="text-[10px] font-medium fill-gray-600 dark:fill-gray-400"
            >
              {cat}
            </text>
          );
        })}
      </svg>

      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 bg-indigo-600 rounded-full inline-block" />
          Current
        </div>
        {targetCoverage.length > 0 && (
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-purple-600 rounded-full inline-block border-dashed" />
            Target
          </div>
        )}
      </div>
    </div>
  );
}
