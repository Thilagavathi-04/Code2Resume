import { useState } from 'react';
import { User, FileText, Code2, Briefcase, GraduationCap, Award, FolderOpen, Plus, Trash2, ChevronUp, ChevronDown, Sparkles, Loader2 } from 'lucide-react';
import SectionEditor from './SectionEditor';
import Button from '../ui/Button';
import v2 from '../../api/v2';

const inputClass = "w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent";
const textareaClass = `${inputClass} resize-none`;

const PROFICIENCIES = ['beginner', 'intermediate', 'advanced', 'expert'];

const SECTION_CONFIG = {
  personal: { title: 'Personal Information', icon: User },
  summary: { title: 'Professional Summary', icon: FileText },
  skills: { title: 'Skills', icon: Code2 },
  experience: { title: 'Experience', icon: Briefcase },
  education: { title: 'Education', icon: GraduationCap },
  certifications: { title: 'Certifications', icon: Award },
  projects: { title: 'Projects', icon: FolderOpen },
};

const DEFAULT_ORDER = ['personal', 'summary', 'skills', 'experience', 'education', 'certifications', 'projects'];

export default function ResumeForm({ data, onChange, sectionOrder, onReorder, className = '' }) {
  const [enhancingSummary, setEnhancingSummary] = useState(false);
  const [enhancingProject, setEnhancingProject] = useState(null);

  const updateField = (section, field, value, index) => {
    const updated = { ...data };
    if (index !== undefined) {
      updated[section] = [...(updated[section] || [])];
      updated[section][index] = { ...updated[section][index], [field]: value };
    } else {
      updated[section] = { ...(updated[section] || {}), [field]: value };
    }
    onChange(updated);
  };

  const addItem = (section, template) => {
    const updated = { ...data };
    updated[section] = [...(updated[section] || []), template];
    onChange(updated);
  };

  const removeItem = (section, index) => {
    const updated = { ...data };
    updated[section] = (updated[section] || []).filter((_, i) => i !== index);
    onChange(updated);
  };

  const personal = data.personal || {};
  const summary = data.summary || '';
  const skills = data.skills || [];
  const experience = data.experience || [];
  const education = data.education || [];
  const certifications = data.certifications || [];
  const projects = data.projects || [];

  const orderedSections = sectionOrder || DEFAULT_ORDER;

  const moveSection = (index, direction) => {
    if (!onReorder) return;
    const newOrder = [...orderedSections];
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= newOrder.length) return;
    [newOrder[index], newOrder[newIndex]] = [newOrder[newIndex], newOrder[index]];
    onReorder(newOrder);
  };

  const handleEnhanceSummary = async () => {
    setEnhancingSummary(true);
    try {
      const skillNames = skills.map(s => s.name).filter(Boolean);
      const res = await v2.resumes.aiEnhance({
        text: summary,
        context: 'summary',
        skills: skillNames,
      });
      const enhanced = res.data?.enhanced_text || res.enhanced_text;
      if (enhanced) {
        onChange({ ...data, summary: enhanced });
      }
    } catch (err) {
      console.error('AI enhancement failed:', err);
    } finally {
      setEnhancingSummary(false);
    }
  };

  const handleAutoGenProject = async (index) => {
    setEnhancingProject(index);
    try {
      const proj = projects[index];
      const res = await v2.resumes.aiEnhance({
        text: '',
        context: 'project',
        project_name: proj.name || 'Unnamed Project',
        project_tech: proj.technologies || '',
      });
      const enhanced = res.data?.enhanced_text || res.enhanced_text;
      if (enhanced) {
        updateField('projects', 'description', enhanced, index);
      }
    } catch (err) {
      console.error('Auto-generate failed:', err);
    } finally {
      setEnhancingProject(null);
    }
  };

  const renderSectionContent = (sectionKey) => {
    switch (sectionKey) {
      case 'personal':
        return (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input className={inputClass} placeholder="Full Name" value={personal.name || ''} onChange={e => updateField('personal', 'name', e.target.value)} />
            <input className={inputClass} type="email" placeholder="Email" value={personal.email || ''} onChange={e => updateField('personal', 'email', e.target.value)} />
            <input className={inputClass} placeholder="Phone" value={personal.phone || ''} onChange={e => updateField('personal', 'phone', e.target.value)} />
            <input className={inputClass} placeholder="Location" value={personal.location || ''} onChange={e => updateField('personal', 'location', e.target.value)} />
            <input className={inputClass} placeholder="Website URL" value={personal.website || ''} onChange={e => updateField('personal', 'website', e.target.value)} />
            <input className={inputClass} placeholder="LinkedIn URL" value={personal.linkedin || ''} onChange={e => updateField('personal', 'linkedin', e.target.value)} />
          </div>
        );
      case 'summary':
        return (
          <>
            <textarea
              className={textareaClass}
              rows={4}
              placeholder="Write a brief professional summary..."
              value={summary}
              onChange={e => onChange({ ...data, summary: e.target.value })}
            />
            <Button
              variant="secondary"
              size="sm"
              className="w-full"
              onClick={handleEnhanceSummary}
              disabled={enhancingSummary}
            >
              {enhancingSummary ? (
                <><Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" /> Enhancing...</>
              ) : (
                <><Sparkles className="w-3.5 h-3.5 mr-1.5" /> Enhance with AI</>
              )}
            </Button>
          </>
        );
      case 'skills':
        return skills.length === 0 ? (
          <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-2">No skills added yet</p>
        ) : (
          skills.map((skill, i) => (
            <div key={i} className="flex items-center gap-2">
              <input className={`${inputClass} flex-1`} placeholder="Skill name" value={skill.name || ''} onChange={e => updateField('skills', 'name', e.target.value, i)} />
              <select className={`${inputClass} w-32`} value={skill.proficiency || 'intermediate'} onChange={e => updateField('skills', 'proficiency', e.target.value, i)}>
                {PROFICIENCIES.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
              <button onClick={() => removeItem('skills', i)} className="p-1.5 text-gray-400 hover:text-red-500 transition-colors">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))
        );
      case 'experience':
        return experience.length === 0 ? (
          <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-2">No experience added yet</p>
        ) : (
          experience.map((exp, i) => (
            <div key={i} className="p-3 rounded-lg border border-gray-100 dark:border-gray-700 space-y-2 relative">
              <button onClick={() => removeItem('experience', i)} className="absolute top-2 right-2 p-1 text-gray-400 hover:text-red-500 transition-colors">
                <Trash2 className="w-3.5 h-3.5" />
              </button>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <input className={inputClass} placeholder="Company" value={exp.company || ''} onChange={e => updateField('experience', 'company', e.target.value, i)} />
                <input className={inputClass} placeholder="Position" value={exp.position || ''} onChange={e => updateField('experience', 'position', e.target.value, i)} />
                <input className={inputClass} type="month" placeholder="Start" value={exp.startDate || ''} onChange={e => updateField('experience', 'startDate', e.target.value, i)} />
                <input className={inputClass} type="month" placeholder="End" value={exp.endDate || ''} onChange={e => updateField('experience', 'endDate', e.target.value, i)} />
              </div>
              <textarea className={textareaClass} rows={2} placeholder="Description" value={exp.description || ''} onChange={e => updateField('experience', 'description', e.target.value, i)} />
            </div>
          ))
        );
      case 'education':
        return education.length === 0 ? (
          <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-2">No education added yet</p>
        ) : (
          education.map((edu, i) => (
            <div key={i} className="p-3 rounded-lg border border-gray-100 dark:border-gray-700 space-y-2 relative">
              <button onClick={() => removeItem('education', i)} className="absolute top-2 right-2 p-1 text-gray-400 hover:text-red-500 transition-colors">
                <Trash2 className="w-3.5 h-3.5" />
              </button>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <input className={inputClass} placeholder="Institution" value={edu.institution || ''} onChange={e => updateField('education', 'institution', e.target.value, i)} />
                <input className={inputClass} placeholder="Degree" value={edu.degree || ''} onChange={e => updateField('education', 'degree', e.target.value, i)} />
                <input className={inputClass} placeholder="Field of Study" value={edu.field || ''} onChange={e => updateField('education', 'field', e.target.value, i)} />
                <input className={inputClass} placeholder="GPA" value={edu.gpa || ''} onChange={e => updateField('education', 'gpa', e.target.value, i)} />
                <input className={inputClass} type="month" placeholder="Start" value={edu.startDate || ''} onChange={e => updateField('education', 'startDate', e.target.value, i)} />
                <input className={inputClass} type="month" placeholder="End" value={edu.endDate || ''} onChange={e => updateField('education', 'endDate', e.target.value, i)} />
              </div>
            </div>
          ))
        );
      case 'certifications':
        return certifications.length === 0 ? (
          <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-2">No certifications added yet</p>
        ) : (
          certifications.map((cert, i) => (
            <div key={i} className="flex items-center gap-2">
              <input className={`${inputClass} flex-1`} placeholder="Certification name" value={cert.name || ''} onChange={e => updateField('certifications', 'name', e.target.value, i)} />
              <input className={`${inputClass} w-32`} placeholder="Issuer" value={cert.issuer || ''} onChange={e => updateField('certifications', 'issuer', e.target.value, i)} />
              <button onClick={() => removeItem('certifications', i)} className="p-1.5 text-gray-400 hover:text-red-500 transition-colors">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))
        );
      case 'projects':
        return projects.length === 0 ? (
          <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-2">No projects added yet</p>
        ) : (
          projects.map((proj, i) => (
            <div key={i} className="p-3 rounded-lg border border-gray-100 dark:border-gray-700 space-y-2 relative">
              <button onClick={() => removeItem('projects', i)} className="absolute top-2 right-2 p-1 text-gray-400 hover:text-red-500 transition-colors">
                <Trash2 className="w-3.5 h-3.5" />
              </button>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <input className={inputClass} placeholder="Project name" value={proj.name || ''} onChange={e => updateField('projects', 'name', e.target.value, i)} />
                <input className={inputClass} placeholder="Technologies" value={proj.technologies || ''} onChange={e => updateField('projects', 'technologies', e.target.value, i)} />
              </div>
              <textarea className={textareaClass} rows={2} placeholder="Description (2 lines recommended)" value={proj.description || ''} onChange={e => updateField('projects', 'description', e.target.value, i)} />
              <div className="flex gap-2">
                <button
                  onClick={() => handleAutoGenProject(i)}
                  disabled={enhancingProject === i || !proj.name}
                  className="flex items-center gap-1 text-xs px-2 py-1 rounded-md bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors disabled:opacity-50"
                >
                  {enhancingProject === i ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                  {proj.description ? 'Enhance' : 'Generate'}
                </button>
              </div>
              <input className={inputClass} placeholder="Link URL" value={proj.link || ''} onChange={e => updateField('projects', 'link', e.target.value, i)} />
            </div>
          ))
        );
      default:
        return null;
    }
  };

  const getAddHandler = (sectionKey) => {
    switch (sectionKey) {
      case 'skills': return () => addItem('skills', { name: '', proficiency: 'intermediate', category: '' });
      case 'experience': return () => addItem('experience', { company: '', position: '', startDate: '', endDate: '', description: '', highlights: [] });
      case 'education': return () => addItem('education', { institution: '', degree: '', field: '', startDate: '', endDate: '', gpa: '' });
      case 'certifications': return () => addItem('certifications', { name: '', issuer: '', date: '', url: '' });
      case 'projects': return () => addItem('projects', { name: '', description: '', technologies: '', link: '' });
      default: return undefined;
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {orderedSections.map((sectionKey, index) => {
        const config = SECTION_CONFIG[sectionKey];
        if (!config) return null;
        const Icon = config.icon;
        const canMoveUp = onReorder && index > 0;
        const canMoveDown = onReorder && index < orderedSections.length - 1;

        return (
          <SectionEditor
            key={sectionKey}
            title={config.title}
            icon={Icon}
            onAdd={getAddHandler(sectionKey)}
            addLabel={sectionKey === 'skills' ? 'Add Skill' : 'Add'}
            headerExtra={
              onReorder && (
                <div className="flex items-center gap-0.5">
                  <button
                    onClick={(e) => { e.stopPropagation(); moveSection(index, -1); }}
                    disabled={!canMoveUp}
                    className="p-0.5 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    title="Move up"
                  >
                    <ChevronUp className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); moveSection(index, 1); }}
                    disabled={!canMoveDown}
                    className="p-0.5 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    title="Move down"
                  >
                    <ChevronDown className="w-3.5 h-3.5" />
                  </button>
                </div>
              )
            }
          >
            {renderSectionContent(sectionKey)}
          </SectionEditor>
        );
      })}
    </div>
  );
}
