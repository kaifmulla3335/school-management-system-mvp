import { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginApi } from '../api/auth';
import { AuthContext } from '../context/AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { setUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const data = await loginApi(email, password);
      localStorage.setItem('token', data.access_token);
      // Login ke baad user details fetch karein
      const userRes = await fetch('http://localhost:8000/auth/me', {
        headers: { Authorization: `Bearer ${data.access_token}` }
      });
      const userData = await userRes.json();
      setUser(userData);
      
      if (userData.role === 'admin') navigate('/admin');
      else navigate('/student');
    } catch (err) {
      setError('Invalid credentials. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h2 className="text-2xl font-bold mb-2">Welcome back</h2>
        <p className="text-gray-500 text-sm mb-6">Sign in with your school login ID.</p>
        
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Login ID / Email</label>
            <input type="text" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full border p-2 rounded" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full border p-2 rounded" />
          </div>
          <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700">Sign in</button>
        </form>
      </div>
    </div>
  );
};

export default Login;