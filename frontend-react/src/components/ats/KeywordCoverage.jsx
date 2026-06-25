import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Search, Check, X, Copy, CheckCircle2 } from 'lucide-react';
import Badge from '../ui/Badge';

export default function KeywordCoverage({ keywords = [] }) {
  const [filter, setFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [copied, setCopied] = useState(false);

  const filtered = useMemo(() => keywords.filter(k => {
    const matchesText = k.keyword.toLowerCase().includes(filter.toLowerCase());
    if (statusFilter === 'found') return matchesText && k.found;
    if (statusFilter === 'missing') return matchesText && !k.found;
    return matchesText;
  }), [keywords, filter, statusFilter]);

  const foundCount = keywords.filter(k => k.found).length;
  const missingCount = keywords.filter(k => !k.found).length;
  const coveragePct = keywords.length > 0 ? Math.round((foundCount / keywords.length) * 100) : 0;

  const handleCopyMissing = () => {
    const missing = keywords.filter(k => !k.found).map(k => k.keyword).join(', ');
    navigator.clipboard.writeText(missing);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            Keyword Coverage
            <Badge color={coveragePct >= 70 ? 'green' : coveragePct >= 40 ? 'amber' : 'red'} size="sm">
              {coveragePct}%
            </Badge>
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            {foundCount} found, {missingCount} missing out of {keywords.length} keywords
          </p>
        </div>
        <div className="flex gap-1.5">
          {missingCount > 0 && (
            <button
              onClick={handleCopyMissing}
              className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-400 dark:hover:bg-gray-600 transition-colors"
            >
              {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
              {copied ? 'Copied!' : 'Copy Missing'}
            </button>
          )}
          {['all', 'found', 'missing'].map(s => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-2.5 py-1 text-xs font-medium rounded-lg transition-colors capitalize ${
                statusFilter === s
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-400 dark:hover:bg-gray-600'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {keywords.length > 0 && (
        <div className="w-full h-3 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${coveragePct}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className={`h-full rounded-full ${
              coveragePct >= 70 ? 'bg-green-500' : coveragePct >= 40 ? 'bg-amber-500' : 'bg-red-500'
            }`}
          />
        </div>
      )}

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search keywords..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="w-full pl-9 pr-3 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <div className="flex flex-wrap gap-2">
        {filtered.map((kw, i) => (
          <motion.div
            key={kw.keyword}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.02 }}
          >
            <Badge
              color={kw.found ? 'green' : 'red'}
              size="sm"
              className="gap-1.5 cursor-default hover:shadow-sm transition-shadow"
            >
              {kw.found ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
              {kw.keyword}
            </Badge>
          </motion.div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-8">
          <Search className="w-8 h-8 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
          <p className="text-sm text-gray-400 dark:text-gray-500">No keywords match your filter.</p>
        </div>
      )}
    </div>
  );
}
