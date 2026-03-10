import axios from 'axios';

const API_BASE = '/api';

export interface Document {
  id: string;
  filename: string;
  upload_date: string;
  chunk_count: number;
}

export interface Source {
  chunk_id: string;
  content: string;
  score: number;
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
}

export const api = {
  uploadDocument: async (file: File): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post<Document>(`${API_BASE}/documents/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  listDocuments: async (): Promise<Document[]> => {
    const response = await axios.get<Document[]>(`${API_BASE}/documents`);
    return response.data;
  },

  deleteDocument: async (docId: string): Promise<void> => {
    await axios.delete(`${API_BASE}/documents/${docId}`);
  },

  query: async (question: string, topK?: number): Promise<QueryResponse> => {
    const response = await axios.post<QueryResponse>(`${API_BASE}/query`, {
      question,
      top_k: topK,
    });
    return response.data;
  },

  healthCheck: async (): Promise<{ status: string }> => {
    const response = await axios.get(`${API_BASE}/health`);
    return response.data;
  },
};
