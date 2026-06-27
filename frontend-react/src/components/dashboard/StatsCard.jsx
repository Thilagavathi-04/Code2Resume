export default function StatsCard({ title, value, icon, color = 'blue' }) {
  const colorClasses = {
    blue: 'bg-gray-50 text-gray-600',
    green: 'bg-gray-50 text-gray-600',
    purple: 'bg-gray-50 text-gray-700',
    orange: 'bg-gray-50 text-gray-600',
    teal: 'bg-gray-50 text-gray-600',
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-all duration-300">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`${colorClasses[color]} p-3 rounded-xl`}>
          {icon}
        </div>
      </div>
    </div>
  );
}
