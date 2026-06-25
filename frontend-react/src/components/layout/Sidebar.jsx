import { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  GitBranch,
  FileText,
  Layout,
  CheckCircle,
  Target,
  BarChart3,
  MessageSquare,
  LineChart,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Code2,
  X,
  Briefcase,
} from 'lucide-react';
import { useThemeStore } from '../../store/themeStore';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/analysis', label: 'GitHub Analysis', icon: GitBranch },
  { path: '/builder', label: 'Resume Builder', icon: FileText },
  { path: '/templates', label: 'Resume Templates', icon: Layout },
  { path: '/ats', label: 'ATS Analyzer', icon: CheckCircle },
  { path: '/jobs', label: 'Job Matcher', icon: Target },
  { path: '/job-descriptions', label: 'Job Descriptions', icon: Briefcase },
  // { path: '/skills', label: 'Skill Gap Analysis', icon: BarChart3 },
  // { path: '/interview', label: 'Interview Prep', icon: MessageSquare },
  { path: '/analytics', label: 'Analytics', icon: LineChart },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar({ collapsed, onToggle, mobileOpen, onMobileClose }) {
  const location = useLocation();
  const { isDark, toggle } = useThemeStore();

  const sidebarContent = (
    <>
      <div className={`flex items-center ${collapsed ? 'justify-center' : 'justify-between'} px-4 h-16 border-b border-gray-100 dark:border-gray-700`}>
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <Code2 className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400">Code2Resume</span>
          </div>
        )}
        {collapsed && (
          <div className="w-9 h-9 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <Code2 className="w-5 h-5 text-white" />
          </div>
        )}
        <button
          onClick={onToggle}
          className="hidden lg:flex p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
        <button
          onClick={onMobileClose}
          className="lg:hidden p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onMobileClose}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/25'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          );
        })}
      </nav>

      <div className="p-3 border-t border-gray-100 dark:border-gray-700">
        <div className={`flex items-center gap-3 px-3 py-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 ${collapsed ? 'justify-center' : ''}`}>
          <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
            U
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">User</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">user@example.com</p>
            </div>
          )}
          {!collapsed && (
            <button
              onClick={() => {}}
              className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <motion.aside
        animate={{ width: collapsed ? 72 : 256 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="hidden lg:flex flex-col bg-white dark:bg-slate-900 border-r border-gray-100 dark:border-gray-700 h-screen sticky top-0 z-30"
      >
        {sidebarContent}
      </motion.aside>

      {/* Mobile sidebar */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 lg:hidden"
          >
            <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onMobileClose} />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'spring', duration: 0.4 }}
              className="absolute left-0 top-0 bottom-0 w-64 bg-white dark:bg-slate-900 shadow-xl flex flex-col"
            >
              {sidebarContent}
            </motion.aside>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
