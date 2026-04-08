import { useState } from 'react'

function App() {
  const [connected, setConnected] = useState(false)

  // Check backend connection on mount
  useState(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'healthy') {
          setConnected(true)
        }
      })
      .catch(err => console.error('Backend connection failed:', err))
  }, [])

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">RAG Chatbot</h1>
          <p className="text-gray-600 mt-2">Upload documents and ask questions</p>
          <div className="mt-4">
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {connected ? '● Backend Connected' : '● Backend Disconnected'}
            </span>
          </div>
        </header>

        <main>
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Welcome! 🚀</h2>
            <p className="text-gray-700 mb-4">
              This is your RAG Chatbot application. The backend API is {connected ? 'running' : 'not running'}.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded p-4">
              <h3 className="font-semibold text-blue-900 mb-2">Next Steps:</h3>
              <ul className="list-disc list-inside text-blue-800 space-y-1">
                <li>Document upload component (coming soon)</li>
                <li>Chat interface (coming soon)</li>
                <li>Source panel for citations (coming soon)</li>
                <li>Session management (coming soon)</li>
              </ul>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
