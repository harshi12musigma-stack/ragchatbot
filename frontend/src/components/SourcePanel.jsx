function SourcePanel({ sources }) {
  if (!sources || sources.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center">
          <p>No sources yet</p>
          <p className="text-sm mt-1">Sources will appear here after asking questions</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-4">
      <h3 className="font-semibold text-lg mb-4">Source Documents</h3>
      <div className="space-y-4">
        {sources.map((source, idx) => (
          <div
            key={idx}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">
                  Source {source.index}
                </span>
                <span className="text-sm text-gray-600">{source.filename}</span>
              </div>
              <span className="text-xs text-gray-500">
                Relevance: {(source.relevance * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
              {source.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SourcePanel;
