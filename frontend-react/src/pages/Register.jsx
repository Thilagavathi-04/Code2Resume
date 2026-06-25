import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Eye, EyeOff, User, Github, UserCircle, ArrowRight, ArrowLeft, Check, AlertCircle } from 'lucide-react';
import { registerUser } from '../api/auth';
import { useAuthStore } from '../store/authStore';
import Button from '../components/ui/Button';

const steps = [
  { id: 1, label: 'Account', icon: User },
  { id: 2, label: 'GitHub', icon: Github },
  { id: 3, label: 'Profile', icon: UserCircle },
];

const slideVariants = {
  enter: (direction) => ({ x: direction > 0 ? 300 : -300, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit: (direction) => ({ x: direction > 0 ? -300 : 300, opacity: 0 }),
};

export default function Register() {
  const [step, setStep] = useState(1);
  const [direction, setDirection] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    github_url: '',
    github_token: '',
    linkedin_id: '',
    leetcode_id: '',
    mobile_number: '',
  });
  const navigate = useNavigate();
  const setAuth = useAuthStore(state => state.setAuth);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const validateStep = () => {
    if (step === 1) {
      if (!formData.username || formData.username.length < 3) {
        setError('Username must be at least 3 characters');
        return false;
      }
      if (!formData.password || formData.password.length < 6) {
        setError('Password must be at least 6 characters');
        return false;
      }
    }
    if (step === 2) {
      if (!formData.github_url) {
        setError('GitHub URL is required');
        return false;
      }
      if (!formData.github_token) {
        setError('GitHub token is required');
        return false;
      }
    }
    return true;
  };

  const nextStep = () => {
    setError('');
    if (validateStep()) {
      setDirection(1);
      setStep(step + 1);
    }
  };

  const prevStep = () => {
    setError('');
    setDirection(-1);
    setStep(step - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await registerUser(formData);
      setAuth(response.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      <div className="hidden lg:flex lg:w-1/2 xl:w-[55%] relative bg-gradient-to-br from-indigo-600 via-indigo-700 to-indigo-900 overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)',
            backgroundSize: '24px 24px',
          }} />
        </div>

        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-400/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-indigo-300/20 rounded-full blur-3xl translate-y-1/3 -translate-x-1/4" />

        <motion.div
          className="relative z-10 flex flex-col justify-center px-12 xl:px-20 text-white"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold">Code2Resume</span>
          </div>

          <h1 className="text-4xl xl:text-5xl font-bold leading-tight mb-4">
            Start your journey with
            <span className="text-indigo-200"> Code2Resume</span>
          </h1>
          <p className="text-lg text-indigo-100 max-w-lg mb-10">
            Join developers who use AI to create professional resumes from their code.
          </p>

          <div className="space-y-3">
            {['Automatically analyze GitHub repos', 'AI-powered domain classification', 'Generate LaTeX resumes instantly', 'Chat with AI about your projects'].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + i * 0.1 }}
                className="flex items-center gap-3 p-3 rounded-xl bg-white/10 backdrop-blur-sm border border-white/10"
              >
                <div className="w-6 h-6 rounded-full bg-green-400/20 flex items-center justify-center flex-shrink-0">
                  <Check className="w-3.5 h-3.5 text-green-300" />
                </div>
                <span className="text-sm text-indigo-100">{feature}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      <div className="w-full lg:w-1/2 xl:w-[45%] flex items-center justify-center p-6 sm:p-8 bg-white dark:bg-slate-950 overflow-auto">
        <motion.div
          className="w-full max-w-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
            <div className="w-10 h-10 bg-indigo-600 rounded-2xl flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900 dark:text-white">Code2Resume</span>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Create your account</h2>
            <p className="text-gray-500 dark:text-gray-400 mt-1">Step {step} of 3 — {steps[step - 1].label}</p>
          </div>

          <div className="flex items-center gap-2 mb-8">
            {steps.map((s, i) => (
              <div key={s.id} className="flex items-center flex-1">
                <div className="flex items-center gap-2">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300 ${
                    step > s.id
                      ? 'bg-indigo-600 text-white'
                      : step === s.id
                      ? 'bg-indigo-600 text-white ring-4 ring-indigo-100 dark:ring-indigo-900'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500'
                  }`}>
                    {step > s.id ? <Check className="w-4 h-4" /> : s.id}
                  </div>
                  <span className={`text-sm font-medium hidden sm:inline transition-colors ${
                    step >= s.id ? 'text-gray-900 dark:text-white' : 'text-gray-400 dark:text-gray-500'
                  }`}>
                    {s.label}
                  </span>
                </div>
                {i < steps.length - 1 && (
                  <div className={`flex-1 h-0.5 mx-3 rounded-full transition-colors duration-300 ${
                    step > s.id ? 'bg-indigo-600' : 'bg-gray-200 dark:bg-gray-700'
                  }`} />
                )}
              </div>
            ))}
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 flex items-center gap-2"
            >
              <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </motion.div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="relative overflow-hidden" style={{ minHeight: '320px' }}>
              <AnimatePresence mode="wait" custom={direction}>
                {step === 1 && (
                  <motion.div
                    key="step1"
                    custom={direction}
                    variants={slideVariants}
                    initial="enter"
                    animate="center"
                    exit="exit"
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                    className="space-y-4"
                  >
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Username</label>
                      <input
                        type="text"
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        placeholder="johndoe"
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Password</label>
                      <div className="relative">
                        <input
                          type={showPassword ? 'text' : 'password'}
                          name="password"
                          value={formData.password}
                          onChange={handleChange}
                          placeholder="At least 6 characters"
                          className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all pr-12"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        >
                          {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>
                    <div className="pt-4">
                      <Button type="button" onClick={nextStep} className="w-full" size="lg">
                        Continue <ArrowRight className="w-4 h-4" />
                      </Button>
                    </div>
                  </motion.div>
                )}

                {step === 2 && (
                  <motion.div
                    key="step2"
                    custom={direction}
                    variants={slideVariants}
                    initial="enter"
                    animate="center"
                    exit="exit"
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                    className="space-y-4"
                  >
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">GitHub URL</label>
                      <input
                        type="url"
                        name="github_url"
                        value={formData.github_url}
                        onChange={handleChange}
                        placeholder="https://github.com/username"
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">GitHub Token</label>
                      <input
                        type="password"
                        name="github_token"
                        value={formData.github_token}
                        onChange={handleChange}
                        placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                      />
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-1.5">
                        Generate at GitHub Settings → Developer settings → Personal access tokens
                      </p>
                    </div>
                    <div className="flex gap-3 pt-4">
                      <Button type="button" onClick={prevStep} variant="secondary" className="flex-1" size="lg">
                        <ArrowLeft className="w-4 h-4" /> Back
                      </Button>
                      <Button type="button" onClick={nextStep} className="flex-1" size="lg">
                        Continue <ArrowRight className="w-4 h-4" />
                      </Button>
                    </div>
                  </motion.div>
                )}

                {step === 3 && (
                  <motion.div
                    key="step3"
                    custom={direction}
                    variants={slideVariants}
                    initial="enter"
                    animate="center"
                    exit="exit"
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                    className="space-y-4"
                  >
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                      Optional: add more details to enhance your resume
                    </p>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">LinkedIn ID</label>
                      <input
                        type="text"
                        name="linkedin_id"
                        value={formData.linkedin_id}
                        onChange={handleChange}
                        placeholder="your-linkedin-id"
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">LeetCode ID</label>
                      <input
                        type="text"
                        name="leetcode_id"
                        value={formData.leetcode_id}
                        onChange={handleChange}
                        placeholder="your-leetcode-id"
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Mobile Number</label>
                      <input
                        type="tel"
                        name="mobile_number"
                        value={formData.mobile_number}
                        onChange={handleChange}
                        placeholder="+1 234 567 890"
                        className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-slate-900 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                      />
                    </div>
                    <div className="flex gap-3 pt-4">
                      <Button type="button" onClick={prevStep} variant="secondary" className="flex-1" size="lg">
                        <ArrowLeft className="w-4 h-4" /> Back
                      </Button>
                      <Button type="submit" loading={loading} className="flex-1" size="lg">
                        Create Account
                      </Button>
                    </div>
                    <button
                      type="button"
                      onClick={handleSubmit}
                      className="w-full text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 py-2 transition-colors"
                    >
                      Skip for now
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </form>

          <p className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
            Already have an account?{' '}
            <Link to="/" className="text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 font-medium transition-colors">
              Sign in
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
