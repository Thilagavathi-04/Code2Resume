const categoryStyles = {
  language: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  framework: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  database: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  tool: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
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
