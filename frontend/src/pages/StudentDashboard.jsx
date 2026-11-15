import { useState, useEffect, useContext } from 'react';
import Sidebar from '../components/Sidebar';
import { AuthContext } from '../context/AuthContext';

const StudentDashboard = () => {
  const { user } = useContext(AuthContext);
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch('http://localhost:8000/student/dashboard', {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        setProfileData(data);
      } catch (error) {
        console.error("Failed to fetch dashboard", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 p-8 bg-gray-50 min-h-screen">
        <h1 className="text-3xl font-bold mb-2">My Dashboard</h1>
        <p className="text-gray-500 mb-6">Your school details, all in one place.</p>
        
        {loading ? <p>Loading...</p> : profileData && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">My profile</h2>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-500">Full name</p>
                <p className="font-medium">{profileData.profile.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Admission number</p>
                <p className="font-medium">{profileData.profile.admission_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Class</p>
                <p className="font-medium">{profileData.profile.class_name}</p>
              </div>
              {/* Baaki fields yahan add karein */}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentDashboard;