import { useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Save, Download, Eye, Edit3, FileJson, FileText, X } from 'lucide-react';
import Button from '../components/ui/Button';
import ResumeForm from '../components/resume/ResumeForm';
import ResumePreview from '../components/resume/ResumePreview';
import FormattingToolbar from '../components/resume/FormattingToolbar';
import v2 from '../api/v2';
import { useResumeStore } from '../store/resumeStore';
import { useToastStore } from '../components/ui/Toast';
import { exportResumePDF } from '../api/github';

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
  const [showExportModal, setShowExportModal] = useState(false);
  const [exporting, setExporting] = useState(false);
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
      let id = resumeId;
      if (id) {
        await v2.resumes.update(id, payload);
        await Promise.all([
          v2.resumes.clearExperiences(id),
          v2.resumes.clearEducations(id),
          v2.resumes.clearSkills(id),
          v2.resumes.clearCertifications(id),
          v2.resumes.clearProjects(id),
        ]);
      } else {
        const res = await v2.resumes.create(payload);
        const created = res.data || res;
        id = created.id;
        setResumeId(id);
        navigate(`/builder?resumeId=${id}`, { replace: true });
      }

      const addAll = [];
      for (const exp of (data.experience || [])) {
        if (exp.company || exp.position) {
          addAll.push(v2.resumes.addExperience(id, {
            company: exp.company || '',
            position: exp.position || '',
            start_date: exp.startDate || '',
            end_date: exp.endDate || '',
            description: exp.description || '',
            highlights: exp.highlights || [],
          }));
        }
      }
      for (const edu of (data.education || [])) {
        if (edu.institution) {
          addAll.push(v2.resumes.addEducation(id, {
            institution: edu.institution,
            degree: edu.degree || '',
            field_of_study: edu.field || '',
            start_date: edu.startDate || '',
            end_date: edu.endDate || '',
            gpa: edu.gpa || '',
          }));
        }
      }
      for (const skill of (data.skills || [])) {
        if (skill.name) {
          addAll.push(v2.resumes.addSkill(id, {
            name: skill.name,
            proficiency: skill.proficiency || 'intermediate',
            category: skill.category || '',
          }));
        }
      }
      for (const cert of (data.certifications || [])) {
        if (cert.name) {
          addAll.push(v2.resumes.addCertification(id, {
            name: cert.name,
            issuer: cert.issuer || '',
          }));
        }
      }
      for (const proj of (data.projects || [])) {
        if (proj.name) {
          const techs = typeof proj.technologies === 'string'
            ? proj.technologies.split(',').map(t => t.trim()).filter(Boolean)
            : (proj.technologies || []);
          addAll.push(v2.resumes.addProject(id, {
            name: proj.name,
            description: proj.description || '',
            technologies: techs,
            highlights: proj.highlights || [],
            github_url: proj.link || '',
          }));
        }
      }
      await Promise.all(addAll);

      addToast({ type: 'success', message: 'Resume saved' });
      setSaveStatus('saved');
    } catch {
      addToast({ type: 'error', message: 'Failed to save resume' });
    }
  };

  const handleExport = () => {
    setShowExportModal(true);
  };

  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'resume-data.json';
    a.click();
    URL.revokeObjectURL(url);
    setShowExportModal(false);
    addToast({ type: 'success', message: 'JSON exported!' });
  };

  const handleExportPDF = async () => {
    setExporting(true);
    try {
      const blob = await exportResumePDF(data);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `resume_${resumeTitle.replace(/\s+/g, '_')}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      setShowExportModal(false);
      addToast({ type: 'success', message: 'PDF exported!' });
    } catch (err) {
      addToast({ type: 'error', message: 'Failed to export PDF' });
    } finally {
      setExporting(false);
    }
  };

  if (loadingResume) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-gray-500 border-t-transparent rounded-full" />
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
                ? 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400'
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
              className="px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-gray-500"
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

      {showExportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => !exporting && setShowExportModal(false)} />
          <div className="relative bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 p-6 w-full max-w-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Export Resume</h3>
              <button onClick={() => !exporting && setShowExportModal(false)} className="p-1 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700">
                <X size={18} />
              </button>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">Choose export format:</p>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={handleExportJSON}
                disabled={exporting}
                className="flex flex-col items-center gap-2 p-4 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-500 transition-all disabled:opacity-50"
              >
                <FileJson className="w-8 h-8 text-gray-600 dark:text-gray-400" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">JSON</span>
                <span className="text-xs text-gray-400">Raw data</span>
              </button>
              <button
                onClick={handleExportPDF}
                disabled={exporting}
                className="flex flex-col items-center gap-2 p-4 rounded-xl border-2 border-gray-900 dark:border-gray-400 bg-gray-900 dark:bg-gray-400 text-white transition-all disabled:opacity-50"
              >
                <FileText className="w-8 h-8" />
                <span className="text-sm font-medium">PDF</span>
                <span className="text-xs opacity-70">Print ready</span>
              </button>
            </div>
            {exporting && (
              <div className="flex items-center justify-center gap-2 mt-4 text-sm text-gray-500">
                <div className="animate-spin w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full" />
                Generating PDF...
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
