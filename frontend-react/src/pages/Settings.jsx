import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User,
  Github,
  Brain,
  Bell,
  Shield,
  Palette,
  Save,
  Camera,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Eye,
  EyeOff,
  Monitor,
  Moon,
  Sun,
  LogOut,
  Trash2,
  Link,
  Unlink,
  RefreshCw,
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useThemeStore } from '../store/themeStore';
import { getCurrentUser, updateUser } from '../api/auth';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import { useToastStore } from '../components/ui/Toast';

const TABS = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'github', label: 'GitHub Integration', icon: Github },
  { id: 'ai', label: 'AI Preferences', icon: Brain },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'theme', label: 'Theme', icon: Palette },
];

function Toggle({ enabled, onChange, label }) {
  return (
    <div className="flex items-center justify-between py-3">
      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</span>
      <button
        type="button"
        onClick={() => onChange(!enabled)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          enabled ? 'bg-indigo-600' : 'bg-gray-200 dark:bg-gray-700'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            enabled ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );
}

function InputField({ label, icon: Icon, name, type = 'text', placeholder, value, onChange, disabled, masked }) {
  const [showPassword, setShowPassword] = useState(false);
  const inputType = masked ? (showPassword ? 'text' : 'password') : type;

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
        <div className="flex items-center gap-2">
          {Icon && <Icon size={14} />}
          {label}
        </div>
      </label>
      <div className="relative">
        <input
          type={inputType}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          className={`w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-white text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all ${
            disabled ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        />
        {masked && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        )}
      </div>
    </div>
  );
}

export default function Settings() {
  const setUser = useAuthStore((state) => state.setUser);
  const { isDark, toggle: toggleTheme } = useThemeStore();
  const { addToast } = useToastStore();

  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const [profile, setProfile] = useState({
    username: '',
    email: '',
    phone: '',
    bio: '',
  });

  const [github, setGithub] = useState({
    url: '',
    token: '',
    connected: false,
    syncRepos: true,
    syncSkills: true,
    autoSync: false,
  });

  const [aiPrefs, setAiPrefs] = useState({
    model: '',
    temperature: 50,
    maxTokens: 0,
    responseStyle: '',
  });

  const [notifications, setNotifications] = useState({
    email: false,
    resumeUpdates: false,
    jobAlerts: false,
    interviewReminders: false,
    weeklyDigest: false,
  });

  const [security, setSecurity] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
    twoFactor: false,
    sessions: [],
  });

  const [accentColor, setAccentColor] = useState('#4F46E5');
  const [compactMode, setCompactMode] = useState(false);

  const fetchUserData = useCallback(async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
      setProfile({
        username: userData.username || '',
        email: userData.gmail || '',
        phone: userData.mobile_number || '',
        bio: '',
      });
      setGithub((prev) => ({
        ...prev,
        url: userData.github_url || '',
        connected: !!userData.github_url,
      }));
    } catch {
      setMessage({ type: 'error', text: 'Failed to load user data' });
    } finally {
      setLoading(false);
    }
  }, [setUser]);

  useEffect(() => {
    fetchUserData();
  }, [fetchUserData]);

  const handleSave = async (tab) => {
    setSaving(true);
    setMessage({ type: '', text: '' });
    try {
      if (tab === 'profile') {
        const updateData = { gmail: profile.email, mobile_number: profile.phone };
        const updatedUser = await updateUser(updateData);
        setUser(updatedUser);
      } else if (tab === 'github') {
        const updateData = {
          github_url: github.url || null,
          github_token: github.token || null,
        };
        const updatedUser = await updateUser(updateData);
        setUser(updatedUser);
        setGithub(prev => ({ ...prev, token: '', connected: !!github.url }));
      }
      addToast({ type: 'success', message: 'Settings saved successfully!' });
      setMessage({ type: 'success', text: 'Settings updated successfully!' });
    } catch (error) {
      const errMsg = error.response?.data?.detail || 'Failed to update settings';
      addToast({ type: 'error', message: errMsg });
      setMessage({ type: 'error', text: errMsg });
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = async () => {
    if (security.newPassword !== security.confirmPassword) {
      addToast({ type: 'error', message: 'Passwords do not match.' });
      return;
    }
    setSaving(true);
    try {
      await updateUser({ password: security.newPassword, current_password: security.currentPassword });
      addToast({ type: 'success', message: 'Password changed successfully!' });
      setSecurity((prev) => ({ ...prev, currentPassword: '', newPassword: '', confirmPassword: '' }));
    } catch (error) {
      addToast({ type: 'error', message: error.response?.data?.detail || 'Failed to change password' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
      </div>
    );
  }

  const accentOptions = [
    { color: '#4F46E5', name: 'Indigo' },
    { color: '#7C3AED', name: 'Purple' },
    { color: '#2563EB', name: 'Blue' },
    { color: '#059669', name: 'Green' },
    { color: '#D97706', name: 'Amber' },
    { color: '#DC2626', name: 'Red' },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="w-20 h-20 rounded-2xl bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                  {profile.username?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <button className="absolute -bottom-1 -right-1 w-7 h-7 bg-indigo-600 rounded-full flex items-center justify-center text-white shadow-md hover:bg-indigo-700 transition-colors">
                  <Camera className="w-3.5 h-3.5" />
                </button>
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-900 dark:text-white">{profile.username}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Profile Picture</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <InputField
                label="Username"
                icon={User}
                value={profile.username}
                disabled
              />
              <InputField
                label="Email"
                icon={User}
                name="email"
                type="email"
                placeholder="you@example.com"
                value={profile.email}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
              />
              <InputField
                label="Phone Number"
                icon={User}
                name="phone"
                type="tel"
                placeholder="+1234567890"
                value={profile.phone}
                onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Bio
              </label>
              <textarea
                rows={3}
                placeholder="Tell us about yourself..."
                value={profile.bio}
                onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-white text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"
              />
            </div>

            <div className="flex justify-end">
              <Button onClick={() => handleSave('profile')} loading={saving}>
                <Save className="w-4 h-4" />
                Save Changes
              </Button>
            </div>
          </div>
        );

      case 'github':
        return (
          <div className="space-y-6">
            <div className="flex items-center gap-3 p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                github.connected
                  ? 'bg-green-100 dark:bg-green-900/30'
                  : 'bg-gray-200 dark:bg-gray-700'
              }`}>
                {github.connected ? (
                  <Link className="w-5 h-5 text-green-600 dark:text-green-400" />
                ) : (
                  <Unlink className="w-5 h-5 text-gray-400" />
                )}
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-gray-900 dark:text-white">
                  {github.connected ? 'Connected' : 'Not Connected'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {github.connected ? 'Your GitHub account is linked' : 'Link your GitHub to enable analysis'}
                </p>
              </div>
              {github.connected && (
                <Button variant="danger" size="sm" onClick={() => setGithub({ ...github, connected: false })}>
                  Disconnect
                </Button>
              )}
            </div>

            <InputField
              label="GitHub URL"
              icon={Github}
              name="url"
              placeholder="https://github.com/username"
              value={github.url}
              onChange={(e) => setGithub({ ...github, url: e.target.value })}
            />

            <InputField
              label="GitHub Token"
              icon={Github}
              name="token"
              placeholder="Leave empty to keep current"
              value={github.token}
              onChange={(e) => setGithub({ ...github, token: e.target.value })}
              masked
            />
            <p className="text-xs text-gray-400 dark:text-gray-500 -mt-3">
              Generate at: GitHub Settings → Developer settings → Personal access tokens
            </p>

            <div className="pt-2 border-t border-gray-100 dark:border-gray-700">
              <p className="text-sm font-medium text-gray-900 dark:text-white mb-3">Sync Settings</p>
              <Toggle
                label="Sync repositories"
                enabled={github.syncRepos}
                onChange={(v) => setGithub({ ...github, syncRepos: v })}
              />
              <Toggle
                label="Sync skills automatically"
                enabled={github.syncSkills}
                onChange={(v) => setGithub({ ...github, syncSkills: v })}
              />
              <Toggle
                label="Auto-sync on push"
                enabled={github.autoSync}
                onChange={(v) => setGithub({ ...github, autoSync: v })}
              />
            </div>

            <div className="flex justify-end gap-3">
              <Button variant="secondary" onClick={() => fetchUserData()}>
                <RefreshCw className="w-4 h-4" />
                Refresh
              </Button>
              <Button onClick={() => handleSave('github')} loading={saving}>
                <Save className="w-4 h-4" />
                Save Changes
              </Button>
            </div>
          </div>
        );

      case 'ai':
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Default Model
              </label>
              <select
                value={aiPrefs.model}
                onChange={(e) => setAiPrefs({ ...aiPrefs, model: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value="">Select a model</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="claude-3-opus">Claude 3 Opus</option>
                <option value="claude-3-sonnet">Claude 3 Sonnet</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                Temperature: {aiPrefs.temperature}
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={aiPrefs.temperature}
                onChange={(e) => setAiPrefs({ ...aiPrefs, temperature: parseInt(e.target.value) })}
                className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full appearance-none cursor-pointer accent-indigo-600"
              />
              <div className="flex justify-between text-xs text-gray-400 dark:text-gray-500 mt-1">
                <span>Precise</span>
                <span>Creative</span>
              </div>
            </div>

            <InputField
              label="Max Tokens"
              name="maxTokens"
              type="number"
              placeholder="2048"
              value={aiPrefs.maxTokens || ''}
              onChange={(e) => setAiPrefs({ ...aiPrefs, maxTokens: parseInt(e.target.value) || 0 })}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Response Style
              </label>
              <div className="grid grid-cols-3 gap-2">
                {['professional', 'casual', 'technical'].map((style) => (
                  <button
                    key={style}
                    onClick={() => setAiPrefs({ ...aiPrefs, responseStyle: style })}
                    className={`px-4 py-2.5 rounded-xl text-sm font-medium capitalize transition-all ${
                      aiPrefs.responseStyle === style
                        ? 'bg-indigo-600 text-white shadow-md'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                    }`}
                  >
                    {style}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex justify-end">
              <Button onClick={() => handleSave('ai')} loading={saving}>
                <Save className="w-4 h-4" />
                Save Changes
              </Button>
            </div>
          </div>
        );

      case 'notifications':
        return (
          <div className="space-y-2">
            <Toggle
              label="Email notifications"
              enabled={notifications.email}
              onChange={(v) => setNotifications({ ...notifications, email: v })}
            />
            <Toggle
              label="Resume updates"
              enabled={notifications.resumeUpdates}
              onChange={(v) => setNotifications({ ...notifications, resumeUpdates: v })}
            />
            <Toggle
              label="Job match alerts"
              enabled={notifications.jobAlerts}
              onChange={(v) => setNotifications({ ...notifications, jobAlerts: v })}
            />
            <Toggle
              label="Interview reminders"
              enabled={notifications.interviewReminders}
              onChange={(v) => setNotifications({ ...notifications, interviewReminders: v })}
            />
            <Toggle
              label="Weekly digest"
              enabled={notifications.weeklyDigest}
              onChange={(v) => setNotifications({ ...notifications, weeklyDigest: v })}
            />
            <div className="flex justify-end pt-4">
              <Button onClick={() => handleSave('notifications')} loading={saving}>
                <Save className="w-4 h-4" />
                Save Changes
              </Button>
            </div>
          </div>
        );

      case 'security':
        return (
          <div className="space-y-8">
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">Change Password</h3>
              <div className="space-y-3">
                <InputField
                  label="Current Password"
                  name="currentPassword"
                  value={security.currentPassword}
                  onChange={(e) => setSecurity({ ...security, currentPassword: e.target.value })}
                  masked
                />
                <InputField
                  label="New Password"
                  name="newPassword"
                  value={security.newPassword}
                  onChange={(e) => setSecurity({ ...security, newPassword: e.target.value })}
                  masked
                />
                <InputField
                  label="Confirm New Password"
                  name="confirmPassword"
                  value={security.confirmPassword}
                  onChange={(e) => setSecurity({ ...security, confirmPassword: e.target.value })}
                  masked
                />
              </div>
              <div className="mt-3">
                <Button onClick={handlePasswordChange} loading={saving} size="sm">
                  Update Password
                </Button>
              </div>
            </div>

            <div className="pt-4 border-t border-gray-100 dark:border-gray-700">
              <Toggle
                label="Two-factor authentication"
                enabled={security.twoFactor}
                onChange={(v) => setSecurity({ ...security, twoFactor: v })}
              />
            </div>

            <div className="pt-4 border-t border-gray-100 dark:border-gray-700">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Active Sessions</h3>
              {security.sessions.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">No active sessions.</p>
              ) : (
                <div className="space-y-2">
                  {security.sessions.map((session) => (
                    <div
                      key={session.id}
                      className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50"
                    >
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">{session.device}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{session.lastActive}</p>
                      </div>
                      {session.current ? (
                        <span className="text-xs font-medium text-green-600 dark:text-green-400">Current</span>
                      ) : (
                        <Button variant="ghost" size="sm">
                          <LogOut className="w-3.5 h-3.5" />
                          Revoke
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-red-100 dark:border-red-900/30">
              <h3 className="text-sm font-semibold text-red-600 dark:text-red-400 mb-1">Danger Zone</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                Once you delete your account, there is no going back.
              </p>
              <Button variant="danger" size="sm">
                <Trash2 className="w-4 h-4" />
                Delete Account
              </Button>
            </div>
          </div>
        );

      case 'theme':
        return (
          <div className="space-y-6">
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Appearance</p>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { mode: 'light', icon: Sun, label: 'Light' },
                  { mode: 'system', icon: Monitor, label: 'System' },
                  { mode: 'dark', icon: Moon, label: 'Dark' },
                ].map(({ mode, icon: Icon, label }) => (
                  <button
                    key={mode}
                    onClick={() => {
                      if (mode === 'dark' && !isDark) toggleTheme();
                      else if (mode === 'light' && isDark) toggleTheme();
                    }}
                    className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all ${
                      (mode === 'dark' && isDark) || (mode === 'light' && !isDark)
                        ? 'border-indigo-600 bg-indigo-50 dark:bg-indigo-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <Icon className={`w-5 h-5 ${
                      (mode === 'dark' && isDark) || (mode === 'light' && !isDark)
                        ? 'text-indigo-600'
                        : 'text-gray-400'
                    }`} />
                    <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Accent Color</p>
              <div className="flex gap-3">
                {accentOptions.map((opt) => (
                  <button
                    key={opt.color}
                    onClick={() => setAccentColor(opt.color)}
                    className={`w-10 h-10 rounded-full transition-all ${
                      accentColor === opt.color ? 'ring-2 ring-offset-2 ring-indigo-600 dark:ring-offset-slate-800' : ''
                    }`}
                    style={{ backgroundColor: opt.color }}
                    title={opt.name}
                  />
                ))}
              </div>
            </div>

            <div className="pt-2 border-t border-gray-100 dark:border-gray-700">
              <Toggle
                label="Compact mode"
                enabled={compactMode}
                onChange={setCompactMode}
              />
            </div>

            <div className="flex justify-end">
              <Button onClick={() => handleSave('theme')} loading={saving}>
                <Save className="w-4 h-4" />
                Save Changes
              </Button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Manage your account and preferences
        </p>
      </div>

      {message.text && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`flex items-center gap-2 p-4 rounded-xl ${
            message.type === 'success'
              ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-800'
              : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800'
          }`}
        >
          {message.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
          <p className="text-sm">{message.text}</p>
        </motion.div>
      )}

      <div className="flex gap-6">
        <div className="hidden md:block w-56 flex-shrink-0">
          <nav className="space-y-1">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    activeTab === tab.id
                      ? 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="md:hidden flex overflow-x-auto gap-1 pb-1 -mx-1 px-1">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
                  activeTab === tab.id
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>

        <div className="flex-1 min-w-0">
          <Card>
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.15 }}
              >
                {renderTabContent()}
              </motion.div>
            </AnimatePresence>
          </Card>
        </div>
      </div>
    </div>
  );
}
