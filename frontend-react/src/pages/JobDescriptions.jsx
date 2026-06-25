import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Briefcase, Plus, Trash2, Loader2, Check } from 'lucide-react';
import v2 from '../api/v2';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Modal from '../components/ui/Modal';
import EmptyState from '../components/ui/EmptyState';
import { useResumeStore } from '../store/resumeStore';
import { useToastStore } from '../components/ui/Toast';
import JobDescriptionInput from '../components/job/JobDescriptionInput';

const stagger = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
};
const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0 },
};

export default function JobDescriptions() {
  const addToast = useToastStore(s => s.addToast);
  const { selectedJobDescription, setSelectedJobDescription } = useResumeStore();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const [formData, setFormData] = useState({ title: '', company: '', description: '' });

  const loadJobs = useCallback(async () => {
    try {
      const res = await v2.jobs.list();
      const data = res.data || res;
      setJobs(Array.isArray(data) ? data : []);
    } catch {
      setJobs([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadJobs(); }, [loadJobs]);

  const handleCreate = async () => {
    if (!formData.title.trim() || !formData.description.trim()) {
      addToast({ type: 'warning', message: 'Title and description are required' });
      return;
    }
    setCreating(true);
    try {
      const res = await v2.jobs.create({
        title: formData.title,
        company: formData.company || null,
        description: formData.description,
      });
      const created = res.data || res;
      setJobs(prev => [created, ...prev]);
      setShowCreateModal(false);
      setFormData({ title: '', company: '', description: '' });
      addToast({ type: 'success', message: 'Job description created' });
    } catch {
      addToast({ type: 'error', message: 'Failed to create job description' });
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this job description?')) return;
    setDeleting(id);
    try {
      await v2.jobs.delete?.(id).catch(() => {});
      setJobs(prev => prev.filter(j => j.id !== id));
      if (selectedJobDescription?.id === id) setSelectedJobDescription(null);
      addToast({ type: 'success', message: 'Job description deleted' });
    } catch {
      addToast({ type: 'error', message: 'Failed to delete' });
    } finally {
      setDeleting(null);
    }
  };

  const handleSelect = (job) => {
    setSelectedJobDescription(job);
    addToast({ type: 'success', message: `Selected: ${job.title}` });
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-indigo-500" /></div>;
  }

  return (
    <motion.div className="space-y-6" initial="hidden" animate="visible" variants={stagger}>
      <motion.div variants={item}>
        <Card className="bg-gradient-to-r from-purple-600 to-indigo-600 border-0 text-white">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Briefcase className="w-6 h-6" />
                Job Descriptions
              </h1>
              <p className="text-purple-100 mt-1">Create and manage job descriptions for resume targeting</p>
            </div>
            <Button
              onClick={() => setShowCreateModal(true)}
              variant="secondary"
              className="bg-white/20 hover:bg-white/30 text-white border-white/20"
            >
              <Plus className="w-4 h-4" />
              New Job Description
            </Button>
          </div>
        </Card>
      </motion.div>

      {selectedJobDescription && (
        <motion.div variants={item}>
          <Card className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/10 dark:to-emerald-900/10 border-green-200 dark:border-green-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                  <Check className="w-4 h-4 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-green-700 dark:text-green-300">Active Job Description</p>
                  <p className="text-lg font-bold text-gray-900 dark:text-white">{selectedJobDescription.title}</p>
                  {selectedJobDescription.company && <p className="text-sm text-gray-500 dark:text-gray-400">{selectedJobDescription.company}</p>}
                </div>
              </div>
              <button onClick={() => setSelectedJobDescription(null)} className="text-xs text-green-600 dark:text-green-400 hover:underline">Deselect</button>
            </div>
          </Card>
        </motion.div>
      )}

      <motion.div variants={item}>
        {jobs.length === 0 ? (
          <Card>
            <EmptyState
              icon={Briefcase}
              title="No Job Descriptions"
              description="Create a job description to target your resume generation"
              actionLabel="Create First Job Description"
              onAction={() => setShowCreateModal(true)}
            />
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {jobs.map((job, i) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className={`bg-white dark:bg-slate-800 rounded-xl border p-5 hover:shadow-md transition-all ${
                  selectedJobDescription?.id === job.id
                    ? 'border-green-500 ring-2 ring-green-500/20'
                    : 'border-gray-100 dark:border-gray-700'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                    <Briefcase size={20} className="text-purple-600 dark:text-purple-400" />
                  </div>
                  {selectedJobDescription?.id === job.id && (
                    <span className="text-xs font-medium px-2 py-1 rounded-full bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                      Selected
                    </span>
                  )}
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{job.title}</h3>
                {job.company && <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">{job.company}</p>}
                <p className="text-xs text-gray-400 dark:text-gray-500 mb-4 line-clamp-2">{job.description}</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleSelect(job)}
                    className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      selectedJobDescription?.id === job.id
                        ? 'bg-green-600 text-white'
                        : 'bg-indigo-600 text-white hover:bg-indigo-700'
                    }`}
                  >
                    {selectedJobDescription?.id === job.id ? <Check size={14} /> : 'Select'}
                  </button>
                  <button
                    onClick={() => handleDelete(job.id)}
                    disabled={deleting === job.id}
                    className="flex items-center justify-center px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 transition-colors"
                  >
                    {deleting === job.id ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>

      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Create Job Description" size="lg">
        <div className="space-y-4">
          <JobDescriptionInput onChange={setFormData} />
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" onClick={() => setShowCreateModal(false)}>Cancel</Button>
            <Button variant="primary" onClick={handleCreate} disabled={creating}>
              {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
              {creating ? 'Creating...' : 'Create'}
            </Button>
          </div>
        </div>
      </Modal>
    </motion.div>
  );
}
