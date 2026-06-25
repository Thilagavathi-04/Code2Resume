import api from './axiosConfig';

export const generateResume = async (query) => {
  const response = await api.post('/generate-resume', { query });
  return response.data;
};

export const listResumes = async () => {
  const response = await api.get('/resumes');
  return response.data;
};

export const downloadResume = async (filename) => {
  const response = await api.get(`/download-resume/${filename}`, {
    responseType: 'blob'
  });
  return response.data;
};

export const deleteResume = async (filename) => {
  const response = await api.delete(`/delete-resume/${filename}`);
  return response.data;
};
