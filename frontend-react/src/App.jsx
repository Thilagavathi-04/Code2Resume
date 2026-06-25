import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import AppLayout from './components/layout/AppLayout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import Resumes from './pages/Resumes';
import ATSAnalyzer from './pages/ATSAnalyzer';
import JobMatcher from './pages/JobMatcher';
import SkillGapAnalysis from './pages/SkillGapAnalysis';
import GitHubAnalysis from './pages/GitHubAnalysis';
import ResumeBuilder from './pages/ResumeBuilder';
import ResumeTemplates from './pages/ResumeTemplates';
import InterviewPrep from './pages/InterviewPrep';
import Analytics from './pages/Analytics';
import JobDescriptions from './pages/JobDescriptions';

function PrivateRoute({ children }) {
  const token = useAuthStore(state => state.token);
  return token ? children : <Navigate to="/" />;
}

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <Routes location={location}>
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route path="/dashboard" element={
        <PrivateRoute>
          <AppLayout><Dashboard /></AppLayout>
        </PrivateRoute>
      } />

      <Route path="/analysis" element={
        <PrivateRoute>
          <AppLayout><GitHubAnalysis /></AppLayout>
        </PrivateRoute>
      } />

      <Route path="/builder" element={
        <PrivateRoute>
          <AppLayout><ResumeBuilder /></AppLayout>
        </PrivateRoute>
      } />

      <Route path="/templates" element={
        <PrivateRoute>
          <AppLayout><ResumeTemplates /></AppLayout>
        </PrivateRoute>
      } />

      <Route path="/ats" element={
        <PrivateRoute>
          <AppLayout><ATSAnalyzer /></AppLayout>
        </PrivateRoute>
      } />

      <Route path="/jobs" element={
        <PrivateRoute>
          <AppLayout><JobMatcher /></AppLayout>
        </PrivateRoute>
      } />

      <Route path="/job-descriptions" element={
        <PrivateRoute>
          <AppLayout><JobDescriptions /></AppLayout>
        </PrivateRoute>
      } />

      <Route path="/skills" element={
        <PrivateRoute>
          <AppLayout><SkillGapAnalysis /></AppLayout>
        </PrivateRoute>
      } />

      <Route path="/interview" element={
        <PrivateRoute>
          <AppLayout><InterviewPrep /></AppLayout>
        </PrivateRoute>
      } />

      <Route path="/analytics" element={
        <PrivateRoute>
          <AppLayout><Analytics /></AppLayout>
        </PrivateRoute>
      } />

      <Route path="/resumes" element={
        <PrivateRoute>
          <AppLayout><Resumes /></AppLayout>
        </PrivateRoute>
      } />

      <Route path="/settings" element={
        <PrivateRoute>
          <AppLayout><Settings /></AppLayout>
        </PrivateRoute>
      } />

      <Route path="*" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AnimatedRoutes />
    </BrowserRouter>
  );
}

export default App;
