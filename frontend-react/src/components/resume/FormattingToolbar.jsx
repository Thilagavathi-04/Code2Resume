import { Type, Bold, ChevronDown } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

const FONT_SIZES = [
  { label: 'XS', value: 10 },
  { label: 'SM', value: 12 },
  { label: 'Base', value: 14 },
  { label: 'LG', value: 16 },
  { label: 'XL', value: 18 },
  { label: '2XL', value: 20 },
];

const SECTION_KEYS = [
  { key: 'name', label: 'Name' },
  { key: 'sectionHeadings', label: 'Section Headings' },
  { key: 'body', label: 'Body Text' },
  { key: 'experience', label: 'Experience' },
  { key: 'education', label: 'Education' },
  { key: 'skills', label: 'Skills' },
  { key: 'projects', label: 'Projects' },
  { key: 'certifications', label: 'Certifications' },
];

export default function FormattingToolbar({ formatting, onChange }) {
  const [openDropdown, setOpenDropdown] = useState(null);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpenDropdown(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const defaults = {
    name: { fontSize: 20, bold: true },
    sectionHeadings: { fontSize: 14, bold: true },
    body: { fontSize: 12, bold: false },
    experience: { fontSize: 12, bold: false },
    education: { fontSize: 12, bold: false },
    skills: { fontSize: 12, bold: false },
    projects: { fontSize: 12, bold: false },
    certifications: { fontSize: 12, bold: false },
  };

  const fmt = { ...defaults, ...formatting };

  const updateFormat = (section, key, value) => {
    onChange({
      ...fmt,
      [section]: { ...(fmt[section] || defaults[section]), [key]: value },
    });
  };

  return (
    <div className="p-3 rounded-xl border border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-slate-900 space-y-2">
      <div className="flex items-center gap-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
        <Type className="w-3.5 h-3.5" />
        Formatting
      </div>
      <div className="grid grid-cols-1 gap-2" ref={dropdownRef}>
        {SECTION_KEYS.map(({ key, label }) => {
          const sectionFmt = fmt[key] || defaults[key];
          return (
            <div key={key} className="flex items-center justify-between gap-2">
              <span className="text-xs text-gray-600 dark:text-gray-400 min-w-[90px]">{label}</span>
              <div className="flex items-center gap-1.5">
                <div className="relative">
                  <button
                    onClick={() => setOpenDropdown(openDropdown === key ? null : key)}
                    className="flex items-center gap-1 px-2 py-1 text-xs rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
                  >
                    {sectionFmt.fontSize}px
                    <ChevronDown className="w-3 h-3" />
                  </button>
                  {openDropdown === key && (
                    <div className="absolute z-50 mt-1 right-0 w-20 py-1 bg-white dark:bg-slate-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg">
                      {FONT_SIZES.map(({ label: szLabel, value }) => (
                        <button
                          key={value}
                          onClick={() => { updateFormat(key, 'fontSize', value); setOpenDropdown(null); }}
                          className={`w-full text-left px-3 py-1 text-xs hover:bg-indigo-50 dark:hover:bg-indigo-900/20 ${
                            sectionFmt.fontSize === value ? 'text-indigo-600 dark:text-indigo-400 font-semibold' : 'text-gray-700 dark:text-gray-300'
                          }`}
                        >
                          {szLabel} ({value}px)
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <button
                  onClick={() => updateFormat(key, 'bold', !sectionFmt.bold)}
                  className={`p-1 rounded-lg border transition-colors ${
                    sectionFmt.bold
                      ? 'bg-indigo-600 border-indigo-600 text-white'
                      : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-slate-700'
                  }`}
                  title={sectionFmt.bold ? 'Normal' : 'Bold'}
                >
                  <Bold className="w-3 h-3" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
