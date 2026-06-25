# React.js Migration Guide for Code2Resume

## 📋 Overview

This guide outlines the steps to migrate the frontend from vanilla HTML/JS to React.js while keeping the FastAPI backend unchanged.

## 🎯 Migration Strategy

**Backend**: Keep as-is (FastAPI serves only API endpoints)  
**Frontend**: Replace with React SPA (Single Page Application)  
**Communication**: REST API (existing endpoints)

---

## 📝 Step-by-Step Migration Plan

### Phase 1: Setup React Project Structure

#### 1.1 Create React App with Vite

```bash
cd /home/zypher/PROJECT/Code2Resume

# Create React app in a temporary directory
npm create vite@latest frontend-react -- --template react

# Or use TypeScript (recommended)
npm create vite@latest frontend-react -- --template react-ts
```

#### 1.2 Install Dependencies

```bash
cd frontend-react
npm install

# Install additional dependencies
npm install \
  react-router-dom \
  axios \
  @tanstack/react-query \
  zustand \
  react-hook-form \
  lucide-react \
  tailwindcss \
  autoprefixer \
  postcss
```

#### 1.3 Setup Tailwind CSS (Optional but Recommended)

```bash
npx tailwindcss init -p
```

**tailwind.config.js:**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**src/index.css:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

### Phase 2: Project Structure

#### 2.1 Recommended React Structure

```
frontend-react/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/
│   │   ├── axiosConfig.js
│   │   ├── auth.js
│   │   ├── github.js
│   │   └── resume.js
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── Card.jsx
│   │   │   └── Spinner.jsx
│   │   ├── layout/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── Layout.jsx
│   │   ├── auth/
│   │   │   ├── LoginForm.jsx
│   │   │   └── RegisterForm.jsx
│   │   ├── dashboard/
│   │   │   ├── StatsCard.jsx
│   │   │   ├── RepoList.jsx
│   │   │   └── ChatBox.jsx
│   │   └── resume/
│   │       ├── ResumeList.jsx
│   │       ├── ResumePreview.jsx
│   │       └── GenerateForm.jsx
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Settings.jsx
│   │   └── Resumes.jsx
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useGithub.js
│   │   └── useChat.js
│   ├── store/
│   │   ├── authStore.js
│   │   └── userStore.js
│   ├── utils/
│   │   ├── constants.js
│   │   └── helpers.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
├── vite.config.js
└── .env
```

---

### Phase 3: Convert Existing Pages to React Components

#### 3.1 Authentication Pages

**src/pages/Login.jsx:**
```jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser } from '../api/auth';
import { useAuthStore } from '../store/authStore';

export default function Login() {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore(state => state.setAuth);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await loginUser(formData);
      setAuth(response.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h2 className="text-2xl font-bold mb-6">Login to Code2Resume</h2>
        {error && <div className="bg-red-100 text-red-700 p-3 rounded mb-4">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
            className="w-full p-2 border rounded mb-4"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            className="w-full p-2 border rounded mb-4"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <p className="mt-4 text-center">
          Don't have an account? <a href="/register" className="text-blue-600">Register</a>
        </p>
      </div>
    </div>
  );
}
```

**src/pages/Dashboard.jsx:**
```jsx
import { useState, useEffect } from 'react';
import { fetchUserRepos, analyzeGithub } from '../api/github';
import ChatBox from '../components/dashboard/ChatBox';
import RepoList from '../components/dashboard/RepoList';

export default function Dashboard() {
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  const handleUpdateGithub = async () => {
    setAnalyzing(true);
    try {
      await analyzeGithub();
      // Refresh repos after analysis
      const data = await fetchUserRepos();
      setRepos(data);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <button
          onClick={handleUpdateGithub}
          disabled={analyzing}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          {analyzing ? 'Analyzing...' : 'Update from GitHub'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChatBox />
        <RepoList repos={repos} />
      </div>
    </div>
  );
}
```

#### 3.2 API Layer

**src/api/axiosConfig.js:**
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default api;
```

**src/api/auth.js:**
```javascript
import api from './axiosConfig';

export const loginUser = async (credentials) => {
  const formData = new URLSearchParams();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);
  
  const response = await api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  
  return response.data;
};

export const registerUser = async (userData) => {
  const response = await api.post('/auth/register', userData);
  return response.data;
};
```

**src/api/github.js:**
```javascript
import api from './axiosConfig';

export const analyzeGithub = async () => {
  const response = await api.post('/update-github');
  return response.data;
};

export const fetchUserRepos = async () => {
  const response = await api.get('/repos');
  return response.data;
};
```

#### 3.3 State Management (Zustand)

**src/store/authStore.js:**
```javascript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
  persist(
    (set) => ({
      token: null,
      user: null,
      setAuth: (token) => set({ token }),
      setUser: (user) => set({ user }),
      logout: () => {
        localStorage.removeItem('token');
        set({ token: null, user: null });
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

#### 3.4 Routing

**src/App.jsx:**
```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import Resumes from './pages/Resumes';
import Layout from './components/layout/Layout';

function PrivateRoute({ children }) {
  const token = useAuthStore(state => state.token);
  return token ? children : <Navigate to="/" />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        <Route path="/dashboard" element={
          <PrivateRoute>
            <Layout><Dashboard /></Layout>
          </PrivateRoute>
        } />
        
        <Route path="/settings" element={
          <PrivateRoute>
            <Layout><Settings /></Layout>
          </PrivateRoute>
        } />
        
        <Route path="/resumes" element={
          <PrivateRoute>
            <Layout><Resumes /></Layout>
          </PrivateRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}
```

---

### Phase 4: Backend Modifications

#### 4.1 Update CORS Settings

**backend/app.py:**
```python
# Update CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite/React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4.2 Remove Static File Serving

**Remove from backend/app.py:**
```python
# Remove these lines (React will serve its own static files)
# from fastapi.staticfiles import StaticFiles
# app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Remove HTML template routes
# @app.get("/", response_class=HTMLResponse)
# @app.get("/register", response_class=HTMLResponse)
# etc.
```

#### 4.3 Keep Only API Endpoints

Backend should only serve JSON API responses, no HTML.

---

### Phase 5: Development Workflow

#### 5.1 Environment Files

**frontend-react/.env:**
```env
VITE_API_URL=http://localhost:8001
```

**Usage in React:**
```javascript
const API_URL = import.meta.env.VITE_API_URL;
```

#### 5.2 Development Scripts

**frontend-react/package.json:**
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0"
  }
}
```

#### 5.3 Proxy Configuration (Alternative to CORS)

**frontend-react/vite.config.js:**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

---

### Phase 6: Testing & Migration

#### 6.1 Incremental Migration

1. **Start with Authentication**: Login/Register pages
2. **Add Dashboard**: Main view with repos
3. **Implement Chat**: Real-time chat component
4. **Add Settings**: User profile management
5. **Build Resumes**: Resume generation and listing

#### 6.2 Running Both Versions

During migration, run both versions:
```bash
# Terminal 1: Backend
./scripts/start.sh

# Terminal 2: Old Frontend (for reference)
# Accessible at http://localhost:8001

# Terminal 3: React Frontend
cd frontend-react
npm run dev
# Accessible at http://localhost:5173
```

---

### Phase 7: Production Build

#### 7.1 Build React App

```bash
cd frontend-react
npm run build
# Output: dist/ folder
```

#### 7.2 Serve React Build from FastAPI

**Option 1: Serve from FastAPI**
```python
from fastapi.staticfiles import StaticFiles

# Serve React build
app.mount("/", StaticFiles(directory="frontend-react/dist", html=True), name="react-app")
```

**Option 2: Separate Servers (Recommended)**
- Backend API: `http://localhost:8001`
- Frontend: Nginx/Vercel/Netlify serving React build

---

### Phase 8: Updated Project Structure

#### Final Structure:
```
Code2Resume/
├── backend/              # FastAPI (API only, no HTML)
├── frontend-react/       # React SPA
│   ├── src/
│   ├── public/
│   ├── dist/            # Production build
│   └── package.json
├── frontend/            # OLD (keep for reference, then delete)
├── scripts/
├── fine-tuning/
├── data/
├── docs/
└── tests/
```

---

## 🎯 Migration Checklist

### Phase 1: Setup
- [ ] Create React app with Vite
- [ ] Install dependencies (React Router, Axios, Zustand)
- [ ] Setup Tailwind CSS
- [ ] Configure environment variables

### Phase 2: Components
- [ ] Create Login component
- [ ] Create Register component
- [ ] Create Dashboard component
- [ ] Create Chat component
- [ ] Create Resume list component
- [ ] Create Settings component

### Phase 3: API Integration
- [ ] Setup Axios configuration
- [ ] Create auth API functions
- [ ] Create GitHub API functions
- [ ] Create resume API functions
- [ ] Implement error handling

### Phase 4: State Management
- [ ] Setup Zustand stores
- [ ] Implement auth state
- [ ] Implement user state
- [ ] Add persistence

### Phase 5: Backend Updates
- [ ] Update CORS settings
- [ ] Remove HTML routes
- [ ] Test API endpoints
- [ ] Update documentation

### Phase 6: Testing
- [ ] Test authentication flow
- [ ] Test GitHub analysis
- [ ] Test chat functionality
- [ ] Test resume generation
- [ ] Test file downloads

### Phase 7: Production
- [ ] Build React app
- [ ] Configure deployment
- [ ] Update scripts
- [ ] Update documentation

---

## 🚀 Quick Start Commands

```bash
# 1. Create React app
npm create vite@latest frontend-react -- --template react-ts

# 2. Install dependencies
cd frontend-react
npm install react-router-dom axios zustand @tanstack/react-query

# 3. Start development
npm run dev

# 4. In another terminal, start backend
cd ..
./scripts/start.sh
```

---

## 📚 Key Libraries

| Library | Purpose | Documentation |
|---------|---------|---------------|
| **React Router** | Client-side routing | [Docs](https://reactrouter.com/) |
| **Axios** | HTTP requests | [Docs](https://axios-http.com/) |
| **Zustand** | State management | [Docs](https://zustand-demo.pmnd.rs/) |
| **React Query** | Server state management | [Docs](https://tanstack.com/query/) |
| **Tailwind CSS** | Styling | [Docs](https://tailwindcss.com/) |
| **Vite** | Build tool | [Docs](https://vitejs.dev/) |

---

## ⚠️ Important Notes

1. **CORS**: Configure properly for development and production
2. **Authentication**: Store JWT securely (httpOnly cookies in production)
3. **Environment Variables**: Never commit `.env` files
4. **API Base URL**: Use environment variables, not hardcoded
5. **Error Handling**: Implement global error boundaries
6. **Loading States**: Show spinners during async operations
7. **Security**: Sanitize all user inputs

---

## 🎨 UI Component Libraries (Optional)

Consider using a component library to speed up development:

- **shadcn/ui**: Modern, accessible components (Recommended)
- **Material-UI (MUI)**: Google Material Design
- **Ant Design**: Comprehensive component set
- **Chakra UI**: Simple, modular components

---

## 📖 Additional Resources

- [React Documentation](https://react.dev/)
- [FastAPI + React Tutorial](https://fastapi.tiangolo.com/advanced/custom-response/)
- [Vite + React Guide](https://vitejs.dev/guide/)
- [React Authentication Best Practices](https://react.dev/learn)

---

## 🔄 Migration Timeline Estimate

| Phase | Tasks | Time Estimate |
|-------|-------|---------------|
| **Setup** | Project creation, dependencies | 2-4 hours |
| **Auth Pages** | Login, Register | 4-6 hours |
| **Dashboard** | Main view, repos, chat | 8-12 hours |
| **Settings** | User profile | 2-4 hours |
| **Resumes** | List, generate, download | 6-8 hours |
| **Testing** | Full app testing | 4-6 hours |
| **Polish** | UI/UX improvements | 4-8 hours |
| **Total** | | **30-48 hours** |

---

## ✅ Success Criteria

- [ ] All pages converted to React components
- [ ] Authentication working (login, register, logout)
- [ ] GitHub analysis functional
- [ ] Chat interface interactive
- [ ] Resume generation working
- [ ] File downloads operational
- [ ] Responsive design maintained
- [ ] No console errors
- [ ] Production build successful

---

**Good luck with your React migration! 🚀**
