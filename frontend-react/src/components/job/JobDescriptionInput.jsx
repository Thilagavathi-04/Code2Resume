import { useState } from 'react';
import { ClipboardPaste, FileText } from 'lucide-react';
import Button from '../ui/Button';

export default function JobDescriptionInput({ onChange }) {
  const [title, setTitle] = useState('');
  const [company, setCompany] = useState('');
  const [description, setDescription] = useState('');

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setDescription(text);
      onChange?.({ title, company, description: text });
    } catch {
      // Clipboard access denied
    }
  };

  const update = (field, value) => {
    const state = { title, company, description, [field]: value };
    if (field === 'title') setTitle(value);
    if (field === 'company') setCompany(value);
    if (field === 'description') setDescription(value);
    onChange?.(state);
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Job Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => update('title', e.target.value)}
            placeholder="e.g. Senior Frontend Developer"
            className="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Company</label>
          <input
            type="text"
            value={company}
            onChange={(e) => update('company', e.target.value)}
            placeholder="e.g. Google"
            className="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Job Description</label>
          <span className="text-xs text-gray-400 dark:text-gray-500">{description.length} chars</span>
        </div>
        <div className="relative">
          <textarea
            value={description}
            onChange={(e) => update('description', e.target.value)}
            placeholder="Paste the full job description here..."
            rows={8}
            className="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
          />
          <Button
            variant="ghost"
            size="sm"
            onClick={handlePaste}
            className="absolute top-2 right-2"
          >
            <ClipboardPaste className="w-4 h-4" />
            Paste
          </Button>
        </div>
      </div>
    </div>
  );
}
