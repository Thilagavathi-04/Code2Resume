import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import v2 from '../api/v2';
import { generateResume } from '../api/resume';
import { useToastStore } from '../components/ui/Toast';
import { FileText, Trash2, Loader2, Plus, Edit3, Download, Upload, Eye, X } from 'lucide-react';
import Modal from '../components/ui/Modal';
import Button from '../components/ui/Button';
import ResumePreview from '../components/resume/ResumePreview';

export default function Resumes() {
  const navigate = useNavigate();
  const addToast = useToastStore(s => s.addToast);
  const fileInputRef = useRef(null);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(null);
  const [downloading, setDownloading] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generateQuery, setGenerateQuery] = useState('');
  const [previewResume, setPreviewResume] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewTemplate, setPreviewTemplate] = useState('modern');

  const loadResumes = useCallback(async () => {
    try {
      const res = await v2.resumes.list();
      const data = res.data || res;
      setResumes(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to load resumes:', error);
      setResumes([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadResumes(); }, [loadResumes]);

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this resume?')) return;
    setDeleting(id);
    try {
      await v2.resumes.delete(id);
      setResumes(resumes.filter(r => r.id !== id));
      addToast({ type: 'success', message: 'Resume deleted' });
    } catch {
      addToast({ type: 'error', message: 'Failed to delete resume' });
    } finally {
      setDeleting(null);
    }
  };

  const handleDownload = async (resume) => {
    setDownloading(resume.id);
    try {
      const res = await v2.resumes.export(resume.id);
      const blob = res.data || res;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${(resume.title || 'resume').replace(/\s+/g, '_').toLowerCase()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      addToast({ type: 'success', message: 'Resume downloaded' });
    } catch {
      addToast({ type: 'error', message: 'Failed to download resume' });
    } finally {
      setDownloading(null);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const supportedExtensions = ['.json', '.pdf', '.docx', '.tex', '.latex'];
    const hasValidExtension = supportedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    if (!hasValidExtension) {
      addToast({ type: 'error', message: 'Supported formats: JSON, PDF, DOCX, TeX' });
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      addToast({ type: 'error', message: 'File too large. Maximum size is 10MB.' });
      return;
    }
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      await v2.resumes.import(formData);
      addToast({ type: 'success', message: 'Resume uploaded successfully' });
      await loadResumes();
    } catch (err) {
      const msg = err?.response?.data?.detail || err?.message || 'Failed to upload resume';
      addToast({ type: 'error', message: msg });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleViewEdit = (resume) => {
    navigate(`/builder?resumeId=${resume.id}`);
  };

  const handlePreview = async (resume) => {
    setPreviewLoading(true);
    try {
      const res = await v2.resumes.get(resume.id);
      const data = res.data || res;
      const content = data.content || {};
      setPreviewResume({
        personal: content.personal || {},
        summary: data.summary || '',
        skills: data.skills || [],
        experience: data.experiences || [],
        education: data.educations || [],
        certifications: data.certifications || [],
        projects: data.projects || [],
      });
      setPreviewTemplate(data.template || 'modern');
    } catch {
      addToast({ type: 'error', message: 'Failed to load resume preview' });
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!generateQuery.trim()) return;
    setGenerating(true);
    try {
      const response = await generateResume(generateQuery);
      if (response.success) {
        const title = generateQuery.length > 50 ? generateQuery.slice(0, 50) + '...' : generateQuery;
        await v2.resumes.create({
          title,
          template: 'modern',
          summary: response.message || 'Generated resume',
        });
        addToast({ type: 'success', message: response.message || 'Resume generated!' });
        setShowGenerateModal(false);
        setGenerateQuery('');
        await loadResumes();
      } else {
        throw new Error(response.detail || 'Failed to generate resume');
      }
    } catch (error) {
      addToast({ type: 'error', message: error.message || 'Failed to generate resume' });
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-indigo-500" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Resumes</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">View, generate, upload, and manage your resumes</p>
        </div>
        <div className="flex gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".json,.pdf,.docx,.tex,.latex"
            onChange={handleUpload}
            className="hidden"
          />
          <Button variant="secondary" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
            {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            Upload Resume
          </Button>
          <Button variant="primary" onClick={() => setShowGenerateModal(true)}>
            <Plus className="w-4 h-4" />
            Generate Resume
          </Button>
        </div>
      </div>

      {resumes.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 bg-gray-50 dark:bg-slate-900 rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-700">
          <FileText size={40} className="text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">No Resumes Yet</h3>
          <p className="text-gray-500 dark:text-gray-400 max-w-md text-center mb-4">Generate, upload, or create your first resume to get started</p>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => fileInputRef.current?.click()}>
              <Upload className="w-4 h-4" />
              Upload Resume
            </Button>
            <Button variant="primary" onClick={() => setShowGenerateModal(true)}>
              <Plus className="w-4 h-4" />
              Generate Resume
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {resumes.map((resume, index) => (
            <div
              key={resume.id}
              className="bg-white dark:bg-slate-800 rounded-xl border border-gray-100 dark:border-gray-700 p-5 hover:shadow-md transition-shadow"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                  <FileText size={20} className="text-indigo-600 dark:text-indigo-400" />
                </div>
                <span className="text-xs text-gray-400 dark:text-gray-500">{resume.created_at ? new Date(resume.created_at).toLocaleDateString() : 'Recent'}</span>
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1 truncate">{resume.title || 'Untitled Resume'}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{resume.target_role || 'Resume'}</p>
              <div className="flex gap-2">
                <button
                  onClick={() => handleViewEdit(resume)}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Edit3 size={14} />
                  Edit
                </button>
                <button
                  onClick={() => handlePreview(resume)}
                  disabled={previewLoading}
                  className="flex items-center justify-center px-3 py-2 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 text-sm font-medium rounded-lg hover:bg-purple-200 dark:hover:bg-purple-900/50 transition-colors"
                  title="Display resume"
                >
                  <Eye size={14} />
                </button>
                <button
                  onClick={() => handleDownload(resume)}
                  disabled={downloading === resume.id}
                  className="flex items-center justify-center px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  title="Download resume"
                >
                  {downloading === resume.id ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
                </button>
                <button
                  onClick={() => handleDelete(resume.id)}
                  disabled={deleting === resume.id}
                  className="flex items-center justify-center px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 transition-colors"
                >
                  {deleting === resume.id ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={showGenerateModal} onClose={() => setShowGenerateModal(false)} title="Generate Resume" size="md">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              Describe the resume you want
            </label>
            <textarea
              value={generateQuery}
              onChange={(e) => setGenerateQuery(e.target.value)}
              placeholder="e.g. Generate ML engineer resume, or Create a full stack developer resume..."
              rows={4}
              className="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            />
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
              The AI will generate a LaTeX resume based on your analyzed GitHub projects
            </p>
          </div>
          <div className="flex gap-2 justify-end">
            <Button variant="secondary" onClick={() => setShowGenerateModal(false)}>Cancel</Button>
            <Button variant="primary" onClick={handleGenerate} disabled={!generateQuery.trim() || generating}>
              {generating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating...
                </>
              ) : (
                'Generate'
              )}
            </Button>
          </div>
        </div>
      </Modal>

      <Modal isOpen={!!previewResume} onClose={() => setPreviewResume(null)} title="Resume Preview" size="lg">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500 dark:text-gray-400">Template:</span>
            <select
              value={previewTemplate}
              onChange={(e) => setPreviewTemplate(e.target.value)}
              className="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="modern">Modern</option>
              <option value="professional">Professional</option>
              <option value="startup">Startup</option>
              <option value="minimal">Minimal</option>
              <option value="creative">Creative</option>
              <option value="executive">Executive</option>
              <option value="technical">Technical</option>
            </select>
          </div>
          <div className="max-h-[60vh] overflow-y-auto rounded-xl border border-gray-100 dark:border-gray-700">
            <ResumePreview data={previewResume} template={previewTemplate} />
          </div>
        </div>
      </Modal>
    </div>
  );
}
