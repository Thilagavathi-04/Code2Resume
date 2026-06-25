# Code2Resume - React Frontend

Modern React-based frontend for Code2Resume application with AI-powered resume generation.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Backend server running on port 8001

### Installation

```bash
# Install dependencies
cd frontend-react
npm install
```

### Development

```bash
# Start dev server (with hot reload)
npm run dev

# Or use the unified startup script from project root
cd ..
./scripts/start-react.sh  # Linux/Mac
# or
scripts\start-react.bat   # Windows
```

The app will be available at http://localhost:5173

## 📦 Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router v6** - Client-side routing
- **Zustand** - State management
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## 🏗️ Project Structure

```
frontend-react/
├── public/              # Static assets
├── src/
│   ├── api/            # API integration layer
│   │   ├── axiosConfig.js   # Axios instance with interceptors
│   │   ├── auth.js          # Authentication endpoints
│   │   ├── github.js        # GitHub API endpoints
│   │   └── resume.js        # Resume generation endpoints
│   ├── components/     # Reusable components
│   │   ├── layout/
│   │   │   └── Layout.jsx   # Main layout with navigation
│   │   ├── dashboard/
│   │   │   ├── ChatBox.jsx  # AI chat interface
│   │   │   └── RepoList.jsx # Repository cards
│   │   └── ...
│   ├── pages/          # Page components
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Resumes.jsx
│   │   └── Settings.jsx
│   ├── store/          # Zustand stores
│   │   ├── authStore.js     # Authentication state
│   │   └── userStore.js     # User data state
│   ├── utils/          # Utility functions
│   │   ├── constants.js
│   │   └── helpers.js
│   ├── App.jsx         # Main app with routing
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── .env                # Environment variables
├── vite.config.js      # Vite configuration
├── tailwind.config.js  # Tailwind configuration
└── package.json
```

## 🔐 Authentication Flow

1. User registers/logs in via Login.jsx or Register.jsx
2. Token stored in Zustand store with localStorage persistence
3. Axios interceptor automatically adds token to all requests
4. Protected routes redirect to login if unauthenticated
5. 401 responses trigger automatic logout

## 🛣️ Routes

- `/` - Dashboard (protected)
- `/login` - Login page
- `/register` - Registration page
- `/resumes` - Resume library (protected)
- `/settings` - User settings (protected)

## 🎨 Components

### Layout Components
- **Layout** - Main app shell with navigation and logout

### Dashboard Components
- **ChatBox** - AI chat interface for resume generation
- **RepoList** - Display GitHub repositories with tech stack

### Features
- Form validation with error handling
- Loading states for async operations
- Responsive design with Tailwind CSS
- Toast notifications (lucide-react icons)

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8001
```

### API Base URL

Configured in src/api/axiosConfig.js:
- Defaults to `http://localhost:8001`
- Uses `VITE_API_URL` if set

## 📝 Available Scripts

```bash
# Development server with hot reload
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🚢 Production Build

```bash
# Build for production
npm run build

# Files will be in dist/ directory
# Serve with any static file server
```

## 🔗 API Integration

All API calls use Axios with:
- Automatic token injection
- Request/response interceptors
- Error handling
- Form-encoded login requests

See src/api/ for endpoint definitions.

## 🎯 State Management

Using Zustand for:
- Authentication state (token, user)
- User profile data
- GitHub repositories
- Global loading states

Stores persist to localStorage automatically.

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in package.json dev script:
"dev": "vite --port 3000"
```

### CORS Errors
- Ensure backend CORS allows `http://localhost:5173`
- Check `backend/app.py` CORS configuration

### Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📚 Learn More

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [React Router](https://reactrouter.com)
- [Zustand](https://github.com/pmndrs/zustand)
