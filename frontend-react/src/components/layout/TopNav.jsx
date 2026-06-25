import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Sun, Moon, Bell, Menu, ChevronDown } from 'lucide-react';
import { useThemeStore } from '../../store/themeStore';

const routeTitles = {
  '/': 'Dashboard',
  '/analysis': 'GitHub Analysis',
  '/resume': 'Resume Builder',
  '/templates': 'Resume Templates',
  '/ats': 'ATS Analyzer',
  '/jobs': 'Job Matcher',
  '/skills': 'Skill Gap Analysis',
  '/interview': 'Interview Prep',
  '/analytics': 'Analytics',
  '/settings': 'Settings',
};

export default function TopNav({ onMenuClick }) {
  const location = useLocation();
  const { isDark, toggle } = useThemeStore();
  const title = routeTitles[location.pathname] || 'Code2Resume';

  return (
    <header className="h-16 bg-white/80 dark:bg-slate-900/80 backdrop-blur-lg border-b border-gray-100 dark:border-gray-700 flex items-center justify-between px-4 lg:px-6 sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
        <motion.h1
          key={title}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-xl font-semibold text-gray-900 dark:text-white"
        >
          {title}
        </motion.h1>
      </div>

      <div className="flex items-center gap-2">
        <div className="hidden md:flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-xl w-64">
          <Search className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search..."
            className="bg-transparent text-sm text-gray-900 dark:text-white placeholder-gray-400 outline-none w-full"
          />
        </div>

        <button
          onClick={toggle}
          className="p-2 rounded-xl text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 dark:text-gray-400 transition-colors"
        >
          {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        <button className="relative p-2 rounded-xl text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 dark:text-gray-400 transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
        </button>

        <div className="relative">
          <button className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-semibold text-sm">
              U
            </div>
            <ChevronDown className="w-4 h-4 text-gray-400 hidden sm:block" />
          </button>
        </div>
      </div>
    </header>
  );
}
