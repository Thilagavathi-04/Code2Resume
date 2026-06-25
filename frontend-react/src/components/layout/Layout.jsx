import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { getCurrentUser } from '../../api/auth';
import {
  LayoutDashboard, FileText, Settings, LogOut, Menu, X,
  Github, ChevronDown, Sparkles, Bot
} from 'lucide-react';

export default function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const logout = useAuthStore(state => state.logout);
  const setUser = useAuthStore(state => state.setUser);
  const user = useAuthStore(state => state.user);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const fetchUser = useCallback(async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user:', error);
    }
  }, [setUser]);

  useEffect(() => { fetchUser(); }, [fetchUser]);

  const handleLogout = () => { logout(); navigate('/'); };

  const navLinks = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/resumes', label: 'Resumes', icon: FileText },
    { path: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="layout-container">
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <div className="sidebar-header">
          <Link to="/dashboard" className="sidebar-logo">
            <div className="sidebar-logo-icon"><Sparkles size={20} /></div>
            {sidebarOpen && <span className="sidebar-logo-text">Code2Resume</span>}
          </Link>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="icon-btn">
            <Menu size={18} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {navLinks.map(({ path, label, icon: NavIcon }) => (
            <Link
              key={path} to={path}
              className={`sidebar-nav-link ${location.pathname === path ? 'active' : ''}`}
            >
              <NavIcon size={20} />
              {sidebarOpen && <span className="font-medium">{label}</span>}
            </Link>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div
            className={`sidebar-user ${!sidebarOpen ? 'collapsed' : ''}`}
            onClick={() => setUserMenuOpen(!userMenuOpen)}
          >
            <div className="avatar">{user?.username?.charAt(0).toUpperCase() || 'U'}</div>
            {sidebarOpen && (
              <>
                <div className="sidebar-user-info">
                  <p className="text-sm font-medium text-gray-900">{user?.username || 'User'}</p>
                  <p className="text-xs text-gray-500">{user?.github_url?.split('/').pop() || 'GitHub'}</p>
                </div>
                <ChevronDown size={16} className={`text-gray-400 transition-transform duration-200 ${userMenuOpen ? 'rotate-180' : ''}`} />
              </>
            )}
          </div>

          {userMenuOpen && sidebarOpen && (
            <div className="sidebar-dropdown">
              <Link to="/settings" onClick={() => setUserMenuOpen(false)}>
                <Settings size={16} /> Settings
              </Link>
              <button onClick={handleLogout}>
                <LogOut size={16} /> Logout
              </button>
            </div>
          )}
        </div>
      </aside>

      {mobileMenuOpen && (
        <div className="mobile-overlay">
          <div className="mobile-overlay-bg" onClick={() => setMobileMenuOpen(false)} />
          <aside className="mobile-sidebar animate-slide-in-left">
            <div className="sidebar-header">
              <Link to="/dashboard" className="sidebar-logo">
                <div className="sidebar-logo-icon"><Sparkles size={20} /></div>
                <span className="sidebar-logo-text">Code2Resume</span>
              </Link>
              <button onClick={() => setMobileMenuOpen(false)} className="icon-btn">
                <X size={20} />
              </button>
            </div>

            <nav className="sidebar-nav">
              {navLinks.map(({ path, label, icon: NavIcon }) => (
                <Link key={path} to={path} onClick={() => setMobileMenuOpen(false)}
                  className={`sidebar-nav-link ${location.pathname === path ? 'active' : ''}`}>
                  <NavIcon size={20} />
                  <span className="font-medium">{label}</span>
                </Link>
              ))}
            </nav>

            <div className="sidebar-footer" style={{ position: 'absolute', bottom: 0, left: 0, right: 0 }}>
              <div className="sidebar-user">
                <div className="avatar">{user?.username?.charAt(0).toUpperCase() || 'U'}</div>
                <div className="sidebar-user-info">
                  <p className="text-sm font-medium text-gray-900">{user?.username || 'User'}</p>
                </div>
              </div>
              <button onClick={handleLogout} style={{ width: '100%', marginTop: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', padding: '0.5rem 1rem', fontSize: '0.875rem', color: 'var(--red-600)', borderRadius: '0.5rem', transition: 'background-color 0.15s ease' }}
                onMouseEnter={e => e.currentTarget.style.backgroundColor = 'var(--red-50)'}
                onMouseLeave={e => e.currentTarget.style.backgroundColor = 'transparent'}>
                <LogOut size={16} /> Logout
              </button>
            </div>
          </aside>
        </div>
      )}

      <div className="flex-1 flex flex-col" style={{ minWidth: 0 }}>
        <header className="top-header">
          <div className="top-header-left">
            <button onClick={() => setMobileMenuOpen(true)} className="lg:hidden icon-btn">
              <Menu size={20} />
            </button>
            <div className="lg:block hidden">
              <h1 className="text-lg font-semibold text-gray-900">
                {navLinks.find(l => l.path === location.pathname)?.label || 'Dashboard'}
              </h1>
            </div>
          </div>
          <div className="top-header-right">
            <a href="https://github.com/Mithrajith/Code2Resume" target="_blank" rel="noopener noreferrer" className="icon-btn">
              <Github size={20} />
            </a>
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-green-50 text-green-700 rounded-full text-sm">
              <Bot size={16} />
              <span>AI Ready</span>
            </div>
          </div>
        </header>

        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
}
