import { motion } from 'framer-motion';
import Button from '../ui/Button';

const gradients = {
  modern: 'from-indigo-500 to-purple-600',
  professional: 'from-gray-700 to-gray-900',
  startup: 'from-emerald-500 to-teal-600',
  minimal: 'from-gray-300 to-gray-400 dark:from-gray-600 dark:to-gray-700',
  creative: 'from-fuchsia-500 to-purple-600',
  executive: 'from-slate-700 to-slate-900',
  technical: 'from-cyan-500 to-blue-600',
};

const layouts = {
  modern: (
    <div className="w-full h-full p-3 space-y-2">
      <div className="h-2 w-1/3 bg-white/40 rounded" />
      <div className="h-1 w-1/2 bg-white/20 rounded" />
      <div className="h-1 w-2/5 bg-white/20 rounded" />
      <div className="h-px bg-white/20 my-1" />
      <div className="flex gap-2">
        <div className="flex-1 space-y-1">
          <div className="h-1 w-full bg-white/30 rounded" />
          <div className="h-1 w-4/5 bg-white/20 rounded" />
          <div className="h-1 w-3/5 bg-white/20 rounded" />
        </div>
        <div className="w-1/3 space-y-1">
          <div className="h-1 w-full bg-white/30 rounded" />
          <div className="h-1 w-4/5 bg-white/20 rounded" />
          <div className="h-1 w-2/3 bg-white/20 rounded" />
        </div>
      </div>
    </div>
  ),
  professional: (
    <div className="w-full h-full p-3 space-y-2">
      <div className="h-3 w-2/5 bg-white/40 rounded" />
      <div className="h-1 w-1/3 bg-white/20 rounded" />
      <div className="h-px bg-white/20 my-1" />
      <div className="space-y-1">
        <div className="h-1 w-full bg-white/30 rounded" />
        <div className="h-1 w-5/6 bg-white/20 rounded" />
        <div className="h-1 w-4/5 bg-white/20 rounded" />
      </div>
      <div className="space-y-1">
        <div className="h-1 w-3/5 bg-white/30 rounded" />
        <div className="h-1 w-full bg-white/20 rounded" />
        <div className="h-1 w-2/3 bg-white/20 rounded" />
      </div>
    </div>
  ),
  startup: (
    <div className="w-full h-full p-3 space-y-2">
      <div className="h-2 w-1/4 bg-white/40 rounded" />
      <div className="h-1 w-1/3 bg-white/20 rounded" />
      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1">
          <div className="h-1 w-full bg-white/30 rounded" />
          <div className="h-1 w-4/5 bg-white/20 rounded" />
        </div>
        <div className="space-y-1">
          <div className="h-1 w-full bg-white/30 rounded" />
          <div className="h-1 w-3/4 bg-white/20 rounded" />
        </div>
      </div>
    </div>
  ),
  minimal: (
    <div className="w-full h-full p-3 space-y-3">
      <div className="h-2 w-1/3 bg-white/30 rounded" />
      <div className="space-y-1">
        <div className="h-1 w-full bg-white/20 rounded" />
        <div className="h-1 w-5/6 bg-white/15 rounded" />
      </div>
    </div>
  ),
  creative: (
    <div className="w-full h-full flex">
      <div className="w-1/3 bg-white/20 p-2 space-y-1">
        <div className="h-2 w-full bg-white/40 rounded" />
        <div className="h-1 w-4/5 bg-white/30 rounded" />
        <div className="h-1 w-3/5 bg-white/20 rounded" />
      </div>
      <div className="flex-1 p-2 space-y-1">
        <div className="h-1 w-2/3 bg-white/30 rounded" />
        <div className="h-1 w-full bg-white/20 rounded" />
        <div className="h-1 w-4/5 bg-white/20 rounded" />
      </div>
    </div>
  ),
  executive: (
    <div className="w-full h-full p-3 space-y-2">
      <div className="h-4 w-3/5 bg-white/40 rounded" />
      <div className="h-1 w-1/2 bg-white/20 rounded" />
      <div className="h-px bg-white/30 my-1" />
      <div className="space-y-1">
        <div className="h-1 w-full bg-white/30 rounded" />
        <div className="h-1 w-5/6 bg-white/20 rounded" />
      </div>
      <div className="space-y-1">
        <div className="h-1 w-2/3 bg-white/30 rounded" />
        <div className="h-1 w-full bg-white/20 rounded" />
      </div>
    </div>
  ),
  technical: (
    <div className="w-full h-full p-3 space-y-2">
      <div className="h-2 w-2/5 bg-white/40 rounded font-mono" />
      <div className="h-px w-full bg-cyan-400/40 my-1" />
      <div className="space-y-1 font-mono">
        <div className="h-1 w-1/3 bg-cyan-300/40 rounded" />
        <div className="h-1 w-full bg-white/20 rounded" />
        <div className="h-1 w-4/5 bg-white/15 rounded" />
      </div>
      <div className="space-y-1 font-mono">
        <div className="h-1 w-1/4 bg-cyan-300/40 rounded" />
        <div className="h-1 w-5/6 bg-white/20 rounded" />
      </div>
    </div>
  ),
};

export default function TemplateCard({ template, onSelect, isSelected, className = '' }) {
  const gradient = gradients[template.id] || gradients.modern;

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -4 }}
      whileTap={{ scale: 0.98 }}
      className={`group relative rounded-xl overflow-hidden border-2 transition-colors ${
        isSelected
          ? 'border-indigo-500'
          : 'border-gray-100 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-700'
      } ${className}`}
    >
      <div className={`aspect-[3/4] bg-gradient-to-br ${gradient}`}>
        {layouts[template.id] || layouts.modern}
      </div>
      <div className="p-3 bg-white dark:bg-slate-800">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">{template.name}</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{template.description}</p>
        <Button
          variant="primary"
          size="sm"
          className="w-full mt-2 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={() => onSelect(template.id)}
        >
          Select Template
        </Button>
      </div>
    </motion.div>
  );
}
