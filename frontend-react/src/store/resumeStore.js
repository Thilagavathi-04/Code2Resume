import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useResumeStore = create(
  persist(
    (set) => ({
      selectedJobDescription: null,
      selectedResume: null,
      selectedTemplate: 'modern',

      setSelectedJobDescription: (jd) => set({ selectedJobDescription: jd }),
      setSelectedResume: (resume) => set({ selectedResume: resume }),
      setSelectedTemplate: (template) => set({ selectedTemplate: template }),
      clearSelection: () => set({ selectedJobDescription: null, selectedResume: null }),
    }),
    { name: 'resume-workflow-store' }
  )
);
