import { useState } from 'react';
import { motion } from 'framer-motion';
import Sidebar from './Sidebar';
import TopNav from './TopNav';
import ToastContainer from '../ui/Toast';

const pageTransition = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
  transition: { duration: 0.2 },
};

export default function AppLayout({ children }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-slate-950">
      <Sidebar
        collapsed={collapsed}
        onToggle={() => setCollapsed(!collapsed)}
        mobileOpen={mobileOpen}
        onMobileClose={() => setMobileOpen(false)}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <TopNav onMenuClick={() => setMobileOpen(true)} />

        <main className="flex-1 p-4 lg:p-6 overflow-auto">
          <motion.div
            key={typeof window !== 'undefined' ? window.location.pathname : ''}
            {...pageTransition}
          >
            {children}
          </motion.div>
        </main>
      </div>

      <ToastContainer />
    </div>
  );
}
