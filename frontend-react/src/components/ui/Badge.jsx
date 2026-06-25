const colorVariants = {
  indigo: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400',
  green: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  amber: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  red: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  purple: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
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
