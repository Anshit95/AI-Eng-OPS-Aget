import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { BookOpen, Search, FileText, CheckCircle2 } from 'lucide-react';

export const KnowledgeBase: React.FC = () => {
  const [documents, setDocuments] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('payments rollback procedure');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDocuments()
      .then(setDocuments)
      .catch(console.error)
      .finally(() => setLoading(false));
    handleSearch();
  }, []);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await api.searchKnowledge(searchQuery, 4);
      setSearchResults(res.chunks || []);
    } catch (err) {
      console.error(err);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-indigo-400" />
          RAG Knowledge Base & Operational Runbooks
        </h1>
        <p className="text-xs text-slate-400 mt-1 font-mono">
          Embeddings-powered vector retrieval over runbooks, historical postmortems, and security policies
        </p>
      </div>

      {/* Interactive Semantic Search Console */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
        <h2 className="text-sm font-bold text-white font-mono flex items-center gap-2">
          <Search className="w-4 h-4 text-indigo-400" />
          Semantic Vector Retrieval Console
        </h2>

        <form onSubmit={handleSearch} className="flex gap-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search operational documentation, rollback steps, or CVE guidance..."
            className="flex-1 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 font-mono focus:outline-none focus:border-indigo-500 transition"
          />
          <button
            type="submit"
            disabled={searching}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
          >
            {searching ? 'Querying...' : 'Vector Search'}
          </button>
        </form>

        {/* Results */}
        {searchResults.length > 0 && (
          <div className="pt-2 space-y-3">
            <div className="text-[11px] font-mono text-slate-400">
              Retrieved Top-{searchResults.length} Chunks (Cosine Similarity Ranked):
            </div>
            {searchResults.map((r, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5 text-xs font-mono">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300">
                      {r.category}
                    </span>
                    <span className="font-bold text-white">{r.document_title}</span>
                  </div>
                  <span className="text-emerald-400 font-bold text-[11px]">
                    Cosine Similarity: {r.similarity_score}
                  </span>
                </div>
                <div className="text-slate-300 font-sans text-xs pt-1 line-clamp-3">
                  {r.content}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Document Library Catalog */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
            Indexed Engineering Runbooks & Policies ({documents.length})
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {documents.map((d) => (
            <div key={d.id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-slate-300">
                  {d.category}
                </span>
                <span className="text-[10px] font-mono text-slate-500">
                  {new Date(d.created_at).toLocaleDateString()}
                </span>
              </div>
              <h3 className="text-xs font-bold text-white">{d.title}</h3>
              <p className="text-xs text-slate-400 font-sans line-clamp-3">{d.content}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
