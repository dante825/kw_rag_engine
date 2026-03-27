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

export interface ConversationTurn {
  question: string;
  answer: string;
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

  queryStream: async (
    question: string,
    topK: number | undefined,
    history: ConversationTurn[],
    docIdFilter: string | null,
    onToken: (token: string) => void,
    onSources: (sources: Source[]) => void,
  ): Promise<void> => {
    const response = await fetch(`${API_BASE}/query/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, top_k: topK, history, doc_id_filter: docIdFilter }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Query failed' }));
      throw new Error(err.detail || 'Query failed');
    }

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const data = line.slice(6).trim();
        if (!data) continue;

        const parsed = JSON.parse(data);
        if (parsed.type === 'token') {
          onToken(parsed.content);
        } else if (parsed.type === 'sources') {
          onSources(parsed.sources);
        }
      }
    }
  },

  healthCheck: async (): Promise<{ status: string }> => {
    const response = await axios.get(`${API_BASE}/health`);
    return response.data;
  },
};
