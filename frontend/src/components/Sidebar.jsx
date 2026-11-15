import { Link, useNavigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const Sidebar = () => {
  const { user, setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    navigate('/');
  };

  return (
    <div className="w-64 bg-slate-900 text-white min-h-screen p-4 flex flex-col justify-between">
      <div>
        <div className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center font-bold">S</div>
          <div>
            <h1 className="font-bold text-lg">School Portal</h1>
            <p className="text-xs text-gray-400">Management system</p>
          </div>
        </div>

        <nav className="space-y-2">
          {user?.role === 'admin' ? (
            <>
              <Link to="/admin" className="block p-2 bg-blue-600 rounded">Dashboard</Link>
              <Link to="/admin/add-student" className="block p-2 hover:bg-slate-800 rounded">Add Student</Link>
            </>
          ) : (
            <Link to="/student" className="block p-2 bg-blue-600 rounded">My Dashboard</Link>
          )}
        </nav>
      </div>

      <div className="border-t border-slate-700 pt-4">
        <p className="text-sm font-bold">{user?.email || user?.username}</p>
        <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
        <button onClick={handleLogout} className="mt-2 text-sm text-red-400 hover:text-red-300">Log out</button>
      </div>
    </div>
  );
};

export default Sidebar;