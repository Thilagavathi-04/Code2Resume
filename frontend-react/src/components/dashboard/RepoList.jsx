import { useState } from 'react';
import { FolderGit2, Search, Filter, Star, ExternalLink } from 'lucide-react';

export default function RepoList({ repos }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('all');

  const domains = ['all', ...new Set(repos.map(r => r.domain).filter(Boolean))];

  const filteredRepos = repos.filter(repo => {
    const matchesSearch =
      repo.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      repo.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDomain = selectedDomain === 'all' || repo.domain === selectedDomain;
    return matchesSearch && matchesDomain;
  });

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col" style={{ minHeight: '500px', maxHeight: 'calc(100vh - 280px)' }}>
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Your Repositories</h2>
            <p className="text-sm text-gray-500">{repos.length} repositories analyzed</p>
          </div>
          <div className="w-10 h-10 bg-teal-50 rounded-xl flex items-center justify-center">
            <FolderGit2 size={20} className="text-teal-600" />
          </div>
        </div>

        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search repositories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-teal-500 focus:border-transparent outline-none transition-all"
          />
        </div>

        {domains.length > 1 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {domains.map(domain => (
              <button
                key={domain}
                onClick={() => setSelectedDomain(domain)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all duration-200 ${
                  selectedDomain === domain
                    ? 'bg-teal-100 text-teal-700 shadow-sm'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {domain === 'all' ? 'All' : domain}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {filteredRepos.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mb-4">
              <FolderGit2 size={32} className="text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-700 mb-2">No Repositories</h3>
            <p className="text-gray-500 text-sm max-w-xs">
              {repos.length === 0
                ? 'Click "Update from GitHub" to analyze your repositories'
                : 'No repositories match your search'}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredRepos.map((repo, index) => (
              <div
                key={index}
                className="group border border-gray-100 rounded-xl p-4 hover:border-teal-200 hover:shadow-sm transition-all duration-300 animate-fade-in-up"
                style={{ animationDelay: `${index * 0.03}s` }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-900 truncate group-hover:text-teal-600 transition-colors">
                        {repo.name}
                      </h3>
                      {repo.stars > 0 && (
                        <span className="flex items-center gap-1 text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">
                          <Star size={12} fill="currentColor" />
                          {repo.stars}
                        </span>
                      )}
                    </div>

                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                      {repo.description || repo.what_it_does || 'No description'}
                    </p>

                    {repo.tech_stack && (
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {(Array.isArray(repo.tech_stack)
                          ? repo.tech_stack
                          : repo.tech_stack.split(',').map(t => t.trim())
                        ).slice(0, 5).map((tech, i) => (
                          <span
                            key={i}
                            className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-md"
                          >
                            {tech}
                          </span>
                        ))}
                        {(Array.isArray(repo.tech_stack) ? repo.tech_stack.length : repo.tech_stack.split(',').length) > 5 && (
                          <span className="text-xs text-gray-400">
                            +{repo.tech_stack.length - 5} more
                          </span>
                        )}
                      </div>
                    )}

                    {repo.domain && (
                      <span className="inline-block mt-2 text-xs bg-teal-50 text-teal-600 px-2 py-1 rounded-md font-medium">
                        {repo.domain}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
