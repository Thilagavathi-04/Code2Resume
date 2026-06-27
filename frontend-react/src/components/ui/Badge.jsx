const colorVariants = {
  indigo: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  green: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  amber: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  red: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  purple: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  gray: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
};

const sizeVariants = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
};

export default function Badge({
  color = 'indigo',
  size = 'md',
  className = '',
  children,
  ...props
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 font-medium rounded-full ${colorVariants[color]} ${sizeVariants[size]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
}
