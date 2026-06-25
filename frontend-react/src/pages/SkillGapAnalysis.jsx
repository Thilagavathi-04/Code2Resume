import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Target, BookOpen, TrendingUp, CheckCircle2 } from 'lucide-react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import EmptyState from '../components/ui/EmptyState';
import Skeleton from '../components/ui/Skeleton';
import SkillBadge from '../components/ui/SkillBadge';
import Badge from '../components/ui/Badge';
import SkillRadarChart from '../components/skillgap/SkillRadarChart';
import LearningRoadmap from '../components/skillgap/LearningRoadmap';
import SkillProgressTracker from '../components/skillgap/SkillProgressTracker';
import v2 from '../api/v2';

const stagger = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
};
const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0 },
};

export default function SkillGapAnalysis() {
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [progress, setProgress] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalyses = async () => {
      try {
        const res = await v2.skillGap.list();
        const data = Array.isArray(res) ? res : (res.data || []);
        if (data.length > 0) {
          const latest = data[0];
          setResults(latest);
          setProgress(latest.progress || []);
        }
      } catch {
        setError('Unable to load skill gap analyses.');
      } finally {
        setLoading(false);
      }
    };
    fetchAnalyses();
  }, []);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setError(null);
    try {
      const payload = {
        existing_skills: results?.existing_skills || [],
        missing_skills: results?.missing_skills || [],
        learning_recommendations: results?.learning_recommendations || [],
        radar_data: results?.radar_data || {},
      };
      const res = await v2.skillGap.create(payload);
      const created = res.data || res;
      setResults(created);
      setProgress(created.progress || []);
    } catch {
      setError('Analysis failed. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleMarkComplete = (skillName) => {
    setProgress(prev =>
      prev.map(p => p.name === skillName ? { ...p, completed: true, currentLevel: p.targetLevel } : p)
    );
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="space-y-3">
          <Skeleton variant="text" width="200px" height="32px" />
          <Skeleton variant="text" width="400px" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="space-y-4">
            <Skeleton variant="text" width="40%" />
            <div className="flex flex-wrap gap-2">{[1, 2, 3, 4, 5].map(i => <Skeleton key={i} variant="rectangular" width="80px" height="32px" />)}</div>
          </Card>
          <Card className="space-y-4">
            <Skeleton variant="text" width="40%" />
            <div className="flex flex-wrap gap-2">{[1, 2, 3].map(i => <Skeleton key={i} variant="rectangular" width="80px" height="32px" />)}</div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <motion.div className="space-y-6" initial="hidden" animate="visible" variants={stagger}>
      <motion.div variants={item}>
        <Card className="bg-gradient-to-r from-indigo-600 to-purple-600 border-0 text-white">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Target className="w-6 h-6" />
                Skill Gap Analysis
              </h1>
              <p className="text-indigo-100 mt-1">Identify skill gaps and get personalized learning recommendations.</p>
            </div>
            <Button
              onClick={handleAnalyze}
              disabled={analyzing}
              loading={analyzing}
              variant="secondary"
              className="bg-white/20 hover:bg-white/30 text-white border-white/20"
            >
              <TrendingUp className="w-4 h-4" />
              {analyzing ? 'Analyzing...' : 'Analyze Skills'}
            </Button>
          </div>
        </Card>
      </motion.div>

      {analyzing && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="space-y-4">
            <Skeleton variant="text" width="40%" />
            <div className="flex flex-wrap gap-2">{[1, 2, 3, 4, 5].map(i => <Skeleton key={i} variant="rectangular" width="80px" height="32px" />)}</div>
          </Card>
          <Card className="space-y-4">
            <Skeleton variant="text" width="40%" />
            <div className="flex flex-wrap gap-2">{[1, 2, 3].map(i => <Skeleton key={i} variant="rectangular" width="80px" height="32px" />)}</div>
          </Card>
          <Card className="flex items-center justify-center"><Skeleton variant="circular" width="280px" height="280px" /></Card>
          <Card className="space-y-4">
            <Skeleton variant="text" width="50%" />
            {[1, 2, 3, 4].map(i => <Skeleton key={i} variant="rectangular" height="80px" />)}
          </Card>
        </div>
      )}

      {error && !results && (
        <EmptyState
          icon={Target}
          title="No Skill Analysis"
          description={error}
        />
      )}

      {!results && !analyzing && !error && (
        <EmptyState
          icon={Target}
          title="No Skill Analysis"
          description="Click Analyze Skills to identify gaps in your profile and get learning recommendations."
        />
      )}

      {results && !analyzing && (
        <motion.div initial="hidden" animate="visible" variants={stagger} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <motion.div variants={item}>
              <Card>
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                  Existing Skills
                </h3>
                <div className="flex flex-wrap gap-2">
                  {(results.existing_skills || results.existingSkills || []).map((skill) => (
                    <SkillBadge key={skill.name} name={skill.name} category={skill.category} proficiency={skill.proficiency} />
                  ))}
                </div>
              </Card>
            </motion.div>

            <motion.div variants={item}>
              <Card>
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <Target className="w-4 h-4 text-red-600" />
                  Missing Skills
                </h3>
                <div className="flex flex-wrap gap-2">
                  {(results.missing_skills || results.missingSkills || []).map((skill) => (
                    <Badge key={skill.name} color="red" size="md" className="gap-1.5">
                      {skill.name}
                      <span className="text-[10px] opacity-60">{skill.requiredLevel}</span>
                    </Badge>
                  ))}
                </div>
              </Card>
            </motion.div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <motion.div variants={item}>
              <Card className="flex flex-col items-center">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4 self-start">Skill Coverage</h3>
                <SkillRadarChart
                  categories={results.radar_data?.categories || results.radarCategories || []}
                  currentCoverage={results.radar_data?.currentCoverage || results.currentCoverage || []}
                  targetCoverage={results.radar_data?.targetCoverage || results.targetCoverage || []}
                />
              </Card>
            </motion.div>

            <motion.div variants={item}>
              <Card>
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-indigo-600" />
                  Learning Recommendations
                </h3>
                <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                  {Object.entries(
                    (results.learning_recommendations || results.recommendations || []).reduce((acc, rec) => {
                      if (!acc[rec.skill]) acc[rec.skill] = [];
                      acc[rec.skill].push(rec);
                      return acc;
                    }, {})
                  ).map(([skill, recs]) => (
                    <div key={skill}>
                      <p className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 mb-1.5 uppercase tracking-wide">{skill}</p>
                      {recs.map((rec, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.05 }}
                          className="p-2.5 rounded-lg bg-gray-50 dark:bg-slate-900 mb-2 last:mb-0"
                        >
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-gray-900 dark:text-white">{rec.title}</p>
                            <Badge color={rec.priority === 'high' ? 'red' : rec.priority === 'medium' ? 'amber' : 'green'} size="sm">
                              {rec.priority}
                            </Badge>
                          </div>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{rec.description}</p>
                          <div className="flex items-center gap-2 mt-1.5">
                            <Badge color="indigo" size="sm">{rec.type}</Badge>
                            <Badge color="gray" size="sm">{rec.estimatedTime}</Badge>
                            <Badge color="gray" size="sm">{rec.difficulty}</Badge>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  ))}
                </div>
              </Card>
            </motion.div>
          </div>

          <motion.div variants={item}>
            <Card>
              <LearningRoadmap steps={(results.learning_recommendations || results.recommendations || []).map(r => ({
                title: r.title,
                description: `${r.skill}: ${r.description}`,
                estimatedTime: r.estimatedTime,
                priority: r.priority,
                difficulty: r.difficulty,
                type: r.type,
              }))} />
            </Card>
          </motion.div>

          {progress.length > 0 && (
            <motion.div variants={item}>
              <Card>
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-purple-600" />
                  Skill Progress
                </h3>
                <SkillProgressTracker skills={progress} onMarkComplete={handleMarkComplete} />
              </Card>
            </motion.div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}
