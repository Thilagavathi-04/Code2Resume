import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Zap, Code2, GitBranch, FileText, Target,
  RefreshCw, Activity, GitCommit,
  FileCode2, Search, Briefcase, MessageSquare,
  ArrowRight, Clock, CheckCircle2,
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { fetchUserRepos, analyzeGithub, getAnalysisStatus } from '../api/github';
import v2 from '../api/v2';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import CircularScore from '../components/ui/CircularScore';
import ProgressBar from '../components/ui/ProgressBar';
import Skeleton from '../components/ui/Skeleton';

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
};

const staggerItem = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0 },
};

export default function Dashboard() {
  const user = useAuthStore(state => state.user);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [repos, setRepos] = useState([]);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisStatus, setAnalysisStatus] = useState('');
  const [activities, setActivities] = useState([]);
  const [resumeCount, setResumeCount] = useState(0);
  const [skillCount, setSkillCount] = useState(0);
  const [interviewCount, setInterviewCount] = useState(0);
  const [latestAtsScore, setLatestAtsScore] = useState(null);
  const [profileStrength, setProfileStrength] = useState(0);
  const reposRef = useRef([]);
  const loadedRef = useRef(false);

  const loadRepos = useCallback(async () => {
    try {
      const data = await fetchUserRepos();
      const reposArr = Array.isArray(data) ? data : [];
      setRepos(reposArr);
      reposRef.current = reposArr;
    } catch {
      setRepos([]);
      reposRef.current = [];
    }
  }, []);

  const loadV2Data = useCallback(async () => {
    try {
      const [resumesRes, interviewsRes, atsReportsRes] = await Promise.allSettled([
        v2.resumes.list(),
        v2.interviews.list(),
        v2.jobs.getATSReports(),
      ]);

      const resumes = resumesRes.status === 'fulfilled' ? (resumesRes.value?.data || []) : [];
      const interviews = interviewsRes.status === 'fulfilled' ? (interviewsRes.value?.data || []) : [];
      const atsReports = atsReportsRes.status === 'fulfilled' ? (atsReportsRes.value?.data || []) : [];

      setResumeCount(Array.isArray(resumes) ? resumes.length : 0);

      const allSkills = new Set();
      if (Array.isArray(resumes)) {
        resumes.forEach(r => {
          if (Array.isArray(r.skills)) r.skills.forEach(s => allSkills.add(s.name || s));
        });
      }
      setSkillCount(allSkills.size);
      setInterviewCount(Array.isArray(interviews) ? interviews.length : 0);

      if (Array.isArray(atsReports) && atsReports.length > 0) {
        const sorted = [...atsReports].sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
        setLatestAtsScore(sorted[0].overall_score ?? sorted[0].score ?? null);
      }

      const repoCount = reposRef.current.length;
      const strengthParts = [
        repoCount > 0 ? 1 : 0,
        resumes.length > 0 ? 1 : 0,
        allSkills.size > 0 ? 1 : 0,
      ];
      setProfileStrength(Math.round((strengthParts.reduce((a, b) => a + b, 0) / 3) * 100));

      const recentActivities = [];
      if (Array.isArray(resumes)) {
        resumes.slice(0, 3).forEach(r => {
          recentActivities.push({
            id: `resume-${r.id}`,
            icon: FileText,
            title: `Resume: ${r.title || 'Untitled'}`,
            description: 'Resume created',
            time: r.created_at ? new Date(r.created_at).toLocaleDateString() : 'Recently',
            color: 'purple',
          });
        });
      }
      if (Array.isArray(interviews)) {
        interviews.slice(0, 3).forEach(s => {
          recentActivities.push({
            id: `interview-${s.id}`,
            icon: MessageSquare,
            title: `Interview: ${s.job_title || 'Session'}`,
            description: s.status || 'Completed',
            time: s.created_at ? new Date(s.created_at).toLocaleDateString() : 'Recently',
            color: 'green',
          });
        });
      }
      recentActivities.sort((a, b) => {
        const dateA = a.time === 'Recently' ? 0 : new Date(a.time).getTime();
        const dateB = b.time === 'Recently' ? 0 : new Date(b.time).getTime();
        return dateB - dateA;
      });
      setActivities(recentActivities.slice(0, 5));
    } catch {
      setResumeCount(0);
      setSkillCount(0);
      setInterviewCount(0);
      setLatestAtsScore(null);
      setProfileStrength(0);
      setActivities([]);
    }
  }, []);

  useEffect(() => {
    if (loadedRef.current) return;
    loadedRef.current = true;
    const loadAll = async () => {
      await Promise.all([loadRepos(), loadV2Data()]);
      setLoading(false);
    };
    loadAll();
  }, [loadRepos, loadV2Data]);

  useEffect(() => {
    if (!loading && repos.length > 0) {
      const techSet = new Set();
      repos.forEach(r => {
        const techs = Array.isArray(r.tech_stack)
          ? r.tech_stack
          : typeof r.tech_stack === 'string'
          ? r.tech_stack.split(',').map(t => t.trim())
          : [];
        techs.forEach(t => t && techSet.add(t));
      });

      const recent = repos.slice(0, 5).map((r, i) => ({
        id: i,
        icon: GitCommit,
        title: `Analyzed ${r.name || 'repository'}`,
        description: r.domain ? `Domain: ${r.domain}` : 'Code analysis complete',
        time: 'Recently',
        color: 'indigo',
      }));
      setActivities(prev => {
        const merged = [...recent, ...prev];
        const seen = new Set();
        return merged.filter(a => {
          if (seen.has(a.id)) return false;
          seen.add(a.id);
          return true;
        }).slice(0, 5);
      });
    }
  }, [repos.length > 0, loading]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setAnalysisProgress(10);
    setAnalysisStatus('Starting analysis...');
    try {
      const result = await analyzeGithub();
      if (result.job_id) {
        let attempts = 0;
        const interval = setInterval(async () => {
          try {
            const data = await getAnalysisStatus(result.job_id);
            if (data.status === 'processing') {
              setAnalysisProgress(prev => Math.min(prev + 5, 90));
              setAnalysisStatus(data.progress || 'Analyzing repositories...');
              attempts++;
              if (attempts >= 60) {
                clearInterval(interval);
                setAnalyzing(false);
                setAnalysisProgress(0);
              }
            } else if (data.status === 'completed') {
              clearInterval(interval);
              setAnalysisProgress(100);
              setAnalysisStatus('Analysis complete!');
              setAnalyzing(false);
              loadRepos();
              setTimeout(() => setAnalysisProgress(0), 2000);
            } else if (data.status === 'failed') {
              clearInterval(interval);
              setAnalyzing(false);
              setAnalysisProgress(0);
              setAnalysisStatus('Analysis failed');
            }
          } catch {
            clearInterval(interval);
            setAnalyzing(false);
            setAnalysisProgress(0);
          }
        }, 5000);
      }
    } catch {
      setAnalyzing(false);
      setAnalysisProgress(0);
    }
  };

  const uniqueTechCount = [...new Set(repos.flatMap(r =>
    Array.isArray(r.tech_stack) ? r.tech_stack : typeof r.tech_stack === 'string' ? r.tech_stack.split(',').map(t => t.trim()) : []
  ))].filter(Boolean).length;

  const stats = [
    { label: 'ATS Score', value: latestAtsScore ?? '—', icon: Zap, color: 'indigo' },
    { label: 'GitHub Repos', value: repos.length || '—', icon: GitBranch, color: 'blue', isText: repos.length === 0 },
    { label: 'Resumes', value: resumeCount || '—', icon: FileText, color: 'purple', isText: resumeCount === 0 },
    { label: 'Job Match', value: '—', icon: Target, color: 'amber', isText: true },
  ];

  const quickActions = [
    { label: 'Generate Resume', icon: FileCode2, color: 'indigo', route: '/resumes' },
    { label: 'Analyze GitHub', icon: Search, color: 'blue', action: handleAnalyze },
    { label: 'Match Jobs', icon: Briefcase, color: 'amber', route: '/resumes' },
    { label: 'AI Chat', icon: MessageSquare, color: 'green', route: '/chat' },
  ];

  const iconBgColors = {
    indigo: 'bg-gray-100 dark:bg-gray-900/30',
    green: 'bg-gray-100 dark:bg-gray-900/30',
    blue: 'bg-gray-100 dark:bg-gray-900/30',
    purple: 'bg-gray-100 dark:bg-gray-900/30',
    amber: 'bg-gray-100 dark:bg-gray-900/30',
  };

  const iconColors = {
    indigo: 'text-gray-900 dark:text-gray-400',
    green: 'text-gray-600 dark:text-gray-400',
    blue: 'text-gray-600 dark:text-gray-400',
    purple: 'text-gray-700 dark:text-gray-400',
    amber: 'text-gray-600 dark:text-gray-400',
  };

  const circularColors = {
    indigo: '#111827',
    green: '#4B5563',
    blue: '#374151',
    purple: '#1F2937',
    amber: '#6B7280',
  };

  const displayName = user?.username || 'User';

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="rectangular" height="120px" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} variant="rectangular" height="120px" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Skeleton variant="rectangular" height="200px" />
            <Skeleton variant="rectangular" height="300px" />
          </div>
          <div className="space-y-6">
            <Skeleton variant="rectangular" height="200px" />
            <Skeleton variant="rectangular" height="250px" />
          </div>
        </div>
      </div>
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
        <Card className="bg-gradient-to-br from-gray-900 via-gray-800 to-black border-0 text-white overflow-hidden relative">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2" />
          <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <p className="text-white/60 text-sm font-medium mb-1">Welcome back</p>
              <h1 className="text-3xl font-bold">{displayName}</h1>
              <p className="text-white/70 mt-2 max-w-md">Track your career profile, analyze GitHub projects, and generate professional resumes.</p>
            </div>
            <Button
              onClick={handleAnalyze}
              disabled={analyzing}
              variant="secondary"
              className="bg-white/10 hover:bg-white/20 text-white border-white/10 backdrop-blur-sm"
            >
              <RefreshCw className={`w-4 h-4 ${analyzing ? 'animate-spin' : ''}`} />
              {analyzing ? 'Analyzing...' : 'Sync GitHub'}
            </Button>
          </div>
        </Card>
      </motion.div>

      {analysisProgress > 0 && (
        <motion.div variants={staggerItem}>
          <Card>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-900/30 flex items-center justify-center">
                <Activity className="w-4 h-4 text-gray-900 dark:text-gray-400 animate-pulse" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">Analysis in Progress</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{analysisStatus}</p>
              </div>
            </div>
            <ProgressBar value={analysisProgress} color="indigo" showLabel />
          </Card>
        </motion.div>
      )}

      <motion.div variants={staggerItem} className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div key={i} variants={staggerItem}>
            <Card hover className="!p-5">
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-xl ${iconBgColors[stat.color]} flex items-center justify-center flex-shrink-0`}>
                  <stat.icon className={`w-6 h-6 ${iconColors[stat.color]}`} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {stat.isCircular ? (
                      <CircularScore
                        score={typeof stat.value === 'number' ? stat.value : 0}
                        size={40}
                        color={circularColors[stat.color]}
                      />
                    ) : stat.value}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{stat.label}</p>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <motion.div variants={staggerItem}>
            <Card>
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Activity</h3>
                {activities.length > 0 && (
                  <span className="text-xs text-gray-400 dark:text-gray-500">{activities.length} items</span>
                )}
              </div>
              {activities.length === 0 ? (
                <div className="text-center py-12">
                  <Activity className="w-12 h-12 text-gray-200 dark:text-gray-700 mx-auto mb-3" />
                  <p className="text-sm text-gray-500 dark:text-gray-400">No activities yet</p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">Analyze your GitHub to get started</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {activities.map((activity, idx) => (
                    <div key={activity.id} className={`flex items-center gap-3 p-3 rounded-xl transition-colors ${idx === 0 ? 'bg-gray-50 dark:bg-slate-900' : 'hover:bg-gray-50 dark:hover:bg-slate-900'}`}>
                      <div className={`w-9 h-9 rounded-lg ${iconBgColors[activity.color]} flex items-center justify-center flex-shrink-0`}>
                        <activity.icon className={`w-4 h-4 ${iconColors[activity.color]}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{activity.title}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{activity.description}</p>
                      </div>
                      <div className="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500 flex-shrink-0">
                        <Clock className="w-3 h-3" />
                        {activity.time}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </motion.div>
        </div>

        <div className="space-y-6">
          <motion.div variants={staggerItem}>
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h3>
              <div className="space-y-2">
                {quickActions.map((action, i) => (
                  <motion.button
                    key={i}
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    onClick={() => action.route ? navigate(action.route) : action.action?.()}
                    className="w-full flex items-center gap-3 p-3 rounded-xl bg-gray-50 dark:bg-slate-900 hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors text-left group"
                  >
                    <div className={`w-10 h-10 rounded-xl ${iconBgColors[action.color]} flex items-center justify-center group-hover:scale-105 transition-transform flex-shrink-0`}>
                      <action.icon className={`w-5 h-5 ${iconColors[action.color]}`} />
                    </div>
                    <div className="flex-1">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{action.label}</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-300 dark:text-gray-600 group-hover:text-gray-500 dark:group-hover:text-gray-400 transition-colors" />
                  </motion.button>
                ))}
              </div>
            </Card>
          </motion.div>

          <motion.div variants={staggerItem}>
            <Card className="flex flex-col items-center text-center">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 self-start">Profile Strength</h3>
              <CircularScore score={profileStrength} size={100} color="#111827" />
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-3">
                {profileStrength >= 80 ? 'Great profile!' : profileStrength >= 50 ? 'Good progress' : 'Keep building'}
              </p>
              <div className="w-full mt-4 space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-500 dark:text-gray-400">Complete profile</span>
                  <span className="font-medium text-gray-700 dark:text-gray-300">{profileStrength}%</span>
                </div>
                <ProgressBar value={profileStrength} color="indigo" />
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
