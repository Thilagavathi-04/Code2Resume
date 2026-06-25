import { useState, useEffect, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import {
  Search, Filter, GitBranch, Code2, Layers, Wrench,
  BarChart3, Target, Star, Globe, ChevronRight, BookOpen, RefreshCw,
  Settings, Github,
} from 'lucide-react';
import { fetchUserRepos } from '../api/github';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import EmptyState from '../components/ui/EmptyState';
import Skeleton from '../components/ui/Skeleton';
import SkillBadge from '../components/ui/SkillBadge';
import RepoCard from '../components/github/RepoCard';
import TechTag from '../components/github/TechTag';
import SkillChart from '../components/github/SkillChart';
import { useToastStore } from '../components/ui/Toast';
import api from '../api/axiosConfig';
import { getCurrentUser } from '../api/auth';

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const staggerItem = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

const panelTransition = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
  transition: { duration: 0.25 },
};

const DOMAINS = [
  'Machine Learning', 'Deep Learning', 'Computer Vision', 'NLP',
  'Full Stack', 'Frontend', 'Backend', 'Mobile App',
  'Data Science', 'Cybersecurity', 'DevOps', 'Cloud Computing',
  'IoT', 'Blockchain',
];

const CATEGORIES = {
  language: 'language',
  framework: 'framework',
  database: 'database',
  tool: 'tool',
};

function getTechCategory(tech) {
  const lower = (tech || '').toLowerCase();
  const langs = ['javascript', 'typescript', 'python', 'java', 'go', 'rust', 'c++', 'c', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'dart'];
  const frameworks = ['react', 'vue', 'angular', 'next', 'nuxt', 'svelte', 'django', 'flask', 'fastapi', 'express', 'spring', 'rails', 'laravel', 'flutter', 'react native'];
  const databases = ['mysql', 'postgresql', 'mongo', 'redis', 'sqlite', 'elasticsearch', 'dynamodb', 'cassandra', 'neo4j'];
  const tools = ['docker', 'kubernetes', 'aws', 'gcp', 'azure', 'ci/cd', 'terraform', 'ansible', 'jenkins', 'github actions'];

  if (langs.some(l => lower.includes(l))) return CATEGORIES.language;
  if (frameworks.some(f => lower.includes(f))) return CATEGORIES.framework;
  if (databases.some(d => lower.includes(d))) return CATEGORIES.database;
  if (tools.some(t => lower.includes(t))) return CATEGORIES.tool;
  return 'default';
}

export default function GitHubAnalysis() {
  const navigate = useNavigate();
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [mobileTab, setMobileTab] = useState('list');
  const [githubConfigured, setGithubConfigured] = useState(true);
  const addToast = useToastStore(s => s.addToast);

  const loadRepos = useCallback(async () => {
    try {
      const data = await fetchUserRepos();
      setRepos(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load repos:', err);
      setRepos([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const checkGithubConfig = useCallback(async () => {
    try {
      const userData = await getCurrentUser();
      setGithubConfigured(!!userData.github_url);
    } catch {
      setGithubConfigured(false);
    }
  }, []);

  useEffect(() => { checkGithubConfig(); }, [checkGithubConfig]);
  useEffect(() => { loadRepos(); }, [loadRepos]);

  const handleSync = useCallback(async () => {
    setSyncing(true);
    try {
      const res = await api.post('/analyze-all');
      const { job_id } = res.data;
      addToast({ type: 'info', message: 'Sync started. Analyzing repositories...' });

      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await api.get(`/analysis-status/${job_id}`);
          const status = statusRes.data;
          if (status.status === 'completed') {
            clearInterval(pollInterval);
            addToast({ type: 'success', message: 'GitHub sync completed!' });
            await loadRepos();
            setSyncing(false);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            addToast({ type: 'error', message: status.error || 'Sync failed' });
            setSyncing(false);
          }
        } catch {
          clearInterval(pollInterval);
          addToast({ type: 'error', message: 'Failed to check sync status' });
          setSyncing(false);
        }
      }, 3000);
    } catch (err) {
      const msg = err?.response?.data?.detail || err?.message || 'Failed to start sync';
      addToast({ type: 'error', message: msg });
      setSyncing(false);
    }
  }, [addToast, loadRepos]);

  const filteredRepos = useMemo(() => {
    return repos.filter(repo => {
      const matchesSearch = !search ||
        (repo.name || '').toLowerCase().includes(search.toLowerCase()) ||
        (repo.description || '').toLowerCase().includes(search.toLowerCase());
      const matchesDomain = !selectedDomain || repo.domain === selectedDomain;
      return matchesSearch && matchesDomain;
    });
  }, [repos, search, selectedDomain]);

  const selectedData = useMemo(() => {
    if (!selectedRepo) return null;
    const repo = repos.find(r => r.id === selectedRepo || r.name === selectedRepo);
    if (!repo) return null;

    const techs = Array.isArray(repo.tech_stack)
      ? repo.tech_stack
      : typeof repo.tech_stack === 'string'
      ? repo.tech_stack.split(',').map(t => t.trim()).filter(Boolean)
      : [];

    const skills = Array.isArray(repo.skills)
      ? repo.skills
      : typeof repo.skills === 'string'
      ? repo.skills.split(',').map(s => s.trim()).filter(Boolean)
      : [];

    const frameworks = Array.isArray(repo.frameworks)
      ? repo.frameworks
      : typeof repo.frameworks === 'string'
      ? repo.frameworks.split(',').map(f => f.trim()).filter(Boolean)
      : [];

    const techCounts = {};
    techs.forEach(t => { techCounts[t] = (techCounts[t] || 0) + 1; });
    const skillCounts = {};
    skills.forEach(s => { skillCounts[s] = (skillCounts[s] || 0) + 1; });

    return {
      ...repo,
      techs,
      skills,
      frameworks,
      skillChart: Object.entries(skillCounts)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10),
    };
  }, [selectedRepo, repos]);

  const availableDomains = useMemo(() => {
    const domains = new Set();
    repos.forEach(r => { if (r.domain) domains.add(r.domain); });
    return DOMAINS.filter(d => domains.has(d));
  }, [repos]);

  const handleRepoSelect = useCallback((repo) => {
    setSelectedRepo(repo.id || repo.name);
    setMobileTab('details');
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="rectangular" height="80px" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} variant="rectangular" height="100px" />
            ))}
          </div>
          <div className="lg:col-span-2">
            <Skeleton variant="rectangular" height="400px" />
          </div>
        </div>
      </div>
    );
  }

  if (!githubConfigured) {
    return (
      <motion.div
        className="space-y-6"
        initial="hidden"
        animate="visible"
        variants={staggerContainer}
      >
        <motion.div variants={staggerItem}>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">GitHub Analysis</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Analyze your repositories and extract skills
            </p>
          </div>
        </motion.div>

        <motion.div variants={staggerItem}>
          <Card>
            <EmptyState
              icon={Github}
              title="GitHub not configured"
              description="Connect your GitHub account to analyze repositories and extract skills for your resume."
              actionLabel="Configure GitHub"
              onAction={() => navigate('/settings')}
            />
          </Card>
        </motion.div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="space-y-6"
      initial="hidden"
      animate="visible"
      variants={staggerContainer}
    >
      <motion.div variants={staggerItem}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">GitHub Analysis</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Analyze your repositories and extract skills
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge color="indigo" size="md">{repos.length} repositories</Badge>
            <Button variant="secondary" size="sm" onClick={handleSync} disabled={syncing}>
              <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
              {syncing ? 'Syncing...' : 'Sync'}
            </Button>
          </div>
        </div>
      </motion.div>

      <div className="lg:hidden flex gap-2">
        <Button
          variant={mobileTab === 'list' ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => setMobileTab('list')}
        >
          Repositories
        </Button>
        <Button
          variant={mobileTab === 'details' ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => setMobileTab('details')}
        >
          Details
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div
          variants={staggerItem}
          className={`space-y-4 ${mobileTab !== 'list' ? 'hidden lg:block' : ''}`}
        >
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search repositories..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          {availableDomains.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              <Filter className="w-4 h-4 text-gray-400" />
              {availableDomains.map(domain => (
                <button
                  key={domain}
                  onClick={() => setSelectedDomain(selectedDomain === domain ? null : domain)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                    selectedDomain === domain
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  {domain}
                </button>
              ))}
            </div>
          )}

          <div className="space-y-2 max-h-[60vh] overflow-y-auto pr-1">
            {filteredRepos.length === 0 ? (
              <EmptyState
                icon={GitBranch}
                title="No repositories found"
                description={search || selectedDomain ? 'Try adjusting your filters' : 'Connect your GitHub to see repositories'}
              />
            ) : (
              filteredRepos.map(repo => (
                <RepoCard
                  key={repo.id || repo.name}
                  repo={repo}
                  isSelected={selectedRepo === (repo.id || repo.name)}
                  onClick={() => handleRepoSelect(repo)}
                />
              ))
            )}
          </div>
        </motion.div>

        <motion.div
          variants={staggerItem}
          className={`lg:col-span-2 ${mobileTab !== 'details' ? 'hidden lg:block' : ''}`}
        >
          <AnimatePresence mode="wait">
            {selectedData ? (
              <motion.div key={selectedData.id || selectedData.name} {...panelTransition}>
                <Card className="space-y-6">
                  <div className="flex items-start justify-between">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                        {selectedData.name}
                      </h2>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {selectedData.description || 'No description'}
                      </p>
                    </div>
                    {selectedData.stars > 0 && (
                      <Badge color="amber" size="md">
                        <Star className="w-3.5 h-3.5" />
                        {selectedData.stars}
                      </Badge>
                    )}
                  </div>

                  {selectedData.language && (
                    <div className="flex items-center gap-2">
                      <Code2 className="w-4 h-4 text-gray-400" />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {selectedData.language}
                      </span>
                    </div>
                  )}

                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                      <Layers className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                      Technologies
                    </h3>
                    {selectedData.techs.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {selectedData.techs.map(tech => (
                          <TechTag key={tech} name={tech} category={getTechCategory(tech)} />
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-400 dark:text-gray-500">No technologies detected</p>
                    )}
                  </div>

                  {selectedData.frameworks.length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                        <Wrench className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                        Frameworks
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedData.frameworks.map(fw => (
                          <SkillBadge key={fw} name={fw} category="framework" />
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedData.skills.length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                        <Target className="w-4 h-4 text-green-600 dark:text-green-400" />
                        Extracted Skills
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedData.skills.map(skill => (
                          <SkillBadge key={skill} name={skill} category="language" />
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedData.readme && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                        <BookOpen className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        README
                      </h3>
                      <div className="prose prose-sm max-w-none dark:prose-invert p-4 rounded-xl bg-gray-50 dark:bg-slate-900 max-h-96 overflow-y-auto">
                        <ReactMarkdown>{selectedData.readme}</ReactMarkdown>
                      </div>
                    </div>
                  )}

                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                      Skill Distribution
                    </h3>
                    {selectedData.skillChart.length > 0 ? (
                      <SkillChart skills={selectedData.skillChart} />
                    ) : (
                      <p className="text-sm text-gray-400 dark:text-gray-500">No skill data available</p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="p-3 rounded-xl bg-gray-50 dark:bg-slate-900 text-center">
                      <p className="text-lg font-bold text-gray-900 dark:text-white">
                        {selectedData.techs.length}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Technologies</p>
                    </div>
                    <div className="p-3 rounded-xl bg-gray-50 dark:bg-slate-900 text-center">
                      <p className="text-lg font-bold text-gray-900 dark:text-white">
                        {selectedData.skills.length}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Skills</p>
                    </div>
                    <div className="p-3 rounded-xl bg-gray-50 dark:bg-slate-900 text-center">
                      <p className="text-lg font-bold text-gray-900 dark:text-white">
                        {selectedData.frameworks.length}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Frameworks</p>
                    </div>
                    <div className="p-3 rounded-xl bg-gray-50 dark:bg-slate-900 text-center">
                      <p className="text-lg font-bold text-gray-900 dark:text-white">
                        {selectedData.stars || 0}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Stars</p>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ) : (
              <motion.div key="empty" {...panelTransition}>
                <Card>
                  <EmptyState
                    icon={Globe}
                    title="Select a repository"
                    description="Choose a repository from the list to view its analysis details"
                  />
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </motion.div>
  );
}
