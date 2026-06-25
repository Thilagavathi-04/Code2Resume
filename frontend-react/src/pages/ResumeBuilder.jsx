import { useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Save, Download, Eye, Edit3 } from 'lucide-react';
import Button from '../components/ui/Button';
import ResumeForm from '../components/resume/ResumeForm';
import ResumePreview from '../components/resume/ResumePreview';
import FormattingToolbar from '../components/resume/FormattingToolbar';
import v2 from '../api/v2';
import { useResumeStore } from '../store/resumeStore';
import { useToastStore } from '../components/ui/Toast';

const STORAGE_KEY = 'resume-builder-data';

const defaultData = {
  personal: { name: '', email: '', phone: '', location: '', website: '', linkedin: '' },
  summary: '',
  skills: [],
  experience: [],
  education: [],
  certifications: [],
  projects: [],
};

const defaultFormatting = {
  name: { fontSize: 20, bold: true },
  sectionHeadings: { fontSize: 14, bold: true },
  body: { fontSize: 12, bold: false },
  experience: { fontSize: 12, bold: false },
  education: { fontSize: 12, bold: false },
  skills: { fontSize: 12, bold: false },
  projects: { fontSize: 12, bold: false },
  certifications: { fontSize: 12, bold: false },
};

const defaultSectionOrder = ['personal', 'summary', 'skills', 'experience', 'education', 'certifications', 'projects'];

function mapResumeToFormData(resume) {
  const content = resume.content || {};
  const asArray = (v) => Array.isArray(v) ? v : [];
  return {
    personal: content.personal || { name: '', email: '', phone: '', location: '', website: '', linkedin: '' },
    summary: resume.summary || '',
    skills: asArray(resume.skills).map(s => ({ name: s.name, proficiency: s.proficiency || 'intermediate', category: s.category || '' })),
    experience: asArray(resume.experiences).map(e => ({
      company: e.company,
      position: e.position,
      startDate: e.start_date || '',
      endDate: e.end_date || '',
      description: e.description || '',
      highlights: e.highlights || [],
    })),
    education: asArray(resume.educations).map(e => ({
      institution: e.institution,
      degree: e.degree || '',
      field: e.field_of_study || '',
      startDate: e.start_date || '',
      endDate: e.end_date || '',
      gpa: e.gpa || '',
    })),
    certifications: asArray(resume.certifications).map(c => ({
      name: c.name,
      issuer: c.issuer || '',
    })),
    projects: asArray(resume.projects).map(p => ({
      name: p.name,
      description: p.description || '',
      technologies: Array.isArray(p.technologies) ? p.technologies.join(', ') : (p.technologies || ''),
      link: p.live_url || p.github_url || '',
    })),
  };
}

function mapResumeToFormatting(resume) {
  const content = resume.content || {};
  return content.formatting || { ...defaultFormatting };
}

function mapResumeToSectionOrder(resume) {
  const content = resume.content || {};
  return content.sectionOrder || [...defaultSectionOrder];
}

function mapFormDataToPayload(data, title, template, formatting, sectionOrder) {
  return {
    title: title || 'Untitled Resume',
    template,
    summary: data.summary || '',
    content: {
      personal: data.personal,
      formatting,
      sectionOrder,
    },
  };
}

export default function ResumeBuilder() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const addToast = useToastStore(s => s.addToast);
  const { selectedTemplate, setSelectedTemplate } = useResumeStore();

  const [data, setData] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? { ...defaultData, ...JSON.parse(saved) } : defaultData;
    } catch {
      return defaultData;
    }
  });
  const [formatting, setFormatting] = useState({ ...defaultFormatting });
  const [sectionOrder, setSectionOrder] = useState([...defaultSectionOrder]);
  const [resumeId, setResumeId] = useState(null);
  const [resumeTitle, setResumeTitle] = useState('Untitled Resume');
  const [mobileTab, setMobileTab] = useState('form');
  const [saveStatus, setSaveStatus] = useState('saved');
  const [loadingResume, setLoadingResume] = useState(false);
  const saveTimerRef = useRef(null);

  const loadResume = useCallback(async (id) => {
    setLoadingResume(true);
    try {
      const res = await v2.resumes.get(id);
      const resume = res.data || res;
      setData(mapResumeToFormData(resume));
      setFormatting(mapResumeToFormatting(resume));
      setSectionOrder(mapResumeToSectionOrder(resume));
      setResumeId(resume.id);
      setResumeTitle(resume.title || 'Untitled Resume');
      if (resume.template) setSelectedTemplate(resume.template);
      addToast({ type: 'success', message: 'Resume loaded successfully' });
    } catch {
      addToast({ type: 'error', message: 'Failed to load resume' });
    } finally {
      setLoadingResume(false);
    }
  }, [setSelectedTemplate, addToast]);

  useEffect(() => {
    const id = searchParams.get('resumeId');
    if (id) loadResume(id);
  }, [searchParams, loadResume]);

  useEffect(() => {
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        setSaveStatus('saved');
      } catch {
        setSaveStatus('error');
      }
    }, 1000);
    return () => {
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    };
  }, [data]);

  const handleDataChange = useCallback((newData) => {
    setData(newData);
    setSaveStatus('saving');
  }, []);

  const handleSave = async () => {
    try {
      const payload = mapFormDataToPayload(data, resumeTitle, selectedTemplate, formatting, sectionOrder);
      if (resumeId) {
        await v2.resumes.update(resumeId, payload);
      } else {
        const res = await v2.resumes.create(payload);
        const created = res.data || res;
        setResumeId(created.id);
        navigate(`/builder?resumeId=${created.id}`, { replace: true });
      }
      addToast({ type: 'success', message: 'Resume saved' });
      setSaveStatus('saved');
    } catch {
      addToast({ type: 'error', message: 'Failed to save resume' });
    }
  };

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'resume-data.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loadingResume) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <input
              type="text"
              value={resumeTitle}
              onChange={(e) => setResumeTitle(e.target.value)}
              className="text-2xl font-bold text-gray-900 dark:text-white bg-transparent border-none focus:outline-none focus:ring-0 p-0"
              placeholder="Untitled Resume"
            />
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Create and customize your professional resume
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full ${
              saveStatus === 'saved'
                ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                : 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
            }`}>
              <Save className="w-3 h-3" />
              {saveStatus === 'saved' ? 'Saved' : 'Saving...'}
            </span>
            <Button variant="primary" size="sm" onClick={handleSave}>
              <Save className="w-4 h-4" />
              {resumeId ? 'Update' : 'Save'}
            </Button>
          </div>
        </div>
      </div>

      <div className="lg:hidden flex gap-2">
        <Button
          variant={mobileTab === 'form' ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => setMobileTab('form')}
        >
          <Edit3 className="w-4 h-4" />
          Edit
        </Button>
        <Button
          variant={mobileTab === 'preview' ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => setMobileTab('preview')}
        >
          <Eye className="w-4 h-4" />
          Preview
        </Button>
        <Button variant="secondary" size="sm" onClick={handleExport}>
          <Download className="w-4 h-4" />
          Export
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className={`space-y-4 max-h-[calc(100vh-200px)] overflow-y-auto pr-2 ${mobileTab !== 'form' ? 'hidden lg:block' : ''}`}>
          <FormattingToolbar formatting={formatting} onChange={setFormatting} />
          <ResumeForm data={data} onChange={handleDataChange} sectionOrder={sectionOrder} onReorder={setSectionOrder} />
        </div>

        <div className={`space-y-4 ${mobileTab !== 'preview' ? 'hidden lg:block' : ''}`}>
          <div className="flex items-center justify-between">
            <select
              value={selectedTemplate}
              onChange={e => setSelectedTemplate(e.target.value)}
              className="px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="modern">Modern</option>
              <option value="professional">Professional</option>
              <option value="startup">Startup</option>
              <option value="minimal">Minimal</option>
              <option value="creative">Creative</option>
              <option value="executive">Executive</option>
              <option value="technical">Technical</option>
            </select>
            <Button variant="primary" size="sm" onClick={handleExport} className="hidden lg:inline-flex">
              <Download className="w-4 h-4" />
              Export
            </Button>
          </div>
          <ResumePreview data={data} template={selectedTemplate} formatting={formatting} sectionOrder={sectionOrder} />
        </div>
      </div>
    </div>
  );
}
