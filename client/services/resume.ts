import type { Resume, JobMatch } from "@/types/resume";

const API_URL = import.meta.env.VITE_API_URL || '';

// Helper function to get auth token from localStorage
const getAuthToken = (): string | null => {
  return localStorage.getItem('authToken');
};

// Helper function for API requests with auth
const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const token = getAuthToken();
  
  const headers: Record<string, string> = {};
  
  // Only set Content-Type for non-FormData bodies
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  // Only add auth header when token exists (avoid sending "Bearer null")
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const config: RequestInit = {
    ...options,
    headers: {
      ...headers,
      ...(options.headers as Record<string, string> | undefined),
    },
  };
  
  const response = await fetch(`${API_URL}${endpoint}`, config);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }
  
  return response.json();
};


// Upload a resume file
export const uploadResume = async (file: File): Promise<Resume> => {
  const formData = new FormData();
  formData.append('file', file);
  const token = getAuthToken();
  
  const response = await fetch(`${API_URL}/resume/upload`, {
    method: 'POST',
    body: formData,
    headers: token ? {
      'Authorization': `Bearer ${token}`,
    } : {},
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }
  
  return response.json();
};

// Get all resumes for current user
export const getMyResumes = async (): Promise<Resume[]> => {
  return apiRequest('/resume/my-resumes');
};

// Match a resume with jobs
export const matchResume = async (resumeId: number, topK: number = 3): Promise<JobMatch[]> => {
  return apiRequest(`/resume/${resumeId}/match?top_k=${topK}`);
};

// Delete a resume
export const deleteResume = async (resumeId: number): Promise<{ message: string }> => {
  return apiRequest(`/resume/${resumeId}`, {
    method: 'DELETE',
  });
};

// Analyze resume (file or raw text) + optional job description
export const analyzeResume = async (file: File | null, resumeText?: string, jobDescription?: string): Promise<any> => {
  const formData = new FormData();
  if (file) {
    formData.append('file', file);
  } else if (resumeText) {
    formData.append('resume_text', resumeText);
  }
  if (jobDescription) {
    formData.append('job_description', jobDescription);
  }

  const token = getAuthToken();
  const response = await fetch(`${API_URL}/resume/analyze`, {
    method: 'POST',
    body: formData,
    headers: token ? {
      'Authorization': `Bearer ${token}`,
    } : {},
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
};

export const uploadVoice = async (file: File, language?: string): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);
  if (language) formData.append('language', language);

  const token = getAuthToken();
  const response = await fetch(`${API_URL}/resume/upload-voice`, {
    method: 'POST',
    body: formData,
    headers: token ? {
      'Authorization': `Bearer ${token}`,
    } : {},
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
};

export const chatWithResume = async (resumeId: number, message: string): Promise<any> => {
  const formData = new FormData();
  formData.append('resume_id', String(resumeId));
  formData.append('message', message);

  const token = getAuthToken();
  const response = await fetch(`${API_URL}/resume/chat`, {
    method: 'POST',
    body: formData,
    headers: token ? {
      'Authorization': `Bearer ${token}`,
    } : {},
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
};

export const rankResumes = async (jobDescription: string, topK: number = 10): Promise<any> => {
  const formData = new FormData();
  formData.append('job_description', jobDescription);
  formData.append('top_k', String(topK));

  const token = getAuthToken();
  const response = await fetch(`${API_URL}/resume/rank`, {
    method: 'POST',
    body: formData,
    headers: token ? {
      'Authorization': `Bearer ${token}`,
    } : {},
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
};

export const suggestImprovements = async (resumeId?: number, resumeText?: string, jobDescription?: string) => {
  const formData = new FormData();
  if (resumeId) formData.append('resume_id', String(resumeId));
  if (resumeText) formData.append('resume_text', resumeText);
  if (jobDescription) formData.append('job_description', jobDescription);

  const token = getAuthToken();
  const response = await fetch(`${API_URL}/resume/suggest`, {
    method: 'POST',
    body: formData,
    headers: token ? {
      'Authorization': `Bearer ${token}`,
    } : {},
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
};