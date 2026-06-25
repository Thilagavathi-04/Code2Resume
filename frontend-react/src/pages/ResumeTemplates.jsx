import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Layout, Search } from 'lucide-react';
import Card from '../components/ui/Card';
import EmptyState from '../components/ui/EmptyState';
import TemplateCard from '../components/resume/TemplateCard';
import TemplatePreview from '../components/resume/TemplatePreview';
import { useResumeStore } from '../store/resumeStore';

const TEMPLATES = [
  {
    id: 'modern',
    name: 'Modern',
    description: 'Clean layout with indigo accents, centered header, and organized sections.',
  },
  {
    id: 'professional',
    name: 'Professional',
    description: 'Dark header banner with traditional single-column layout for corporate roles.',
  },
  {
    id: 'startup',
    name: 'Startup',
    description: 'Creative card-based layout with emerald accents and avatar for tech roles.',
  },
  {
    id: 'minimal',
    name: 'Minimal',
    description: 'Stripped-back design focused purely on content with elegant typography.',
  },
  {
    id: 'creative',
    name: 'Creative',
    description: 'Bold two-column layout with fuchsia gradient sidebar for creative professionals.',
  },
  {
    id: 'executive',
    name: 'Executive',
    description: 'Formal dark header with structured sections for senior leadership roles.',
  },
  {
    id: 'technical',
    name: 'Technical',
    description: 'Monospace accents with cyan highlights, code-comment style section headers.',
  },
];

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
};

const staggerItem = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0 },
};

export default function ResumeTemplates() {
  const navigate = useNavigate();
  const { selectedTemplate, setSelectedTemplate } = useResumeStore();
  const [previewTemplate, setPreviewTemplate] = useState(null);
  const [search, setSearch] = useState('');

  const filtered = TEMPLATES.filter(t =>
    !search || t.name.toLowerCase().includes(search.toLowerCase()) ||
    t.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <motion.div
      className="space-y-6"
      initial="hidden"
      animate="visible"
      variants={staggerContainer}
    >
      <motion.div variants={staggerItem}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Resume Templates</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Choose a template to style your resume
            </p>
          </div>
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search templates..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>
      </motion.div>

      {selectedTemplate && (
        <motion.div variants={staggerItem}>
          <Card className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/10 dark:to-purple-900/10 border-indigo-200 dark:border-indigo-800">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-indigo-700 dark:text-indigo-300">
                  Active Template
                </p>
                <p className="text-lg font-bold text-gray-900 dark:text-white">
                  {TEMPLATES.find(t => t.id === selectedTemplate)?.name}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => navigate('/builder')}
                  className="text-xs text-white bg-indigo-600 hover:bg-indigo-700 px-3 py-1.5 rounded-lg font-medium transition-colors"
                >
                  Go to Builder
                </button>
                <button
                  onClick={() => setSelectedTemplate(null)}
                  className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline"
                >
                  Change
                </button>
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      <motion.div variants={staggerItem} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filtered.map(template => (
          <motion.div key={template.id} variants={staggerItem}>
            <TemplateCard
              template={template}
              isSelected={selectedTemplate === template.id}
              onSelect={id => setPreviewTemplate(TEMPLATES.find(t => t.id === id))}
            />
          </motion.div>
        ))}
      </motion.div>

      {filtered.length === 0 && (
        <motion.div variants={staggerItem}>
          <Card>
            <EmptyState
              icon={Layout}
              title="No templates found"
              description="Try adjusting your search query"
            />
          </Card>
        </motion.div>
      )}

      <TemplatePreview
        template={previewTemplate}
        isOpen={!!previewTemplate}
        onClose={() => setPreviewTemplate(null)}
        onSelect={setSelectedTemplate}
      />
    </motion.div>
  );
}
