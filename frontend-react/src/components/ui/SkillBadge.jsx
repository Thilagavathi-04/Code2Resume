const categoryColors = {
  language: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  framework: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  tool: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  soft: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  default: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
};

const proficiencyDots = {
  beginner: 1,
  intermediate: 2,
  advanced: 3,
  expert: 4,
};

export default function SkillBadge({
  name,
  category = 'default',
  proficiency,
  className = '',
}) {
  const colorClass = categoryColors[category] || categoryColors.default;
  const dots = proficiency ? proficiencyDots[proficiency] || 0 : 0;

  return (
    <span
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium ${colorClass} ${className}`}
    >
      {name}
      {proficiency && (
        <span className="flex gap-0.5">
          {Array.from({ length: 4 }).map((_, i) => (
            <span
              key={i}
              className={`w-1.5 h-1.5 rounded-full ${
                i < dots
                  ? 'bg-current opacity-100'
                  : 'bg-current opacity-20'
              }`}
            />
          ))}
        </span>
      )}
    </span>
  );
}
