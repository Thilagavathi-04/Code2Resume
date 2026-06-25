import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export default function Header() {
  const { logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-100">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/dashboard" className="text-2xl font-bold bg-gradient-to-r from-teal-600 to-blue-600 bg-clip-text text-transparent">
            Code2Resume
          </Link>

          <nav className="flex items-center gap-6">
            <Link
              to="/dashboard"
              className="text-gray-700 hover:text-teal-600 transition-colors font-medium"
            >
              Dashboard
            </Link>

            <Link
              to="/resumes"
              className="text-gray-700 hover:text-teal-600 transition-colors font-medium"
            >
              Resumes
            </Link>

            <Link
              to="/settings"
              className="text-gray-700 hover:text-teal-600 transition-colors font-medium"
            >
              Settings
            </Link>

            <button
              onClick={handleLogout}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors font-medium"
            >
              Logout
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
}
