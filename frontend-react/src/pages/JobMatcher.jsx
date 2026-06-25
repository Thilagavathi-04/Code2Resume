import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Briefcase, Target, Clock, Search, AlertTriangle } from 'lucide-react';
import v2 from '../api/v2';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import EmptyState from '../components/ui/EmptyState';
import Skeleton from '../components/ui/Skeleton';
import Badge from '../components/ui/Badge';
import MatchAnalysis from '../components/job/MatchAnalysis';
import SkillComparison from '../components/job/SkillComparison';

const stagger = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
};
const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0 },
};

export default function JobMatcher() {
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedResumeId, setSelectedResumeId] = useState('');
  const [selectedJobId, setSelectedJobId] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingData, setLoadingData] = useState(true);
  const [error, setError] = useState('');

  const loadData = useCallback(async () => {
    try {
      const [resumesRes, jobsRes] = await Promise.allSettled([
        v2.resumes.list(),
        v2.jobs.list(),
      ]);
      const resumesData = resumesRes.status === 'fulfilled' ? (resumesRes.value?.data || []) : [];
      const jobsData = jobsRes.status === 'fulfilled' ? (jobsRes.value?.data || []) : [];
      setResumes(Array.isArray(resumesData) ? resumesData : []);
      setJobs(Array.isArray(jobsData) ? jobsData : []);
      setHistory(
        (Array.isArray(jobsData) ? jobsData : []).slice(0, 5).map(j => ({
          id: j.id,
          title: j.title || 'Untitled',
          company: j.company || 'Unknown',
          score: j.match_score ?? null,
          date: j.created_at ? new Date(j.created_at).toLocaleDateString() : 'Recently',
        }))
      );
    } catch {
      setResumes([]);
      setJobs([]);
      setHistory([]);
    } finally {
      setLoadingData(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleAnalyze = async () => {
    if (!selectedResumeId || !selectedJobId) {
      setError('Please select both a resume and a job description.');
      return;
    }
    setAnalyzing(true);
    setError('');
    setResults(null);
    try {
      const res = await v2.jobs.analyze({ resume_id: selectedResumeId, job_description_id: selectedJobId });
      const data = res?.data || res;
      const matchResult = {
        score: data.match_score ?? data.score ?? 0,
        recommendation: data.recommendation || data.summary || '',
        breakdown: (data.breakdown ?? data.category_scores ?? []).map(b => {
          if (typeof b === 'object' && 'category' in b) return b;
          if (typeof b === 'string') return { category: b, score: 70 };
          return { category: b.category || b.name || 'skills', score: b.score ?? 70 };
        }),
        missingSkills: (data.missing_skills ?? data.missing_keywords ?? []).map(s => {
          if (typeof s === 'string') return { name: s, category: 'tool' };
          return { name: s.name || s.keyword || s, category: s.category || 'tool' };
        }),
        yourSkills: data.matching_keywords ?? data.your_skills ?? [],
        requiredSkills: data.required_skills ?? data.required_keywords ?? [],
        improvements: data.recommendations ?? data.improvements ?? [],
        requiredKeywords: (data.matching_keywords ?? data.keywords ?? []).map(k => {
          if (typeof k === 'string') return { keyword: k, found: true };
          return { keyword: k.keyword || k.name || k, found: k.found ?? !k.missing ?? true };
        }),
      };
      setResults(matchResult);
      const job = jobs.find(j => j.id === selectedJobId);
      setHistory(prev => [
        {
          id: Date.now(),
          title: job?.title || 'Untitled',
          company: job?.company || 'Unknown',
          score: matchResult.score,
          date: 'Just now',
        },
        ...prev,
      ].slice(0, 10));
    } catch {
      setError('Failed to analyze job match. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <motion.div className="space-y-6" initial="hidden" animate="visible" variants={stagger}>
      <motion.div variants={item}>
        <Card className="bg-gradient-to-r from-indigo-600 to-purple-600 border-0 text-white">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Target className="w-6 h-6" />
                Job Matcher
              </h1>
              <p className="text-indigo-100 mt-1">Compare your profile against job descriptions.</p>
            </div>
            <Button
              onClick={handleAnalyze}
              disabled={analyzing || !selectedResumeId || !selectedJobId}
              loading={analyzing}
              variant="secondary"
              className="bg-white/20 hover:bg-white/30 text-white border-white/20"
            >
              <Target className="w-4 h-4" />
              {analyzing ? 'Matching...' : 'Analyze Match'}
            </Button>
          </div>
        </Card>
      </motion.div>

      {error && (
        <motion.div variants={item}>
          <Card className="border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/10">
            <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm font-medium">{error}</span>
            </div>
          </Card>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <motion.div variants={item} className="lg:col-span-5 space-y-6">
          <Card>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-indigo-600" />
              Select Resume
            </h3>
            {loadingData ? (
              <Skeleton variant="rectangular" height="60px" />
            ) : resumes.length === 0 ? (
              <EmptyState
                icon={Briefcase}
                title="No Resumes Found"
                description="Create a resume first to match against jobs."
                actionLabel="Create Resume"
                onAction={() => window.location.href = '/resumes'}
              />
            ) : (
              <select
                value={selectedResumeId}
                onChange={(e) => setSelectedResumeId(e.target.value)}
                className="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Choose a resume...</option>
                {resumes.map(r => (
                  <option key={r.id} value={r.id}>{r.title || `Resume ${r.id}`}</option>
                ))}
              </select>
            )}
          </Card>

          <Card>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <Search className="w-4 h-4 text-purple-600" />
              Select Job Description
            </h3>
            {loadingData ? (
              <Skeleton variant="rectangular" height="60px" />
            ) : jobs.length === 0 ? (
              <EmptyState
                icon={Search}
                title="No Job Descriptions Found"
                description="Add a job description first to match against your resume."
                actionLabel="Add Job Description"
                onAction={() => window.location.href = '/jobs'}
              />
            ) : (
              <select
                value={selectedJobId}
                onChange={(e) => setSelectedJobId(e.target.value)}
                className="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Choose a job description...</option>
                {jobs.map(j => (
                  <option key={j.id} value={j.id}>{j.title || j.company || `Job ${j.id}`}</option>
                ))}
              </select>
            )}
          </Card>

          <Card>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <Clock className="w-4 h-4 text-purple-600" />
              Analysis History
            </h3>
            <div className="space-y-2">
              {history.map((h) => (
                <div key={h.id} className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-gray-50 dark:hover:bg-slate-900 transition-colors cursor-pointer">
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    h.score >= 70 ? 'bg-green-100 dark:bg-green-900/30' : h.score >= 40 ? 'bg-amber-100 dark:bg-amber-900/30' : h.score === null ? 'bg-gray-100 dark:bg-gray-800' : 'bg-red-100 dark:bg-red-900/30'
                  }`}>
                    <span className={`text-xs font-bold ${
                      h.score >= 70 ? 'text-green-600 dark:text-green-400' : h.score >= 40 ? 'text-amber-600 dark:text-amber-400' : h.score === null ? 'text-gray-400' : 'text-red-600 dark:text-red-400'
                    }`}>{h.score !== null ? `${h.score}%` : '—'}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{h.title}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{h.company} · {h.date}</p>
                  </div>
                </div>
              ))}
              {history.length === 0 && (
                <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-4">No previous analyses</p>
              )}
            </div>
          </Card>
        </motion.div>

        <motion.div variants={item} className="lg:col-span-7 space-y-6">
          {analyzing && (
            <div className="space-y-6">
              <Card className="flex items-center justify-center"><Skeleton variant="circular" width="160px" height="160px" /></Card>
              <Card className="space-y-4">
                <Skeleton variant="text" width="40%" />
                {[1, 2, 3].map(i => <Skeleton key={i} variant="rectangular" height="40px" />)}
              </Card>
              <Card className="space-y-4">
                <Skeleton variant="text" width="50%" />
                <Skeleton variant="rectangular" height="200px" />
              </Card>
            </div>
          )}

          {!results && !analyzing && (
            <EmptyState
              icon={Target}
              title="No Match Analysis"
              description="Select a resume and job description, then click Analyze Match to see how well your profile fits."
            />
          )}

          {results && !analyzing && (
            <motion.div initial="hidden" animate="visible" variants={stagger} className="space-y-6">
              <motion.div variants={item}>
                <Card>
                  <MatchAnalysis analysis={results} />
                </Card>
              </motion.div>

              <motion.div variants={item}>
                <Card>
                  <SkillComparison yourSkills={results.yourSkills} requiredSkills={results.requiredSkills} />
                </Card>
              </motion.div>

              {results.requiredKeywords.length > 0 && (
                <motion.div variants={item}>
                  <Card>
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                      <Search className="w-4 h-4 text-indigo-600" />
                      Keyword Analysis
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {results.requiredKeywords.map((kw, i) => (
                        <Badge key={i} color={kw.found ? 'green' : 'red'} size="sm">
                          {kw.found ? '✓' : '✗'} {kw.keyword}
                        </Badge>
                      ))}
                    </div>
                  </Card>
                </motion.div>
              )}

              {results.improvements.length > 0 && (
                <motion.div variants={item}>
                  <Card>
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Suggested Improvements</h3>
                    <div className="space-y-2">
                      {results.improvements.map((imp, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.05 }}
                          className="flex items-start gap-2"
                        >
                          <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 mt-0.5">{i + 1}.</span>
                          <span className="text-sm text-gray-700 dark:text-gray-300">{typeof imp === 'string' ? imp : imp.text || imp.description || JSON.stringify(imp)}</span>
                        </motion.div>
                      ))}
                    </div>
                  </Card>
                </motion.div>
              )}
            </motion.div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
}
