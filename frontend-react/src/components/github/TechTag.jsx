const categoryStyles = {
  language: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  framework: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
  database: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  tool: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  default: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
};

export default function TechTag({ name, category = 'default', className = '' }) {
  const style = categoryStyles[category] || categoryStyles.default;

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${style} ${className}`}>
      {name}
    </span>
  );
}
