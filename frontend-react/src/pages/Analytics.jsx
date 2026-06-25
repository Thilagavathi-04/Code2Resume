import { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  FileText,
  Sparkles,
  Target,
  ArrowUpRight,
  ArrowDownRight,
  BarChart3,
  Calendar,
} from 'lucide-react';
import Card from '../components/ui/Card';
import EmptyState from '../components/ui/EmptyState';
import Skeleton from '../components/ui/Skeleton';
import ATSTrendChart from '../components/analytics/ATSTrendChart';
import SkillGrowthChart from '../components/analytics/SkillGrowthChart';
import MatchTrendChart from '../components/analytics/MatchTrendChart';
import v2 from '../api/v2';

const DATE_RANGES = [
  { id: 7, label: 'Last 7 days' },
  { id: 30, label: 'Last 30 days' },
  { id: 90, label: 'Last 90 days' },
];

const colorMap = [
  'bg-gray-100 dark:bg-gray-800',
  'bg-indigo-200 dark:bg-indigo-900/40',
  'bg-indigo-300 dark:bg-indigo-800/50',
  'bg-indigo-400 dark:bg-indigo-700/60',
  'bg-indigo-600 dark:bg-indigo-500',
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 15 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export default function Analytics() {
  const [dateRange, setDateRange] = useState(30);
  const [loading, setLoading] = useState(true);
  const [resumes, setResumes] = useState([]);
  const [atsReports, setAtsReports] = useState([]);
  const [skillGaps, setSkillGaps] = useState([]);
  const [interviews, setInterviews] = useState([]);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [rRes, aRes, sRes, iRes] = await Promise.allSettled([
          v2.resumes.list(),
          v2.jobs.getATSReports(),
          v2.skillGap.list(),
          v2.interviews.list(),
        ]);
        if (rRes.status === 'fulfilled') setResumes(Array.isArray(rRes.value) ? rRes.value : (rRes.value?.data || []));
        if (aRes.status === 'fulfilled') setAtsReports(Array.isArray(aRes.value) ? aRes.value : (aRes.value?.data || []));
        if (sRes.status === 'fulfilled') setSkillGaps(Array.isArray(sRes.value) ? sRes.value : (sRes.value?.data || []));
        if (iRes.status === 'fulfilled') setInterviews(Array.isArray(iRes.value) ? iRes.value : (iRes.value?.data || []));
      } catch (_) { /* unreachable */ } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const metrics = useMemo(() => {
    const avgAts = atsReports.length > 0
      ? Math.round(atsReports.reduce((s, r) => s + (r.overall_score || 0), 0) / atsReports.length)
      : 0;

    const prevReports = atsReports.filter((r) => {
      const d = new Date(r.created_at);
      const now = new Date();
      return (now - d) / 86400000 > dateRange / 2;
    });
    const prevAvg = prevReports.length > 0
      ? Math.round(prevReports.reduce((s, r) => s + (r.overall_score || 0), 0) / prevReports.length)
      : avgAts;
    const change = prevAvg > 0 ? Math.round(((avgAts - prevAvg) / prevAvg) * 100) : 0;

    const newSkills = skillGaps.reduce((sum, sg) => {
      return sum + (sg.missing_skills || sg.missingSkills || []).length;
    }, 0);

    const totalSessions = interviews.length;
    const completedSessions = interviews.filter((s) => s.completed_count && s.total_count && s.completed_count >= s.total_count).length;
    const readiness = totalSessions > 0 ? Math.round((completedSessions / totalSessions) * 100) : 0;

    return [
      {
        title: 'ATS Score Trend',
        value: String(avgAts),
        change: change !== 0 ? `${change > 0 ? '+' : ''}${change}%` : null,
        positive: change >= 0,
        icon: TrendingUp,
        color: 'indigo',
      },
      {
        title: 'Resume Performance',
        value: String(resumes.length),
        subtitle: `avg score: ${avgAts}`,
        icon: FileText,
        color: 'purple',
      },
      {
        title: 'Skill Growth',
        value: String(newSkills),
        subtitle: 'new skills',
        icon: Sparkles,
        color: 'green',
      },
      {
        title: 'Interview Readiness',
        value: `${readiness}%`,
        icon: Target,
        color: 'amber',
      },
    ];
  }, [atsReports, resumes, skillGaps, interviews, dateRange]);

  const hasData = resumes.length > 0 || atsReports.length > 0 || skillGaps.length > 0 || interviews.length > 0;

  const heatmapData = useMemo(() => {
    return Array.from({ length: 20 }, () =>
      Array.from({ length: 7 }, () => 0)
    );
  }, []);

  const atsChartData = useMemo(() => {
    return atsReports
      .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      .slice(-10)
      .map((r) => ({
        date: new Date(r.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        score: r.overall_score || 0,
      }));
  }, [atsReports]);

  const barChartData = useMemo(() => {
    return atsReports
      .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      .slice(-10)
      .map((r) => r.overall_score || 0);
  }, [atsReports]);

  const skillGrowthData = useMemo(() => {
    const counts = {};
    skillGaps.forEach((sg) => {
      (sg.existing_skills || sg.existingSkills || []).forEach((s) => {
        const name = typeof s === 'string' ? s : s.name;
        counts[name] = (counts[name] || 0) + 1;
      });
    });
    const colors = ['#4F46E5', '#7C3AED', '#2563EB', '#059669', '#0891B2', '#D97706'];
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6)
      .map(([category, count], i) => ({
        category,
        count,
        color: colors[i % colors.length],
      }));
  }, [skillGaps]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="space-y-3">
          <Skeleton variant="text" width="200px" height="32px" />
          <Skeleton variant="text" width="300px" />
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} variant="rectangular" height="120px" />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} variant="rectangular" height="240px" />)}
        </div>
      </div>
    );
  }

  if (!hasData) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Track your career readiness progress
          </p>
        </div>
        <EmptyState
          icon={BarChart3}
          title="No analytics yet"
          description="Generate resumes and complete interview questions to see your analytics here."
        />
      </div>
    );
  }

  return (
    <motion.div
      className="space-y-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={itemVariants} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Track your career readiness progress
          </p>
        </div>
        <div className="flex gap-1.5 bg-gray-100 dark:bg-gray-800 rounded-xl p-1">
          {DATE_RANGES.map((range) => (
            <button
              key={range.id}
              onClick={() => setDateRange(range.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                dateRange === range.id
                  ? 'bg-white dark:bg-slate-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              {range.label}
            </button>
          ))}
        </div>
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          const bgColors = {
            indigo: 'bg-indigo-100 dark:bg-indigo-900/30',
            purple: 'bg-purple-100 dark:bg-purple-900/30',
            green: 'bg-green-100 dark:bg-green-900/30',
            amber: 'bg-amber-100 dark:bg-amber-900/30',
          };
          const iconColors = {
            indigo: 'text-indigo-600 dark:text-indigo-400',
            purple: 'text-purple-600 dark:text-purple-400',
            green: 'text-green-600 dark:text-green-400',
            amber: 'text-amber-600 dark:text-amber-400',
          };
          return (
            <Card key={metric.title} hover>
              <div className="flex items-start justify-between">
                <div className={`w-10 h-10 rounded-xl ${bgColors[metric.color]} flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 ${iconColors[metric.color]}`} />
                </div>
                {metric.change && (
                  <span className={`inline-flex items-center gap-0.5 text-xs font-semibold ${
                    metric.positive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                  }`}>
                    {metric.positive ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                    {metric.change}
                  </span>
                )}
              </div>
              <div className="mt-3">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{metric.value}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  {metric.subtitle || metric.title}
                </p>
              </div>
            </Card>
          );
        })}
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">ATS Score Trend</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Resume optimization over time</p>
          </div>
          {atsChartData.length > 0 ? (
            <ATSTrendChart data={atsChartData} height={180} />
          ) : (
            <div className="flex items-center justify-center h-[180px] text-sm text-gray-400">No ATS data available</div>
          )}
        </Card>

        <Card>
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Resume Improvement</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Score progression per generation</p>
          </div>
          <div className="w-full overflow-x-auto">
            <svg viewBox="0 0 600 180" className="w-full" style={{ minWidth: 280 }}>
              {[0, 25, 50, 75, 100].map((v) => {
                const y = 10 + (1 - v / 100) * 140;
                return (
                  <g key={v}>
                    <line x1="40" y1={y} x2="580" y2={y} stroke="currentColor" className="text-gray-100 dark:text-gray-700" strokeDasharray="4 4" />
                    <text x="35" y={y + 4} textAnchor="end" className="fill-gray-400 dark:fill-gray-500" fontSize="11">{v}</text>
                  </g>
                );
              })}
              {barChartData.length > 0 ? (
                barChartData.map((v, i) => {
                  const x = 60 + i * 52;
                  const barH = (v / 100) * 140;
                  return (
                    <g key={i}>
                      <rect
                        x={x}
                        y={150 - barH}
                        width="36"
                        height={barH}
                        rx="6"
                        fill="#4F46E5"
                        className="transition-all duration-500"
                        opacity={0.85}
                      />
                      <text x={x + 18} y="168" textAnchor="middle" className="fill-gray-400 dark:fill-gray-500" fontSize="9">
                        {`D${i + 1}`}
                      </text>
                    </g>
                  );
                })
              ) : (
                <text x="300" y="90" textAnchor="middle" className="fill-gray-400 dark:fill-gray-500" fontSize="12">No data</text>
              )}
            </svg>
          </div>
        </Card>

        <Card>
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Skill Growth</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Skills detected from your repositories</p>
          </div>
          {skillGrowthData.length > 0 ? (
            <SkillGrowthChart data={skillGrowthData} height={180} />
          ) : (
            <div className="flex items-center justify-center h-[180px] text-sm text-gray-400">No skill data available</div>
          )}
        </Card>

        <Card>
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Job Match Trends</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Match percentage over time</p>
          </div>
          <MatchTrendChart height={180} />
        </Card>
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Activity Heatmap</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Your activity over the last 20 weeks</p>
            </div>
            <Calendar className="w-4 h-4 text-gray-400" />
          </div>
          <div className="flex gap-1.5 overflow-x-auto pb-1">
            {heatmapData.map((week, wi) => (
              <div key={wi} className="flex flex-col gap-1.5">
                {week.map((level, di) => (
                  <div
                    key={di}
                    className={`w-3 h-3 rounded-sm ${colorMap[level]}`}
                    title={`Week ${wi + 1}, Day ${di + 1}`}
                  />
                ))}
              </div>
            ))}
          </div>
          <div className="flex items-center justify-end gap-1.5 mt-3">
            <span className="text-xs text-gray-400 dark:text-gray-500">Less</span>
            {colorMap.map((c, i) => (
              <div key={i} className={`w-3 h-3 rounded-sm ${c}`} />
            ))}
            <span className="text-xs text-gray-400 dark:text-gray-500">More</span>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
}
