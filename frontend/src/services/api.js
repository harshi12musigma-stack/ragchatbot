import axios from 'axios';

const API_BASE = '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadDocument = async (file, sessionId) => {
  const formData = new FormData();
  formData.append('file', file);
  if (sessionId) {
    formData.append('session_id', sessionId);
  }

  const response = await axios.post(`${API_BASE}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const sendMessage = async (question, sessionId, conversationHistory = []) => {
  const response = await api.post('/chat', {
    question,
    session_id: sessionId,
    conversation_history: conversationHistory,
  });

  return response.data;
};

export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
