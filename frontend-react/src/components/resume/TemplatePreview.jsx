import Modal from '../ui/Modal';
import Button from '../ui/Button';

const gradients = {
  modern: 'from-indigo-500 to-purple-600',
  professional: 'from-gray-700 to-gray-900',
  startup: 'from-emerald-500 to-teal-600',
  minimal: 'from-gray-300 to-gray-400 dark:from-gray-600 dark:to-gray-700',
};

function TemplateLayout({ id }) {
  if (id === 'modern') {
    return (
      <div className="bg-white dark:bg-slate-800 p-8 space-y-6 shadow-lg rounded-lg">
        <div className="text-center border-b border-gray-100 dark:border-gray-700 pb-4">
          <div className="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded mx-auto mb-2" />
          <div className="h-4 w-64 bg-gray-100 dark:bg-gray-800 rounded mx-auto mb-1" />
          <div className="h-3 w-40 bg-gray-100 dark:bg-gray-800 rounded mx-auto" />
        </div>
        <div>
          <div className="h-4 w-32 bg-indigo-200 dark:bg-indigo-900/30 rounded mb-3" />
          <div className="space-y-1.5">
            <div className="h-3 w-full bg-gray-100 dark:bg-gray-700 rounded" />
            <div className="h-3 w-5/6 bg-gray-100 dark:bg-gray-700 rounded" />
            <div className="h-3 w-4/6 bg-gray-100 dark:bg-gray-700 rounded" />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-1.5">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-6 bg-indigo-100 dark:bg-indigo-900/20 rounded" />
          ))}
        </div>
        <div>
          <div className="h-4 w-32 bg-indigo-200 dark:bg-indigo-900/30 rounded mb-3" />
          <div className="space-y-3">
            <div className="flex justify-between">
              <div className="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded" />
              <div className="h-3 w-16 bg-gray-100 dark:bg-gray-800 rounded" />
            </div>
            <div className="h-2 w-full bg-gray-100 dark:bg-gray-700 rounded" />
            <div className="h-2 w-5/6 bg-gray-100 dark:bg-gray-700 rounded" />
          </div>
        </div>
      </div>
    );
  }
  if (id === 'professional') {
    return (
      <div className="bg-white dark:bg-slate-800 p-8 space-y-6 shadow-lg rounded-lg">
        <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
          <div className="h-8 w-56 bg-gray-800 dark:bg-gray-200 rounded mb-2" />
          <div className="h-3 w-48 bg-gray-300 dark:bg-gray-600 rounded" />
        </div>
        <div className="space-y-4">
          {['Experience', 'Education', 'Skills'].map((section, i) => (
            <div key={i}>
              <div className="h-4 w-24 bg-gray-800 dark:bg-gray-200 rounded mb-2" />
              <div className="space-y-1.5 pl-3 border-l-2 border-gray-200 dark:border-gray-700">
                <div className="h-2.5 w-full bg-gray-100 dark:bg-gray-700 rounded" />
                <div className="h-2.5 w-4/5 bg-gray-100 dark:bg-gray-700 rounded" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }
  if (id === 'startup') {
    return (
      <div className="bg-white dark:bg-slate-800 p-8 space-y-6 shadow-lg rounded-lg">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-emerald-200 dark:bg-emerald-900/30" />
          <div>
            <div className="h-6 w-40 bg-gray-200 dark:bg-gray-700 rounded mb-1" />
            <div className="h-3 w-32 bg-gray-100 dark:bg-gray-800 rounded" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 bg-emerald-50 dark:bg-emerald-900/10 rounded-lg">
            <div className="h-3 w-16 bg-emerald-200 dark:bg-emerald-800/30 rounded mb-2" />
            <div className="space-y-1">
              <div className="h-2 w-full bg-gray-100 dark:bg-gray-700 rounded" />
              <div className="h-2 w-4/5 bg-gray-100 dark:bg-gray-700 rounded" />
            </div>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="h-3 w-16 bg-gray-200 dark:bg-gray-700 rounded mb-2" />
            <div className="space-y-1">
              <div className="h-2 w-full bg-gray-100 dark:bg-gray-700 rounded" />
              <div className="h-2 w-4/5 bg-gray-100 dark:bg-gray-700 rounded" />
            </div>
          </div>
        </div>
      </div>
    );
  }
  return (
    <div className="bg-white dark:bg-slate-800 p-8 space-y-8 shadow-lg rounded-lg">
      <div className="text-center">
        <div className="h-7 w-40 bg-gray-200 dark:bg-gray-700 rounded mx-auto" />
      </div>
      <div className="space-y-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="space-y-1.5">
            <div className="h-2.5 w-full bg-gray-100 dark:bg-gray-700 rounded" />
            <div className="h-2.5 w-5/6 bg-gray-100 dark:bg-gray-700 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}

export default function TemplatePreview({ template, isOpen, onClose, onSelect }) {
  if (!template) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={template.name} size="lg">
      <div className="space-y-4">
        <div className={`aspect-[3/4] max-h-[500px] overflow-auto rounded-lg bg-gradient-to-br ${gradients[template.id] || gradients.modern} p-2`}>
          <TemplateLayout id={template.id} />
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-300">{template.description}</p>
        <div className="flex gap-2">
          <Button variant="primary" className="flex-1" onClick={() => { onSelect(template.id); onClose(); }}>
            Select & Use
          </Button>
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}
