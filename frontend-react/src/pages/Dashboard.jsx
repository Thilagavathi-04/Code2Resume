import { useState, useEffect, useCallback } from 'react';
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
import ChatBox from '../components/dashboard/ChatBox';

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

  const loadRepos = useCallback(async () => {
    try {
      const data = await fetchUserRepos();
      setRepos(Array.isArray(data) ? data : []);
    } catch {
      setRepos([]);
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

      const repoCount = repos.length;
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
  }, [repos]);

  useEffect(() => {
    const loadAll = async () => {
      await loadRepos();
      setLoading(false);
    };
    loadAll();
  }, [loadRepos]);

  useEffect(() => {
    if (!loading) {
      loadV2Data();
    }
  }, [loading, loadV2Data]);

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
  }, [repos, loading]);

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
    { label: 'ATS Score', value: latestAtsScore ?? '—', icon: Zap, color: 'indigo', isCircular: latestAtsScore !== null },
    { label: 'Total Skills', value: skillCount || '—', icon: Code2, color: 'green', isText: skillCount === 0 },
    { label: 'GitHub Repos', value: repos.length || '—', icon: GitBranch, color: 'blue', isText: repos.length === 0 },
    { label: 'Resumes', value: resumeCount || '—', icon: FileText, color: 'purple', isText: resumeCount === 0 },
    { label: 'Job Match', value: '—', icon: Target, color: 'amber', isText: true },
  ];

  const quickActions = [
    { label: 'Generate Resume', icon: FileCode2, color: 'indigo', route: '/resumes' },
    { label: 'Analyze GitHub', icon: Search, color: 'blue', action: handleAnalyze },
    { label: 'Match Jobs', icon: Briefcase, color: 'amber', route: '/resumes' },
    { label: 'AI Chat', icon: MessageSquare, color: 'green', route: '/dashboard' },
  ];

  const iconBgColors = {
    indigo: 'bg-indigo-100 dark:bg-indigo-900/30',
    green: 'bg-green-100 dark:bg-green-900/30',
    blue: 'bg-blue-100 dark:bg-blue-900/30',
    purple: 'bg-purple-100 dark:bg-purple-900/30',
    amber: 'bg-amber-100 dark:bg-amber-900/30',
  };

  const iconColors = {
    indigo: 'text-indigo-600 dark:text-indigo-400',
    green: 'text-green-600 dark:text-green-400',
    blue: 'text-blue-600 dark:text-blue-400',
    purple: 'text-purple-600 dark:text-purple-400',
    amber: 'text-amber-600 dark:text-amber-400',
  };

  const circularColors = {
    indigo: '#4F46E5',
    green: '#16A34A',
    blue: '#2563EB',
    purple: '#9333EA',
    amber: '#D97706',
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
        <Card className="bg-gradient-to-r from-indigo-600 to-indigo-700 border-0 text-white">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold">Welcome back, {displayName}</h1>
              <p className="text-indigo-100 mt-1">Here's what's happening with your career profile.</p>
            </div>
            <Button
              onClick={handleAnalyze}
              disabled={analyzing}
              variant="secondary"
              className="bg-white/20 hover:bg-white/30 text-white border-white/20"
            >
              <RefreshCw className={`w-4 h-4 ${analyzing ? 'animate-spin' : ''}`} />
              {analyzing ? 'Analyzing...' : 'Update from GitHub'}
            </Button>
          </div>
        </Card>
      </motion.div>

      {analysisProgress > 0 && (
        <motion.div variants={staggerItem}>
          <Card>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                <Activity className="w-4 h-4 text-indigo-600 dark:text-indigo-400 animate-pulse" />
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

      <motion.div variants={staggerItem} className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        {stats.map((stat, i) => (
          <motion.div key={i} variants={staggerItem}>
            <Card hover className="flex flex-col items-center text-center !p-5">
              {stat.isCircular ? (
                <CircularScore
                  score={typeof stat.value === 'number' ? stat.value : 0}
                  size={64}
                  color={circularColors[stat.color]}
                  label={stat.label}
                />
              ) : (
                <>
                  <div className={`w-10 h-10 rounded-xl ${iconBgColors[stat.color]} flex items-center justify-center mb-3`}>
                    <stat.icon className={`w-5 h-5 ${iconColors[stat.color]}`} />
                  </div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{stat.label}</p>
                </>
              )}
            </Card>
          </motion.div>
        ))}
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <motion.div variants={staggerItem}>
            <ChatBox />
          </motion.div>

          <motion.div variants={staggerItem}>
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activities</h3>
              {activities.length === 0 ? (
                <div className="text-center py-8">
                  <Activity className="w-10 h-10 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                  <p className="text-sm text-gray-500 dark:text-gray-400">No activities yet. Analyze your GitHub to get started.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {activities.map((activity) => (
                    <div key={activity.id} className="flex items-start gap-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-slate-900 transition-colors">
                      <div className={`w-8 h-8 rounded-lg ${iconBgColors[activity.color]} flex items-center justify-center flex-shrink-0`}>
                        <activity.icon className={`w-4 h-4 ${iconColors[activity.color]}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">{activity.title}</p>
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
            <Card className="flex flex-col items-center">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 self-start">Interview Readiness</h3>
              <CircularScore score={interviewCount > 0 ? Math.min(50 + interviewCount * 10, 100) : 20} size={120} color="#4F46E5" />
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-3 text-center">
                {interviewCount > 0
                  ? `You have ${interviewCount} interview session${interviewCount === 1 ? '' : 's'}`
                  : 'Connect GitHub to improve your score'}
              </p>
              {resumeCount > 0 && (
                <div className="w-full mt-4 space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500 dark:text-gray-400">Profile Strength</span>
                    <span className="font-medium text-gray-700 dark:text-gray-300">{profileStrength}%</span>
                  </div>
                  <ProgressBar value={profileStrength} color="indigo" />
                </div>
              )}
            </Card>
          </motion.div>

          <motion.div variants={staggerItem}>
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-3">
                {quickActions.map((action, i) => (
                  <motion.button
                    key={i}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => action.route ? navigate(action.route) : action.action?.()}
                    className="flex flex-col items-center gap-2 p-4 rounded-xl bg-gray-50 dark:bg-slate-900 hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors text-center group"
                  >
                    <div className={`w-10 h-10 rounded-xl ${iconBgColors[action.color]} flex items-center justify-center group-hover:scale-110 transition-transform`}>
                      <action.icon className={`w-5 h-5 ${iconColors[action.color]}`} />
                    </div>
                    <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{action.label}</span>
                  </motion.button>
                ))}
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
