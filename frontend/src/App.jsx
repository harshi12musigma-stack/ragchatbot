import { useState, useEffect } from 'react';
import { checkHealth } from './services/api';
import DocumentUploader from './components/DocumentUploader';
import ChatInterface from './components/ChatInterface';
import SourcePanel from './components/SourcePanel';

function App() {
  const [connected, setConnected] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [sources, setSources] = useState([]);

  // Check backend connection
  useEffect(() => {
    checkHealth()
      .then((data) => {
        setConnected(data.status === 'healthy');
      })
      .catch((err) => console.error('Backend connection failed:', err));
  }, []);

  // Generate session ID on mount
  useEffect(() => {
    setSessionId(crypto.randomUUID());
  }, []);

  const handleUploadSuccess = (result) => {
    setUploadedDoc(result);
    setSessionId(result.session_id);
  };

  const handleSourcesUpdate = (newSources) => {
    setSources(newSources);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">RAG Chatbot</h1>
              <p className="text-gray-600 mt-1">Upload documents and ask questions</p>
            </div>
            <div className="flex items-center space-x-4">
              {uploadedDoc && (
                <div className="bg-green-50 border border-green-200 rounded px-3 py-2">
                  <p className="text-sm text-green-800">
                    📄 {uploadedDoc.filename} ({uploadedDoc.chunks} chunks)
                  </p>
                </div>
              )}
              <span
                className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  connected
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}
              >
                {connected ? '● Connected' : '● Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {!uploadedDoc ? (
          /* Upload View */
          <div className="max-w-2xl mx-auto">
            <div className="bg-white shadow rounded-lg p-8">
              <h2 className="text-2xl font-semibold mb-6">Get Started</h2>
              <p className="text-gray-700 mb-6">
                Upload a document (PDF, DOCX, TXT, or MD) to start asking questions.
              </p>
              <DocumentUploader
                sessionId={sessionId}
                onUploadSuccess={handleUploadSuccess}
              />
            </div>

            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="font-semibold text-blue-900 mb-3">How it works:</h3>
              <ol className="list-decimal list-inside text-blue-800 space-y-2">
                <li>Upload a document (it will be chunked and vectorized)</li>
                <li>Ask questions in natural language</li>
                <li>Get answers with source citations from your document</li>
                <li>Continue the conversation with context retention</li>
              </ol>
            </div>
          </div>
        ) : (
          /* Chat View */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
            {/* Chat Area */}
            <div className="lg:col-span-2 bg-white shadow rounded-lg overflow-hidden flex flex-col">
              <div className="bg-gray-50 border-b border-gray-200 px-4 py-3">
                <h2 className="font-semibold text-lg">Chat</h2>
              </div>
              <ChatInterface
                sessionId={sessionId}
                onSourcesUpdate={handleSourcesUpdate}
              />
            </div>

            {/* Sources Panel */}
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="bg-gray-50 border-b border-gray-200 px-4 py-3">
                <h2 className="font-semibold text-lg">Sources</h2>
              </div>
              <SourcePanel sources={sources} />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-8 text-center text-sm text-gray-500 pb-4">
        <p>RAG Chatbot v1.0 • Powered by OpenAI GPT-4o-mini & ChromaDB</p>
      </footer>
    </div>
  );
}

export default App;
