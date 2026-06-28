import api from './axiosConfig';

export const analyzeGithub = async (url = null) => {
  const response = await api.post('/analyze', { url });
  return response.data;
};

export const fetchUserRepos = async () => {
  const response = await api.get('/repos');
  return response.data;
};

export const getAnalysisStatus = async (jobId) => {
  const response = await api.get(`/analysis-status/${jobId}`);
  return response.data;
};

export const chatQuery = async (message) => {
  const response = await api.post('/ask', { query: message });
  return response.data;
};

export const rebuildKnowledgeGraph = async () => {
  const response = await api.post('/rebuild-knowledge-graph');
  return response.data;
};

export const exportResumePDF = async (resumeData) => {
  const token = localStorage.getItem('token');
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
  const response = await fetch(`${baseUrl}/export-resume`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ resume_data: resumeData, format: 'pdf' })
  });
  if (!response.ok) throw new Error('PDF export failed');
  return response.blob();
};

export const chatStream = async (message, onToken, onDone, onError) => {
  const controller = new AbortController();

  try {
    const token = localStorage.getItem('token');
    if (!token) {
      if (onError) onError(new Error('Not authenticated. Please log in.'));
      return () => controller.abort();
    }
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
    const response = await fetch(`${baseUrl}/ask/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ query: message }),
      signal: controller.signal
    });

    if (response.status === 401) {
      localStorage.removeItem('token');
      if (onError) onError(new Error('Session expired. Please log in again.'));
      window.location.href = '/';
      return () => controller.abort();
    }

    if (!response.ok) {
      throw new Error('Stream request failed');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.token) {
              onToken(data.token);
            }
          } catch {
            // Skip invalid JSON
          }
        }
      }
    }

    if (onDone) onDone();
  } catch (error) {
    if (error.name === 'AbortError') {
      return;
    }
    if (onError) onError(error);
  }

  return () => controller.abort();
};
