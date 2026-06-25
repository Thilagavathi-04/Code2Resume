const variants = {
  text: 'h-4 rounded',
  circular: 'rounded-full',
  rectangular: 'rounded-xl',
};

export default function Skeleton({
  variant = 'text',
  width,
  height,
  className = '',
}) {
  const defaultSizes = {
    text: { width: '100%', height: '16px' },
    circular: { width: '40px', height: '40px' },
    rectangular: { width: '100%', height: '200px' },
  };

  const size = {
    width: width || defaultSizes[variant].width,
    height: height || defaultSizes[variant].height,
  };

  return (
    <div
      className={`bg-skeleton ${variants[variant]} ${className}`}
      style={size}
    />
  );
}
