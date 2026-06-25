import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  Search,
  Code,
  Briefcase,
  Users,
  Video,
  BookmarkCheck,
  CheckCircle,
  BarChart3,
  Filter,
} from 'lucide-react';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import EmptyState from '../components/ui/EmptyState';
import Skeleton from '../components/ui/Skeleton';
import ProgressBar from '../components/ui/ProgressBar';
import QuestionCard from '../components/interview/QuestionCard';
import v2 from '../api/v2';

const SESSION_TYPES = [
  { id: 'technical', label: 'Technical', icon: Code, color: 'indigo' },
  { id: 'project', label: 'Project-Based', icon: Briefcase, color: 'purple' },
  { id: 'behavioral', label: 'Behavioral', icon: Users, color: 'green' },
  { id: 'mock', label: 'Mock Interview', icon: Video, color: 'amber' },
];

const DIFFICULTY_FILTERS = ['all', 'easy', 'medium', 'hard'];

export default function InterviewPrep() {
  const [loading, setLoading] = useState(true);
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [activeTab, setActiveTab] = useState('technical');
  const [searchQuery, setSearchQuery] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('all');
  const [completedIds, setCompletedIds] = useState(new Set());
  const [savedIds, setSavedIds] = useState(new Set());
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await v2.interviews.list();
        const data = Array.isArray(res) ? res : (res.data || []);
        setSessions(data);
        if (data.length > 0) {
          setActiveSession(data[0]);
        }
      } catch (_) {
        setSessions([]);
      } finally {
        setLoading(false);
      }
    };
    fetchSessions();
  }, []);

  const questions = useMemo(() => {
    if (!activeSession) return [];
    return (activeSession.questions || []).map((q, i) => ({
      ...q,
      id: q.id || i,
      type: q.type || activeSession.session_type || 'technical',
    }));
  }, [activeSession]);

  const filteredQuestions = useMemo(() => {
    return questions.filter((q) => {
      if (q.type !== activeTab) return false;
      if (difficultyFilter !== 'all' && q.difficulty !== difficultyFilter) return false;
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          q.text.toLowerCase().includes(query) ||
          (q.category && q.category.toLowerCase().includes(query))
        );
      }
      return true;
    });
  }, [questions, activeTab, difficultyFilter, searchQuery]);

  const tabQuestions = useMemo(() =>
    questions.filter((q) => q.type === activeTab),
    [questions, activeTab]
  );

  const completedCount = tabQuestions.filter((q) => completedIds.has(q.id)).length;
  const savedCount = tabQuestions.filter((q) => savedIds.has(q.id)).length;
  const totalQuestions = tabQuestions.length;
  const progressPercent = totalQuestions > 0 ? (completedCount / totalQuestions) * 100 : 0;

  const difficultyBreakdown = useMemo(() => {
    const counts = { easy: 0, medium: 0, hard: 0 };
    tabQuestions.forEach((q) => { counts[q.difficulty]++; });
    return counts;
  }, [tabQuestions]);

  const toggleComplete = async (id) => {
    setCompletedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
    if (activeSession) {
      const newCount = completedIds.has(id)
        ? activeSession.completed_count - 1
        : (activeSession.completed_count || 0) + 1;
      try {
        await v2.interviews.update(activeSession.id, { completed_count: newCount });
      } catch {}
    }
  };

  const toggleSave = (id) => {
    setSavedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleNewSession = async () => {
    setCreating(true);
    try {
      const res = await v2.interviews.create({
        title: `Session ${sessions.length + 1}`,
        session_type: activeTab,
        difficulty: 'medium',
      });
      const newSession = res.data || res;
      setSessions((prev) => [newSession, ...prev]);
      setActiveSession(newSession);
      setCompletedIds(new Set());
      setSavedIds(new Set());
    } catch (_) { /* api error */ } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="space-y-3">
          <Skeleton variant="text" width="200px" height="32px" />
          <Skeleton variant="text" width="300px" />
        </div>
        <div className="flex gap-2">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} variant="rectangular" width="120px" height="40px" />
          ))}
        </div>
        <div className="grid gap-4 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} variant="rectangular" height="120px" />
          ))}
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} variant="rectangular" height="100px" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Interview Preparation</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Practice questions to ace your next interview
          </p>
        </div>
        <Button onClick={handleNewSession} loading={creating}>
          <Plus className="w-4 h-4" />
          New Session
        </Button>
      </div>

      {sessions.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {sessions.map((session) => (
            <Card
              key={session.id}
              hover
              className={`cursor-pointer transition-all ${
                activeSession?.id === session.id
                  ? 'ring-2 ring-indigo-600 dark:ring-indigo-400'
                  : ''
              }`}
              onClick={() => {
                setActiveSession(session);
                setCompletedIds(new Set());
                setSavedIds(new Set());
              }}
            >
              <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                {session.title}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {session.session_type || 'General'} &middot; {(session.questions || []).length} questions
              </p>
              {session.completed_count != null && session.total_count != null && (
                <ProgressBar
                  value={session.total_count > 0 ? (session.completed_count / session.total_count) * 100 : 0}
                  color="green"
                  className="mt-2"
                />
              )}
            </Card>
          ))}
        </div>
      )}

      {!activeSession && sessions.length === 0 && (
        <EmptyState
          icon={Code}
          title="No Interview Sessions"
          description="Create a new session to start practicing interview questions."
          actionLabel="New Session"
          onAction={handleNewSession}
        />
      )}

      {activeSession && (
        <>
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
            {SESSION_TYPES.map((type) => {
              const Icon = type.icon;
              return (
                <button
                  key={type.id}
                  onClick={() => setActiveTab(type.id)}
                  className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all duration-200 ${
                    activeTab === type.id
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/25'
                      : 'bg-white dark:bg-slate-800 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-700'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {type.label}
                </button>
              );
            })}
          </div>

          <div className="flex flex-col lg:flex-row gap-6">
            <div className="flex-1 space-y-4">
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search questions..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-white text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  />
                </div>
                <div className="flex gap-1.5 bg-gray-100 dark:bg-gray-800 rounded-xl p-1">
                  {DIFFICULTY_FILTERS.map((d) => (
                    <button
                      key={d}
                      onClick={() => setDifficultyFilter(d)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all ${
                        difficultyFilter === d
                          ? 'bg-white dark:bg-slate-700 text-gray-900 dark:text-white shadow-sm'
                          : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                      }`}
                    >
                      {d}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <AnimatePresence mode="popLayout">
                  {filteredQuestions.length > 0 ? (
                    filteredQuestions.map((q) => (
                      <QuestionCard
                        key={q.id}
                        question={q}
                        completed={completedIds.has(q.id)}
                        saved={savedIds.has(q.id)}
                        onToggleComplete={() => toggleComplete(q.id)}
                        onToggleSave={() => toggleSave(q.id)}
                      />
                    ))
                  ) : (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <EmptyState
                        icon={Filter}
                        title="No questions found"
                        description="Try adjusting your filters or search query."
                      />
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>

            <div className="hidden lg:block w-72 flex-shrink-0 space-y-4">
              <Card>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                    <BarChart3 className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">Statistics</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Current tab</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Total Questions</span>
                      <span className="text-sm font-semibold text-gray-900 dark:text-white">{totalQuestions}</span>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Completed</span>
                      <span className="text-sm font-semibold text-green-600 dark:text-green-400">{completedCount}</span>
                    </div>
                    <ProgressBar value={progressPercent} color="green" />
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Saved</span>
                      <span className="text-sm font-semibold text-indigo-600 dark:text-indigo-400">{savedCount}</span>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-gray-100 dark:border-gray-700">
                    <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                      Difficulty Breakdown
                    </p>
                    <div className="space-y-2.5">
                      {Object.entries(difficultyBreakdown).map(([level, count]) => (
                        <div key={level} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className={`w-2 h-2 rounded-full ${
                              level === 'easy' ? 'bg-green-500' : level === 'medium' ? 'bg-amber-500' : 'bg-red-500'
                            }`} />
                            <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">{level}</span>
                          </div>
                          <span className="text-sm font-medium text-gray-900 dark:text-white">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
