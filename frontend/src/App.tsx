import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { api, Document, QueryResponse, Source, ConversationTurn } from './services/api';

interface ConversationMessage {
  question: string;
  answer: string;
  sources: Source[];
}

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState<ConversationMessage[]>([]);
  const [streamingAnswer, setStreamingAnswer] = useState<QueryResponse | null>(null);
  const [streamingQuestion, setStreamingQuestion] = useState('');
  const [docIdFilter, setDocIdFilter] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history, streamingAnswer]);

  const loadDocuments = async () => {
    try {
      const docs = await api.listDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError('');
    try {
      await api.uploadDocument(file);
      await loadDocuments();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    try {
      await api.deleteDocument(docId);
      await loadDocuments();
    } catch (err) {
      setError('Delete failed');
    }
  };

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    const submittedQuestion = question;
    setQuestion('');
    setStreamingQuestion(submittedQuestion);
    setLoading(true);
    setError('');
    setStreamingAnswer({ answer: '', sources: [] });

    const historyPayload: ConversationTurn[] = history.slice(-10).map(({ question, answer }) => ({ question, answer }));

    let finalAnswer = '';
    let finalSources: Source[] = [];

    try {
      await api.queryStream(
        submittedQuestion,
        undefined,
        historyPayload,
        docIdFilter,
        (token) => {
          finalAnswer += token;
          setStreamingAnswer((prev) => ({
            answer: (prev?.answer ?? '') + token,
            sources: prev?.sources ?? [],
          }));
        },
        (sources: Source[]) => {
          finalSources = sources;
          setStreamingAnswer((prev) => ({ answer: prev?.answer ?? '', sources }));
        },
      );

      setHistory((prev) => [
        ...prev,
        { question: submittedQuestion, answer: finalAnswer, sources: finalSources },
      ]);
    } catch (err: any) {
      setError(err.message || 'Query failed');
    } finally {
      setStreamingAnswer(null);
      setStreamingQuestion('');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-sepia-50">
      <header className="bg-sepia-100 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-sepia-800">RAG Engine</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {error && (
          <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-sepia-100 rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4 text-sepia-800">Upload Documents</h2>
              <input
                type="file"
                accept=".pdf,.txt,.doc,.docx"
                onChange={handleUpload}
                disabled={uploading}
                className="block w-full text-sm text-sepia-600 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sepia-200 file:text-sepia-700 hover:file:bg-sepia-300 disabled:opacity-50"
              />
              {uploading && <p className="mt-2 text-sm text-sepia-500">Uploading...</p>}
            </div>

            <div className="bg-sepia-100 rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4 text-sepia-800">Documents</h2>
              {documents.length === 0 ? (
                <p className="text-sm text-sepia-500">No documents uploaded</p>
              ) : (
                <ul className="space-y-2">
                  {documents.map((doc) => (
                    <li key={doc.id} className="flex items-center justify-between text-sm text-sepia-700">
                      <span className="truncate flex-1">{doc.filename}</span>
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="ml-2 text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="bg-sepia-100 rounded-lg shadow p-6 flex flex-col" style={{ minHeight: '70vh' }}>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-sepia-800">Ask Questions</h2>
                <div className="flex items-center gap-2 text-sm text-sepia-600">
                  <label htmlFor="doc-filter">Filter:</label>
                  <select
                    id="doc-filter"
                    value={docIdFilter ?? ''}
                    onChange={(e) => setDocIdFilter(e.target.value || null)}
                    className="px-2 py-1 border border-sepia-300 rounded bg-sepia-50 text-sepia-700 focus:outline-none focus:ring-1 focus:ring-sepia-500"
                  >
                    <option value="">All documents</option>
                    {documents.map((doc) => (
                      <option key={doc.id} value={doc.id}>{doc.filename}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Chat history */}
              <div className="flex-1 overflow-y-auto mb-4 space-y-4 max-h-[60vh]">
                {history.length === 0 && !streamingAnswer && (
                  <div className="flex flex-col items-center justify-center h-full py-12 space-y-6">
                    <p className="text-sm text-sepia-400">Try asking one of these:</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
                      {[
                        'Summarize the main topics in the documents',
                        'What are the key points covered?',
                        'What conclusions does the document reach?',
                        'Explain the most important concepts',
                      ].map((suggestion) => (
                        <button
                          key={suggestion}
                          onClick={() => setQuestion(suggestion)}
                          className="text-left px-4 py-3 rounded-lg border border-sepia-300 bg-sepia-50 text-sm text-sepia-700 hover:bg-sepia-200 hover:border-sepia-400 transition-colors"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {history.map((turn, idx) => (
                  <div key={idx} className="space-y-2">
                    {/* User bubble */}
                    <div className="flex justify-end">
                      <div className="bg-sepia-200 text-sepia-800 rounded-lg px-4 py-2 max-w-[80%] text-sm">
                        {turn.question}
                      </div>
                    </div>
                    {/* Assistant bubble */}
                    <div className="flex justify-start">
                      <div className="bg-sepia-50 border border-sepia-200 rounded-lg px-4 py-3 max-w-[80%]">
                        <div className="text-sepia-800 prose prose-sm max-w-none">
                          <ReactMarkdown>{turn.answer}</ReactMarkdown>
                        </div>
                        {turn.sources.length > 0 && (
                          <details className="mt-2">
                            <summary className="text-xs text-sepia-500 cursor-pointer select-none">
                              Sources ({turn.sources.length})
                            </summary>
                            <div className="mt-2 space-y-1 max-h-40 overflow-y-auto">
                              {turn.sources.map((source, sIdx) => (
                                <div key={sIdx} className="p-2 bg-sepia-100 border border-sepia-200 rounded text-xs">
                                  <div className="flex justify-between text-sepia-400 mb-1">
                                    <span>Source {sIdx + 1}</span>
                                    <span>{(source.score * 100).toFixed(1)}%</span>
                                  </div>
                                  <p className="text-sepia-600">{source.content}</p>
                                </div>
                              ))}
                            </div>
                          </details>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {/* In-progress streaming bubble */}
                {streamingAnswer && (
                  <div className="space-y-2">
                    <div className="flex justify-end">
                      <div className="bg-sepia-200 text-sepia-800 rounded-lg px-4 py-2 max-w-[80%] text-sm opacity-60">
                        {streamingQuestion}
                      </div>
                    </div>
                    <div className="flex justify-start">
                      <div className="bg-sepia-50 border border-sepia-200 rounded-lg px-4 py-3 max-w-[80%]">
                        <div className="text-sepia-800 prose prose-sm max-w-none">
                          <ReactMarkdown>{streamingAnswer.answer || '...'}</ReactMarkdown>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={chatEndRef} />
              </div>

              {/* Input form */}
              <form onSubmit={handleQuery}>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Enter your question..."
                    disabled={loading}
                    className="flex-1 px-4 py-2 border border-sepia-300 rounded-lg bg-sepia-50 text-sepia-800 placeholder-sepia-400 focus:outline-none focus:ring-2 focus:ring-sepia-500"
                  />
                  <button
                    type="submit"
                    disabled={loading || !question.trim()}
                    className="px-6 py-2 bg-sepia-500 text-white rounded-lg hover:bg-sepia-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Thinking...' : 'Ask'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
