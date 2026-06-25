const colorClasses = {
  indigo: 'bg-indigo-600',
  green: 'bg-green-500',
  amber: 'bg-amber-500',
  red: 'bg-red-500',
};

export default function ProgressBar({
  value = 0,
  color = 'indigo',
  showLabel = false,
  className = '',
}) {
  const clampedValue = Math.min(100, Math.max(0, value));

  return (
    <div className={className}>
      {showLabel && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Progress</span>
          <span className="text-sm font-medium text-gray-500 dark:text-gray-400">{clampedValue}%</span>
        </div>
      )}
      <div className="w-full h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClasses[color]} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${clampedValue}%` }}
        />
      </div>
    </div>
  );
}
