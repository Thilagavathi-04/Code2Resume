import { Mail, Phone, MapPin, Globe, Linkedin } from 'lucide-react';

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const [year, month] = dateStr.split('-');
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return `${months[parseInt(month, 10) - 1] || ''} ${year}`;
};

function SectionTitle({ children, template }) {
  const styles = {
    modern: 'text-indigo-600 dark:text-indigo-400 uppercase tracking-wider border-b border-gray-100 dark:border-gray-700 pb-1',
    professional: 'text-gray-900 dark:text-white uppercase tracking-wider border-l-4 border-gray-800 dark:border-gray-200 pl-3',
    startup: 'text-white bg-emerald-600 dark:bg-emerald-500 px-3 py-1 rounded-lg inline-block',
    minimal: 'text-gray-900 dark:text-white',
    creative: 'text-fuchsia-600 dark:text-fuchsia-400 font-extrabold uppercase tracking-widest text-xs',
    executive: 'text-slate-800 dark:text-slate-200 uppercase tracking-wider border-b-2 border-slate-800 dark:border-slate-200 pb-1',
    technical: 'text-cyan-600 dark:text-cyan-400 font-mono uppercase tracking-wider text-xs',
  };
  return <h2 className={`text-sm font-bold mb-2 ${styles[template] || styles.modern}`}>{children}</h2>;
}

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

const SECTION_RENDERERS = {
  personal: null,
  summary: (data, fmt, Template) => {
    if (!data.summary) return null;
    return { key: 'summary', content: (
      <div>
        <SectionTitle template={Template}>Professional Summary</SectionTitle>
        <p className="text-gray-600 dark:text-gray-300 leading-relaxed" style={{ fontSize: `${fmt.body.fontSize}px`, fontWeight: fmt.body.bold ? 'bold' : 'normal' }}>{data.summary}</p>
      </div>
    )};
  },
  skills: (data, fmt, Template) => {
    if (!data.skills.length) return null;
    return { key: 'skills', content: (
      <div>
        <SectionTitle template={Template}>Skills</SectionTitle>
        <div className="flex flex-wrap gap-1.5">
          {data.skills.map((skill, i) => (
            <span key={i} className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded font-medium" style={{ fontSize: `${fmt.skills.fontSize}px` }}>{skill.name}</span>
          ))}
        </div>
      </div>
    )};
  },
  experience: (data, fmt, Template) => {
    if (!data.experience.length) return null;
    return { key: 'experience', content: (
      <div>
        <SectionTitle template={Template}>Experience</SectionTitle>
        <div className="space-y-3">
          {data.experience.map((exp, i) => (
            <div key={i}>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.experience.fontSize}px` }}>{exp.position || 'Position'}</h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400">{exp.company || 'Company'}</p>
                </div>
                <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">{formatDate(exp.startDate)} – {formatDate(exp.endDate) || 'Present'}</span>
              </div>
              {exp.description && <p className="text-gray-600 dark:text-gray-400 mt-1 leading-relaxed" style={{ fontSize: `${fmt.experience.fontSize - 1}px` }}>{exp.description}</p>}
            </div>
          ))}
        </div>
      </div>
    )};
  },
  education: (data, fmt, Template) => {
    if (!data.education.length) return null;
    return { key: 'education', content: (
      <div>
        <SectionTitle template={Template}>Education</SectionTitle>
        <div className="space-y-3">
          {data.education.map((edu, i) => (
            <div key={i} className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.education.fontSize}px` }}>{edu.degree || 'Degree'} {edu.field && `in ${edu.field}`}</h3>
                <p className="text-xs text-gray-600 dark:text-gray-400">{edu.institution || 'Institution'}</p>
                {edu.gpa && <p className="text-xs text-gray-400 dark:text-gray-500">GPA: {edu.gpa}</p>}
              </div>
              <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">{formatDate(edu.startDate)} – {formatDate(edu.endDate)}</span>
            </div>
          ))}
        </div>
      </div>
    )};
  },
  certifications: (data, fmt, Template) => {
    if (!data.certifications.length) return null;
    return { key: 'certifications', content: (
      <div>
        <SectionTitle template={Template}>Certifications</SectionTitle>
        <div className="space-y-1">
          {data.certifications.map((cert, i) => (
            <div key={i} className="flex items-center justify-between">
              <span className="text-gray-900 dark:text-white font-medium" style={{ fontSize: `${fmt.certifications.fontSize}px` }}>{cert.name}</span>
              <span className="text-xs text-gray-400 dark:text-gray-500">{cert.issuer}</span>
            </div>
          ))}
        </div>
      </div>
    )};
  },
  projects: (data, fmt, Template) => {
    if (!data.projects.length) return null;
    return { key: 'projects', content: (
      <div>
        <SectionTitle template={Template}>Projects</SectionTitle>
        <div className="space-y-3">
          {data.projects.map((proj, i) => (
            <div key={i}>
              <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.projects.fontSize}px` }}>{proj.name || 'Project'}</h3>
              {proj.technologies && <p className="text-xs text-indigo-600 dark:text-indigo-400">{proj.technologies}</p>}
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 min-h-[2em] leading-relaxed">{proj.description || 'Project description'}</p>
            </div>
          ))}
        </div>
      </div>
    )};
  },
};

const DEFAULT_SECTION_ORDER = ['personal', 'summary', 'skills', 'experience', 'education', 'certifications', 'projects'];

function SectionWrapper({ sectionKey, formatting, sectionOrder, children }) {
  if (sectionOrder && !sectionOrder.includes(sectionKey)) return null;
  return children;
}

function getSectionStyle(sectionKey, formatting) {
  const fmt = formatting?.[sectionKey] || defaultFormatting[sectionKey] || defaultFormatting.body;
  return { fontSize: `${fmt.fontSize}px`, fontWeight: fmt.bold ? 'bold' : 'normal' };
}

function ModernTemplate({ personal, summary, skills, experience, education, certifications, projects, formatting }) {
  const fmt = { ...defaultFormatting, ...formatting };
  return (
    <div className="p-6 space-y-5">
      {personal.name && (
        <div className="text-center border-b border-gray-100 dark:border-gray-700 pb-4">
          <h1 style={{ fontSize: `${fmt.name.fontSize}px`, fontWeight: fmt.name.bold ? 'bold' : 'normal' }} className="text-gray-900 dark:text-white">{personal.name}</h1>
          <div className="flex items-center justify-center gap-4 mt-2 flex-wrap">
            {personal.email && <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400"><Mail className="w-3 h-3" /> {personal.email}</span>}
            {personal.phone && <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400"><Phone className="w-3 h-3" /> {personal.phone}</span>}
            {personal.location && <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400"><MapPin className="w-3 h-3" /> {personal.location}</span>}
            {personal.website && <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400"><Globe className="w-3 h-3" /> {personal.website}</span>}
            {personal.linkedin && <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400"><Linkedin className="w-3 h-3" /> LinkedIn</span>}
          </div>
        </div>
      )}
      {summary && (
        <div>
          <SectionTitle template="modern" formatting={fmt}>Professional Summary</SectionTitle>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed" style={{ fontSize: `${fmt.body.fontSize}px`, fontWeight: fmt.body.bold ? 'bold' : 'normal' }}>{summary}</p>
        </div>
      )}
      {skills.length > 0 && (
        <div>
          <SectionTitle template="modern" formatting={fmt}>Skills</SectionTitle>
          <div className="flex flex-wrap gap-1.5">
            {skills.map((skill, i) => (
              <span key={i} className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded font-medium" style={{ fontSize: `${fmt.skills.fontSize}px` }}>{skill.name}</span>
            ))}
          </div>
        </div>
      )}
      {experience.length > 0 && (
        <div>
          <SectionTitle template="modern" formatting={fmt}>Experience</SectionTitle>
          <div className="space-y-3">
            {experience.map((exp, i) => (
              <div key={i}>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.experience.fontSize}px` }}>{exp.position || 'Position'}</h3>
                    <p className="text-xs text-gray-600 dark:text-gray-400">{exp.company || 'Company'}</p>
                  </div>
                  <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">{formatDate(exp.startDate)} – {formatDate(exp.endDate) || 'Present'}</span>
                </div>
                {exp.description && <p className="text-gray-600 dark:text-gray-400 mt-1 leading-relaxed" style={{ fontSize: `${fmt.experience.fontSize - 1}px` }}>{exp.description}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
      {education.length > 0 && (
        <div>
          <SectionTitle template="modern" formatting={fmt}>Education</SectionTitle>
          <div className="space-y-3">
            {education.map((edu, i) => (
              <div key={i} className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.education.fontSize}px` }}>{edu.degree || 'Degree'} {edu.field && `in ${edu.field}`}</h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400">{edu.institution || 'Institution'}</p>
                  {edu.gpa && <p className="text-xs text-gray-400 dark:text-gray-500">GPA: {edu.gpa}</p>}
                </div>
                <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">{formatDate(edu.startDate)} – {formatDate(edu.endDate)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {certifications.length > 0 && (
        <div>
          <SectionTitle template="modern" formatting={fmt}>Certifications</SectionTitle>
          <div className="space-y-1">
            {certifications.map((cert, i) => (
              <div key={i} className="flex items-center justify-between">
                <span className="text-gray-900 dark:text-white font-medium" style={{ fontSize: `${fmt.certifications.fontSize}px` }}>{cert.name}</span>
                <span className="text-xs text-gray-400 dark:text-gray-500">{cert.issuer}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {projects.length > 0 && (
        <div>
          <SectionTitle template="modern" formatting={fmt}>Projects</SectionTitle>
          <div className="space-y-3">
            {projects.map((proj, i) => (
              <div key={i}>
                <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.projects.fontSize}px` }}>{proj.name || 'Project'}</h3>
                {proj.technologies && <p className="text-xs text-indigo-600 dark:text-indigo-400">{proj.technologies}</p>}
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 min-h-[2em] leading-relaxed">{proj.description || 'Project description'}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ProfessionalTemplate({ personal, summary, skills, experience, education, certifications, projects, formatting }) {
  const fmt = { ...defaultFormatting, ...formatting };
  return (
    <div className="p-6 space-y-5">
      {personal.name && (
        <div className="bg-gray-800 dark:bg-gray-200 text-white dark:text-gray-800 -mx-6 -mt-6 px-6 py-4">
          <h1 style={{ fontSize: `${fmt.name.fontSize}px`, fontWeight: fmt.name.bold ? 'bold' : 'normal' }}>{personal.name}</h1>
          <div className="flex items-center gap-4 mt-2 flex-wrap text-gray-200 dark:text-gray-600">
            {personal.email && <span className="inline-flex items-center gap-1 text-xs"><Mail className="w-3 h-3" /> {personal.email}</span>}
            {personal.phone && <span className="inline-flex items-center gap-1 text-xs"><Phone className="w-3 h-3" /> {personal.phone}</span>}
            {personal.location && <span className="inline-flex items-center gap-1 text-xs"><MapPin className="w-3 h-3" /> {personal.location}</span>}
            {personal.website && <span className="inline-flex items-center gap-1 text-xs"><Globe className="w-3 h-3" /> {personal.website}</span>}
            {personal.linkedin && <span className="inline-flex items-center gap-1 text-xs"><Linkedin className="w-3 h-3" /> LinkedIn</span>}
          </div>
        </div>
      )}
      {summary && (
        <div>
          <SectionTitle template="professional" formatting={fmt}>Professional Summary</SectionTitle>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed pl-3" style={{ fontSize: `${fmt.body.fontSize}px`, fontWeight: fmt.body.bold ? 'bold' : 'normal' }}>{summary}</p>
        </div>
      )}
      {skills.length > 0 && (
        <div>
          <SectionTitle template="professional" formatting={fmt}>Skills</SectionTitle>
          <div className="pl-3 text-gray-600 dark:text-gray-300" style={{ fontSize: `${fmt.skills.fontSize}px` }}>
            {skills.map((s, i) => (
              <span key={i}>{s.name}{i < skills.length - 1 ? ', ' : ''}</span>
            ))}
          </div>
        </div>
      )}
      {experience.length > 0 && (
        <div>
          <SectionTitle template="professional" formatting={fmt}>Experience</SectionTitle>
          <div className="space-y-3 pl-3">
            {experience.map((exp, i) => (
              <div key={i} className="border-l-2 border-gray-200 dark:border-gray-700 pl-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.experience.fontSize}px` }}>{exp.position || 'Position'}</h3>
                    <p className="text-xs text-gray-600 dark:text-gray-400">{exp.company || 'Company'}</p>
                  </div>
                  <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">{formatDate(exp.startDate)} – {formatDate(exp.endDate) || 'Present'}</span>
                </div>
                {exp.description && <p className="text-gray-600 dark:text-gray-400 mt-1 leading-relaxed" style={{ fontSize: `${fmt.experience.fontSize - 1}px` }}>{exp.description}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
      {education.length > 0 && (
        <div>
          <SectionTitle template="professional" formatting={fmt}>Education</SectionTitle>
          <div className="space-y-3 pl-3">
            {education.map((edu, i) => (
              <div key={i} className="border-l-2 border-gray-200 dark:border-gray-700 pl-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.education.fontSize}px` }}>{edu.degree || 'Degree'} {edu.field && `in ${edu.field}`}</h3>
                    <p className="text-xs text-gray-600 dark:text-gray-400">{edu.institution || 'Institution'}</p>
                  </div>
                  <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">{formatDate(edu.startDate)} – {formatDate(edu.endDate)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      {certifications.length > 0 && (
        <div>
          <SectionTitle template="professional" formatting={fmt}>Certifications</SectionTitle>
          <div className="space-y-1 pl-3">
            {certifications.map((cert, i) => (
              <div key={i} className="flex items-center justify-between border-l-2 border-gray-200 dark:border-gray-700 pl-3">
                <span className="text-gray-900 dark:text-white font-medium" style={{ fontSize: `${fmt.certifications.fontSize}px` }}>{cert.name}</span>
                <span className="text-xs text-gray-400 dark:text-gray-500">{cert.issuer}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {projects.length > 0 && (
        <div>
          <SectionTitle template="professional" formatting={fmt}>Projects</SectionTitle>
          <div className="space-y-3 pl-3">
            {projects.map((proj, i) => (
              <div key={i} className="border-l-2 border-gray-200 dark:border-gray-700 pl-3">
                <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.projects.fontSize}px` }}>{proj.name || 'Project'}</h3>
                {proj.technologies && <p className="text-xs text-gray-500 dark:text-gray-400">{proj.technologies}</p>}
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 min-h-[2em] leading-relaxed">{proj.description || 'Project description'}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StartupTemplate({ personal, summary, skills, experience, education, certifications, projects, formatting }) {
  const fmt = { ...defaultFormatting, ...formatting };
  return (
    <div className="p-6 space-y-5">
      {personal.name && (
        <div className="flex items-center gap-4 pb-4 border-b border-gray-100 dark:border-gray-700">
          <div className="w-14 h-14 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400 text-xl font-bold flex-shrink-0">
            {personal.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 style={{ fontSize: `${fmt.name.fontSize}px`, fontWeight: fmt.name.bold ? 'bold' : 'normal' }} className="text-gray-900 dark:text-white">{personal.name}</h1>
            <div className="flex items-center gap-3 mt-1 flex-wrap text-xs text-gray-500 dark:text-gray-400">
              {personal.email && <span className="inline-flex items-center gap-1"><Mail className="w-3 h-3" /> {personal.email}</span>}
              {personal.phone && <span className="inline-flex items-center gap-1"><Phone className="w-3 h-3" /> {personal.phone}</span>}
              {personal.location && <span className="inline-flex items-center gap-1"><MapPin className="w-3 h-3" /> {personal.location}</span>}
            </div>
          </div>
        </div>
      )}
      {summary && (
        <div>
          <SectionTitle template="startup">About Me</SectionTitle>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed" style={{ fontSize: `${fmt.body.fontSize}px`, fontWeight: fmt.body.bold ? 'bold' : 'normal' }}>{summary}</p>
        </div>
      )}
      {skills.length > 0 && (
        <div>
          <SectionTitle template="startup">Skills</SectionTitle>
          <div className="grid grid-cols-2 gap-2">
            {skills.map((skill, i) => (
              <div key={i} className="px-3 py-1.5 bg-emerald-50 dark:bg-emerald-900/10 rounded-lg font-medium text-emerald-700 dark:text-emerald-300" style={{ fontSize: `${fmt.skills.fontSize}px` }}>
                {skill.name}
              </div>
            ))}
          </div>
        </div>
      )}
      {experience.length > 0 && (
        <div>
          <SectionTitle template="startup">Experience</SectionTitle>
          <div className="space-y-3">
            {experience.map((exp, i) => (
              <div key={i} className="p-3 bg-gray-50 dark:bg-slate-900 rounded-lg">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.experience.fontSize}px` }}>{exp.position || 'Position'}</h3>
                    <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">{exp.company || 'Company'}</p>
                  </div>
                  <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">{formatDate(exp.startDate)} – {formatDate(exp.endDate) || 'Present'}</span>
                </div>
                {exp.description && <p className="text-gray-600 dark:text-gray-400 mt-2 leading-relaxed" style={{ fontSize: `${fmt.experience.fontSize - 1}px` }}>{exp.description}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
      {education.length > 0 && (
        <div>
          <SectionTitle template="startup">Education</SectionTitle>
          <div className="space-y-2">
            {education.map((edu, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-slate-900 rounded-lg">
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.education.fontSize}px` }}>{edu.degree || 'Degree'} {edu.field && `in ${edu.field}`}</h3>
                  <p className="text-xs text-emerald-600 dark:text-emerald-400">{edu.institution || 'Institution'}</p>
                </div>
                <span className="text-xs text-gray-400 dark:text-gray-500">{formatDate(edu.startDate)} – {formatDate(edu.endDate)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {certifications.length > 0 && (
        <div>
          <SectionTitle template="startup">Certifications</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {certifications.map((cert, i) => (
              <div key={i} className="px-3 py-1.5 bg-emerald-50 dark:bg-emerald-900/10 rounded-lg">
                <span className="font-medium text-emerald-700 dark:text-emerald-300" style={{ fontSize: `${fmt.certifications.fontSize}px` }}>{cert.name}</span>
                {cert.issuer && <span className="text-xs text-gray-400 dark:text-gray-500 ml-1">· {cert.issuer}</span>}
              </div>
            ))}
          </div>
        </div>
      )}
      {projects.length > 0 && (
        <div>
          <SectionTitle template="startup">Projects</SectionTitle>
          <div className="grid grid-cols-1 gap-3">
            {projects.map((proj, i) => (
              <div key={i} className="p-3 bg-gray-50 dark:bg-slate-900 rounded-lg">
                <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.projects.fontSize}px` }}>{proj.name || 'Project'}</h3>
                {proj.technologies && <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-0.5">{proj.technologies}</p>}
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 min-h-[2em] leading-relaxed">{proj.description || 'Project description'}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MinimalTemplate({ personal, summary, skills, experience, education, certifications, projects, formatting }) {
  const fmt = { ...defaultFormatting, ...formatting };
  return (
    <div className="p-6 space-y-5">
      {personal.name && (
        <div className="text-center pb-4">
          <h1 style={{ fontSize: `${fmt.name.fontSize}px`, fontWeight: fmt.name.bold ? 'bold' : 'normal' }} className="text-gray-900 dark:text-white">{personal.name}</h1>
          <div className="flex items-center justify-center gap-3 mt-2 flex-wrap text-xs text-gray-400 dark:text-gray-500">
            {personal.email && <span>{personal.email}</span>}
            {personal.phone && <span>· {personal.phone}</span>}
            {personal.location && <span>· {personal.location}</span>}
            {personal.website && <span>· {personal.website}</span>}
          </div>
        </div>
      )}
      {summary && (
        <div>
          <SectionTitle template="minimal">Summary</SectionTitle>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed" style={{ fontSize: `${fmt.body.fontSize}px`, fontWeight: fmt.body.bold ? 'bold' : 'normal' }}>{summary}</p>
        </div>
      )}
      {skills.length > 0 && (
        <div>
          <SectionTitle template="minimal">Skills</SectionTitle>
          <p className="text-gray-600 dark:text-gray-300" style={{ fontSize: `${fmt.skills.fontSize}px` }}>
            {skills.map((s, i) => (
              <span key={i}>{s.name}{i < skills.length - 1 ? ' · ' : ''}</span>
            ))}
          </p>
        </div>
      )}
      {experience.length > 0 && (
        <div>
          <SectionTitle template="minimal">Experience</SectionTitle>
          <div className="space-y-3">
            {experience.map((exp, i) => (
              <div key={i}>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.experience.fontSize}px` }}>{exp.position || 'Position'}, {exp.company || 'Company'}</h3>
                  </div>
                  <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">{formatDate(exp.startDate)} – {formatDate(exp.endDate) || 'Present'}</span>
                </div>
                {exp.description && <p className="text-gray-600 dark:text-gray-400 mt-1 leading-relaxed" style={{ fontSize: `${fmt.experience.fontSize - 1}px` }}>{exp.description}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
      {education.length > 0 && (
        <div>
          <SectionTitle template="minimal">Education</SectionTitle>
          <div className="space-y-2">
            {education.map((edu, i) => (
              <div key={i} className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.education.fontSize}px` }}>{edu.degree || 'Degree'} {edu.field && `in ${edu.field}`}, {edu.institution || 'Institution'}</h3>
                  {edu.gpa && <p className="text-xs text-gray-400 dark:text-gray-500">GPA: {edu.gpa}</p>}
                </div>
                <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">{formatDate(edu.startDate)} – {formatDate(edu.endDate)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {certifications.length > 0 && (
        <div>
          <SectionTitle template="minimal">Certifications</SectionTitle>
          <p className="text-gray-600 dark:text-gray-300" style={{ fontSize: `${fmt.certifications.fontSize}px` }}>
            {certifications.map((cert, i) => (
              <span key={i}>{cert.name}{cert.issuer ? ` (${cert.issuer})` : ''}{i < certifications.length - 1 ? ' · ' : ''}</span>
            ))}
          </p>
        </div>
      )}
      {projects.length > 0 && (
        <div>
          <SectionTitle template="minimal">Projects</SectionTitle>
          <div className="space-y-2">
            {projects.map((proj, i) => (
              <div key={i}>
                <div className="flex items-start justify-between">
                  <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.projects.fontSize}px` }}>{proj.name || 'Project'}</h3>
                  {proj.technologies && <span className="text-xs text-gray-400 dark:text-gray-500">{proj.technologies}</span>}
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5 min-h-[2em] leading-relaxed">{proj.description || 'Project description'}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function CreativeTemplate({ personal, summary, skills, experience, education, certifications, projects, formatting }) {
  const fmt = { ...defaultFormatting, ...formatting };
  return (
    <div className="flex min-h-full">
      <div className="w-1/3 bg-gradient-to-b from-fuchsia-600 to-purple-700 text-white p-5">
        {personal.name && (
          <div className="mb-6">
            <h1 style={{ fontSize: `${fmt.name.fontSize}px`, fontWeight: 'bold' }} className="text-white leading-tight">{personal.name}</h1>
          </div>
        )}
        <div className="space-y-2 text-sm text-white/80">
          {personal.email && <p className="break-all">{personal.email}</p>}
          {personal.phone && <p>{personal.phone}</p>}
          {personal.location && <p>{personal.location}</p>}
          {personal.website && <p className="break-all text-xs">{personal.website}</p>}
          {personal.linkedin && <p className="break-all text-xs">LinkedIn</p>}
        </div>
        {skills.length > 0 && (
          <div className="mt-6">
            <h2 className="text-xs font-bold uppercase tracking-widest text-white/60 mb-2">Skills</h2>
            <div className="flex flex-wrap gap-1.5">
              {skills.map((skill, i) => (
                <span key={i} className="px-2 py-0.5 bg-white/20 text-white rounded text-xs font-medium">{skill.name}</span>
              ))}
            </div>
          </div>
        )}
        {certifications.length > 0 && (
          <div className="mt-6">
            <h2 className="text-xs font-bold uppercase tracking-widest text-white/60 mb-2">Certifications</h2>
            <div className="space-y-1">
              {certifications.map((cert, i) => (
                <div key={i} className="text-xs text-white/80">
                  <span className="font-medium text-white">{cert.name}</span>
                  {cert.issuer && <span className="block text-white/60">{cert.issuer}</span>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      <div className="flex-1 p-6 space-y-5">
        {summary && (
          <div>
            <SectionTitle template="creative">About Me</SectionTitle>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed" style={{ fontSize: `${fmt.body.fontSize}px` }}>{summary}</p>
          </div>
        )}
        {experience.length > 0 && (
          <div>
            <SectionTitle template="creative">Experience</SectionTitle>
            <div className="space-y-4">
              {experience.map((exp, i) => (
                <div key={i} className="relative pl-4 border-l-2 border-fuchsia-200 dark:border-fuchsia-800">
                  <div className="absolute -left-[5px] top-1 w-2 h-2 bg-fuchsia-500 rounded-full" />
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.experience.fontSize}px` }}>{exp.position || 'Position'}</h3>
                      <p className="text-xs text-fuchsia-600 dark:text-fuchsia-400 font-medium">{exp.company || 'Company'}</p>
                    </div>
                    <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">{formatDate(exp.startDate)} – {formatDate(exp.endDate) || 'Present'}</span>
                  </div>
                  {exp.description && <p className="text-gray-600 dark:text-gray-400 mt-1 text-xs leading-relaxed">{exp.description}</p>}
                </div>
              ))}
            </div>
          </div>
        )}
        {education.length > 0 && (
          <div>
            <SectionTitle template="creative">Education</SectionTitle>
            <div className="space-y-3">
              {education.map((edu, i) => (
                <div key={i} className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.education.fontSize}px` }}>{edu.degree || 'Degree'} {edu.field && `in ${edu.field}`}</h3>
                    <p className="text-xs text-fuchsia-600 dark:text-fuchsia-400">{edu.institution || 'Institution'}</p>
                    {edu.gpa && <p className="text-xs text-gray-400 dark:text-gray-500">GPA: {edu.gpa}</p>}
                  </div>
                  <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">{formatDate(edu.startDate)} – {formatDate(edu.endDate)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        {projects.length > 0 && (
          <div>
            <SectionTitle template="creative">Projects</SectionTitle>
            <div className="space-y-3">
              {projects.map((proj, i) => (
                <div key={i} className="p-3 bg-fuchsia-50 dark:bg-fuchsia-900/10 rounded-lg">
                  <h3 className="font-semibold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.projects.fontSize}px` }}>{proj.name || 'Project'}</h3>
                  {proj.technologies && <p className="text-xs text-fuchsia-600 dark:text-fuchsia-400 mt-0.5">{proj.technologies}</p>}
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 min-h-[2em] leading-relaxed">{proj.description || 'Project description'}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ExecutiveTemplate({ personal, summary, skills, experience, education, certifications, projects, formatting }) {
  const fmt = { ...defaultFormatting, ...formatting };
  return (
    <div className="p-6 space-y-5">
      {personal.name && (
        <div className="bg-slate-800 dark:bg-slate-200 text-white dark:text-slate-800 -mx-6 -mt-6 px-6 py-5">
          <h1 style={{ fontSize: `${fmt.name.fontSize + 2}px`, fontWeight: 'bold' }} className="tracking-wide">{personal.name}</h1>
          <div className="flex items-center gap-3 mt-2 flex-wrap text-sm text-slate-300 dark:text-slate-600">
            {personal.email && <span className="flex items-center gap-1"><Mail className="w-3.5 h-3.5" /> {personal.email}</span>}
            {personal.phone && <span className="flex items-center gap-1"><Phone className="w-3.5 h-3.5" /> {personal.phone}</span>}
            {personal.location && <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {personal.location}</span>}
            {personal.website && <span className="flex items-center gap-1"><Globe className="w-3.5 h-3.5" /> {personal.website}</span>}
            {personal.linkedin && <span className="flex items-center gap-1"><Linkedin className="w-3.5 h-3.5" /> LinkedIn</span>}
          </div>
        </div>
      )}
      {summary && (
        <div>
          <SectionTitle template="executive">Executive Summary</SectionTitle>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed pl-4" style={{ fontSize: `${fmt.body.fontSize}px`, fontWeight: fmt.body.bold ? 'bold' : 'normal' }}>{summary}</p>
        </div>
      )}
      {skills.length > 0 && (
        <div>
          <SectionTitle template="executive">Core Competencies</SectionTitle>
          <div className="grid grid-cols-2 gap-x-6 gap-y-1 pl-4 text-sm text-gray-700 dark:text-gray-300" style={{ fontSize: `${fmt.skills.fontSize}px` }}>
            {skills.map((skill, i) => (
              <span key={i} className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-slate-800 dark:bg-slate-200 rounded-full flex-shrink-0" />
                {skill.name}
              </span>
            ))}
          </div>
        </div>
      )}
      {experience.length > 0 && (
        <div>
          <SectionTitle template="executive">Professional Experience</SectionTitle>
          <div className="space-y-4 pl-4">
            {experience.map((exp, i) => (
              <div key={i}>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-bold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.experience.fontSize}px` }}>{exp.position || 'Position'}</h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400 font-medium">{exp.company || 'Company'}</p>
                  </div>
                  <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded">{formatDate(exp.startDate)} – {formatDate(exp.endDate) || 'Present'}</span>
                </div>
                {exp.description && <p className="text-gray-600 dark:text-gray-400 mt-1.5 leading-relaxed" style={{ fontSize: `${fmt.experience.fontSize - 1}px` }}>{exp.description}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
      {education.length > 0 && (
        <div>
          <SectionTitle template="executive">Education</SectionTitle>
          <div className="space-y-3 pl-4">
            {education.map((edu, i) => (
              <div key={i} className="flex items-start justify-between">
                <div>
                  <h3 className="font-bold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.education.fontSize}px` }}>{edu.degree || 'Degree'} {edu.field && `in ${edu.field}`}</h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400">{edu.institution || 'Institution'}</p>
                  {edu.gpa && <p className="text-xs text-gray-400 dark:text-gray-500">GPA: {edu.gpa}</p>}
                </div>
                <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap">{formatDate(edu.startDate)} – {formatDate(edu.endDate)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {certifications.length > 0 && (
        <div>
          <SectionTitle template="executive">Certifications</SectionTitle>
          <div className="space-y-1 pl-4">
            {certifications.map((cert, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <span className="font-medium text-gray-900 dark:text-white" style={{ fontSize: `${fmt.certifications.fontSize}px` }}>{cert.name}</span>
                <span className="text-xs text-gray-400 dark:text-gray-500">{cert.issuer}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {projects.length > 0 && (
        <div>
          <SectionTitle template="executive">Key Projects</SectionTitle>
          <div className="space-y-3 pl-4">
            {projects.map((proj, i) => (
              <div key={i}>
                <h3 className="font-bold text-gray-900 dark:text-white" style={{ fontSize: `${fmt.projects.fontSize}px` }}>{proj.name || 'Project'}</h3>
                {proj.technologies && <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{proj.technologies}</p>}
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 min-h-[2em] leading-relaxed">{proj.description || 'Project description'}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function TechnicalTemplate({ personal, summary, skills, experience, education, certifications, projects, formatting }) {
  const fmt = { ...defaultFormatting, ...formatting };
  return (
    <div className="p-6 space-y-5 font-sans">
      {personal.name && (
        <div className="border-b-2 border-cyan-600 dark:border-cyan-400 pb-4">
          <h1 style={{ fontSize: `${fmt.name.fontSize}px`, fontWeight: 'bold' }} className="text-gray-900 dark:text-white font-mono">{personal.name}</h1>
          <div className="flex items-center gap-4 mt-2 flex-wrap text-xs text-gray-500 dark:text-gray-400 font-mono">
            {personal.email && <span>{personal.email}</span>}
            {personal.phone && <span>| {personal.phone}</span>}
            {personal.location && <span>| {personal.location}</span>}
            {personal.website && <span>| {personal.website}</span>}
            {personal.linkedin && <span>| LinkedIn</span>}
          </div>
        </div>
      )}
      {summary && (
        <div>
          <SectionTitle template="technical">// About</SectionTitle>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed font-mono text-xs" style={{ fontSize: `${fmt.body.fontSize}px` }}>{summary}</p>
        </div>
      )}
      {skills.length > 0 && (
        <div>
          <SectionTitle template="technical">// Skills</SectionTitle>
          <div className="flex flex-wrap gap-1.5">
            {skills.map((skill, i) => (
              <span key={i} className="px-2 py-0.5 bg-cyan-50 dark:bg-cyan-900/20 text-cyan-700 dark:text-cyan-300 rounded border border-cyan-200 dark:border-cyan-800 font-mono text-xs">{skill.name}</span>
            ))}
          </div>
        </div>
      )}
      {experience.length > 0 && (
        <div>
          <SectionTitle template="technical">// Experience</SectionTitle>
          <div className="space-y-4">
            {experience.map((exp, i) => (
              <div key={i} className="pl-3 border-l border-gray-200 dark:border-gray-700">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white font-mono" style={{ fontSize: `${fmt.experience.fontSize}px` }}>{exp.position || 'Position'}</h3>
                    <p className="text-xs text-cyan-600 dark:text-cyan-400 font-mono">@ {exp.company || 'Company'}</p>
                  </div>
                  <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap font-mono">{formatDate(exp.startDate)} – {formatDate(exp.endDate) || 'Present'}</span>
                </div>
                {exp.description && <p className="text-gray-600 dark:text-gray-400 mt-1 leading-relaxed text-xs font-mono">{exp.description}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
      {education.length > 0 && (
        <div>
          <SectionTitle template="technical">// Education</SectionTitle>
          <div className="space-y-3">
            {education.map((edu, i) => (
              <div key={i} className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white font-mono" style={{ fontSize: `${fmt.education.fontSize}px` }}>{edu.degree || 'Degree'} {edu.field && `in ${edu.field}`}</h3>
                  <p className="text-xs text-cyan-600 dark:text-cyan-400 font-mono">{edu.institution || 'Institution'}</p>
                  {edu.gpa && <p className="text-xs text-gray-400 dark:text-gray-500 font-mono">GPA: {edu.gpa}</p>}
                </div>
                <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap font-mono">{formatDate(edu.startDate)} – {formatDate(edu.endDate)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {certifications.length > 0 && (
        <div>
          <SectionTitle template="technical">// Certifications</SectionTitle>
          <div className="space-y-1 font-mono text-xs">
            {certifications.map((cert, i) => (
              <div key={i} className="flex items-center justify-between">
                <span className="text-gray-900 dark:text-white font-medium">{cert.name}</span>
                <span className="text-gray-400 dark:text-gray-500">{cert.issuer}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {projects.length > 0 && (
        <div>
          <SectionTitle template="technical">// Projects</SectionTitle>
          <div className="space-y-3">
            {projects.map((proj, i) => (
              <div key={i} className="p-3 bg-gray-50 dark:bg-slate-900 rounded-lg border border-gray-100 dark:border-gray-700">
                <h3 className="font-semibold text-gray-900 dark:text-white font-mono" style={{ fontSize: `${fmt.projects.fontSize}px` }}>{proj.name || 'Project'}</h3>
                {proj.technologies && <p className="text-xs text-cyan-600 dark:text-cyan-400 font-mono mt-0.5">[{proj.technologies}]</p>}
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 min-h-[2em] leading-relaxed font-mono">{proj.description || 'Project description'}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

const templates = { modern: ModernTemplate, professional: ProfessionalTemplate, startup: StartupTemplate, minimal: MinimalTemplate, creative: CreativeTemplate, executive: ExecutiveTemplate, technical: TechnicalTemplate };

const bgStyles = {
  modern: 'bg-white dark:bg-slate-800',
  professional: 'bg-white dark:bg-slate-800',
  startup: 'bg-white dark:bg-slate-800',
  minimal: 'bg-white dark:bg-slate-800',
  creative: 'bg-white dark:bg-slate-800',
  executive: 'bg-white dark:bg-slate-800',
  technical: 'bg-white dark:bg-slate-800',
};

function OrderedSections({ data, template, formatting, sectionOrder }) {
  const personal = data.personal || {};
  const fmt = { ...defaultFormatting, ...formatting };
  const order = sectionOrder || DEFAULT_SECTION_ORDER;

  return (
    <div className="p-6 space-y-5">
      {order.map(sectionKey => {
        if (sectionKey === 'personal') {
          if (!personal.name) return null;
          if (template === 'modern') return (
            <div key="personal" className="text-center border-b border-gray-100 dark:border-gray-700 pb-4">
              <h1 style={{ fontSize: `${fmt.name.fontSize}px`, fontWeight: fmt.name.bold ? 'bold' : 'normal' }} className="text-gray-900 dark:text-white">{personal.name}</h1>
              <div className="flex items-center justify-center gap-4 mt-2 flex-wrap">
                {personal.email && <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400"><Mail className="w-3 h-3" /> {personal.email}</span>}
                {personal.phone && <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400"><Phone className="w-3 h-3" /> {personal.phone}</span>}
                {personal.location && <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400"><MapPin className="w-3 h-3" /> {personal.location}</span>}
                {personal.website && <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400"><Globe className="w-3 h-3" /> {personal.website}</span>}
                {personal.linkedin && <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400"><Linkedin className="w-3 h-3" /> LinkedIn</span>}
              </div>
            </div>
          );
          if (template === 'professional') return (
            <div key="personal" className="bg-gray-800 dark:bg-gray-200 text-white dark:text-gray-800 -mx-6 -mt-6 px-6 py-4">
              <h1 style={{ fontSize: `${fmt.name.fontSize}px`, fontWeight: fmt.name.bold ? 'bold' : 'normal' }}>{personal.name}</h1>
              <div className="flex items-center gap-4 mt-2 flex-wrap text-gray-200 dark:text-gray-600">
                {personal.email && <span className="inline-flex items-center gap-1 text-xs"><Mail className="w-3 h-3" /> {personal.email}</span>}
                {personal.phone && <span className="inline-flex items-center gap-1 text-xs"><Phone className="w-3 h-3" /> {personal.phone}</span>}
                {personal.location && <span className="inline-flex items-center gap-1 text-xs"><MapPin className="w-3 h-3" /> {personal.location}</span>}
                {personal.website && <span className="inline-flex items-center gap-1 text-xs"><Globe className="w-3 h-3" /> {personal.website}</span>}
                {personal.linkedin && <span className="inline-flex items-center gap-1 text-xs"><Linkedin className="w-3 h-3" /> LinkedIn</span>}
              </div>
            </div>
          );
          if (template === 'startup') return (
            <div key="personal" className="flex items-center gap-4 pb-4 border-b border-gray-100 dark:border-gray-700">
              <div className="w-14 h-14 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400 text-xl font-bold flex-shrink-0">
                {personal.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <h1 style={{ fontSize: `${fmt.name.fontSize}px`, fontWeight: fmt.name.bold ? 'bold' : 'normal' }} className="text-gray-900 dark:text-white">{personal.name}</h1>
                <div className="flex items-center gap-3 mt-1 flex-wrap text-xs text-gray-500 dark:text-gray-400">
                  {personal.email && <span className="inline-flex items-center gap-1"><Mail className="w-3 h-3" /> {personal.email}</span>}
                  {personal.phone && <span className="inline-flex items-center gap-1"><Phone className="w-3 h-3" /> {personal.phone}</span>}
                  {personal.location && <span className="inline-flex items-center gap-1"><MapPin className="w-3 h-3" /> {personal.location}</span>}
                </div>
              </div>
            </div>
          );
          if (template === 'minimal') return (
            <div key="personal" className="text-center pb-4">
              <h1 style={{ fontSize: `${fmt.name.fontSize}px`, fontWeight: fmt.name.bold ? 'bold' : 'normal' }} className="text-gray-900 dark:text-white">{personal.name}</h1>
              <div className="flex items-center justify-center gap-3 mt-2 flex-wrap text-xs text-gray-400 dark:text-gray-500">
                {personal.email && <span>{personal.email}</span>}
                {personal.phone && <span>· {personal.phone}</span>}
                {personal.location && <span>· {personal.location}</span>}
                {personal.website && <span>· {personal.website}</span>}
              </div>
            </div>
          );
          if (template === 'creative') return (
            <div key="personal" className="flex">
              <div className="w-1/3 bg-gradient-to-b from-fuchsia-600 to-purple-700 text-white p-5 -m-6 mb-0 rounded-r-none">
                <h1 style={{ fontSize: `${fmt.name.fontSize}px`, fontWeight: 'bold' }} className="text-white leading-tight">{personal.name}</h1>
                <div className="space-y-1 mt-2 text-xs text-white/80">
                  {personal.email && <p className="break-all">{personal.email}</p>}
                  {personal.phone && <p>{personal.phone}</p>}
                  {personal.location && <p>{personal.location}</p>}
                </div>
              </div>
              <div className="flex-1" />
            </div>
          );
          if (template === 'executive') return (
            <div key="personal" className="bg-slate-800 dark:bg-slate-200 text-white dark:text-slate-800 -mx-6 -mt-6 px-6 py-5">
              <h1 style={{ fontSize: `${fmt.name.fontSize + 2}px`, fontWeight: 'bold' }} className="tracking-wide">{personal.name}</h1>
              <div className="flex items-center gap-3 mt-2 flex-wrap text-sm text-slate-300 dark:text-slate-600">
                {personal.email && <span className="flex items-center gap-1"><Mail className="w-3.5 h-3.5" /> {personal.email}</span>}
                {personal.phone && <span className="flex items-center gap-1"><Phone className="w-3.5 h-3.5" /> {personal.phone}</span>}
                {personal.location && <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {personal.location}</span>}
                {personal.website && <span className="flex items-center gap-1"><Globe className="w-3.5 h-3.5" /> {personal.website}</span>}
              </div>
            </div>
          );
          if (template === 'technical') return (
            <div key="personal" className="border-b-2 border-cyan-600 dark:border-cyan-400 pb-4">
              <h1 style={{ fontSize: `${fmt.name.fontSize}px`, fontWeight: 'bold' }} className="text-gray-900 dark:text-white font-mono">{personal.name}</h1>
              <div className="flex items-center gap-4 mt-2 flex-wrap text-xs text-gray-500 dark:text-gray-400 font-mono">
                {personal.email && <span>{personal.email}</span>}
                {personal.phone && <span>| {personal.phone}</span>}
                {personal.location && <span>| {personal.location}</span>}
                {personal.website && <span>| {personal.website}</span>}
              </div>
            </div>
          );
          return null;
        }

        const renderer = SECTION_RENDERERS[sectionKey];
        if (!renderer) return null;
        const result = renderer(data, fmt, template);
        if (!result) return null;
        return <div key={result.key}>{result.content}</div>;
      })}
    </div>
  );
}

export default function ResumePreview({ data = {}, template = 'modern', formatting, sectionOrder, className = '' }) {
  const personal = data.personal || {};
  const summary = data.summary || '';
  const skills = data.skills || [];
  const experience = data.experience || [];
  const education = data.education || [];
  const certifications = data.certifications || [];
  const projects = data.projects || [];

  const hasData = personal.name || summary || skills.length || experience.length || education.length;

  if (!hasData) {
    return (
      <div className={`flex items-center justify-center h-full min-h-[400px] bg-gray-50 dark:bg-slate-900 rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-700 ${className}`}>
        <div className="text-center">
          <p className="text-sm text-gray-400 dark:text-gray-500">Start filling in the form to see a live preview</p>
        </div>
      </div>
    );
  }

  const TemplateComponent = templates[template] || templates.modern;
  const sharedProps = { personal, summary, skills, experience, education, certifications, projects, formatting };

  return (
    <div className={`${bgStyles[template] || bgStyles.modern} rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden ${className}`}>
      <TemplateComponent {...sharedProps} />
    </div>
  );
}
