import api from './axiosConfig';

const v2 = {
  auth: {
    register: (data) => api.post('/api/v2/auth/register', data),
    login: (data) => api.post('/api/v2/auth/login', data, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
    me: () => api.get('/api/v2/auth/me'),
    updateMe: (data) => api.put('/api/v2/auth/me', data),
  },

  resumes: {
    list: () => api.get('/api/v2/resumes/'),
    get: (id) => api.get(`/api/v2/resumes/${id}`),
    create: (data) => api.post('/api/v2/resumes/', data),
    update: (id, data) => api.put(`/api/v2/resumes/${id}`, data),
    delete: (id) => api.delete(`/api/v2/resumes/${id}`),
    export: (id) => api.get(`/api/v2/resumes/${id}/export`, { responseType: 'blob' }),
    import: (formData) => api.post('/api/v2/resumes/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
    addExperience: (resumeId, data) => api.post(`/api/v2/resumes/${resumeId}/experiences`, data),
    addEducation: (resumeId, data) => api.post(`/api/v2/resumes/${resumeId}/educations`, data),
    addSkill: (resumeId, data) => api.post(`/api/v2/resumes/${resumeId}/skills`, data),
    addCertification: (resumeId, data) => api.post(`/api/v2/resumes/${resumeId}/certifications`, data),
    addProject: (resumeId, data) => api.post(`/api/v2/resumes/${resumeId}/projects`, data),
    aiEnhance: (data) => api.post('/api/v2/resumes/ai-enhance', data),
  },

  jobs: {
    list: () => api.get('/api/v2/jobs/'),
    get: (id) => api.get(`/api/v2/jobs/${id}`),
    create: (data) => api.post('/api/v2/jobs/', data),
    delete: (id) => api.delete(`/api/v2/jobs/${id}`),
    analyze: (data) => api.post('/api/v2/jobs/analyze', data),
    createATS: (data) => api.post('/api/v2/jobs/ats', data),
    getATSReports: () => api.get('/api/v2/jobs/ats/reports'),
  },

  interviews: {
    list: () => api.get('/api/v2/interviews/'),
    get: (id) => api.get(`/api/v2/interviews/${id}`),
    create: (data) => api.post('/api/v2/interviews/', data),
    update: (id, data) => api.put(`/api/v2/interviews/${id}`, data),
  },

  skillGap: {
    list: () => api.get('/api/v2/skill-gap/'),
    create: (data) => api.post('/api/v2/skill-gap/', data),
  },
};

export default v2;
