export default function Card({
  variant = 'default',
  hover = false,
  className = '',
  children,
  ...props
}) {
  const baseClasses = variant === 'glass'
    ? 'glass rounded-2xl p-6'
    : 'bg-white dark:bg-slate-800 border border-gray-100 dark:border-gray-700 rounded-2xl p-6 shadow-sm';
  
  const hoverClasses = hover
    ? 'hover:shadow-md hover:border-indigo-200 dark:hover:border-indigo-800 transition-all duration-300 cursor-pointer'
    : '';

  return (
    <div className={`${baseClasses} ${hoverClasses} ${className}`} {...props}>
      {children}
    </div>
  );
}
