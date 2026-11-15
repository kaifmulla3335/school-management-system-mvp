import { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import { getStudentsApi } from '../api/students';

const AdminDashboard = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const data = await getStudentsApi();
        setStudents(data);
      } catch (error) {
        console.error("Failed to fetch students", error);
      } finally {
        setLoading(false);
      }
    };
    fetchStudents();
  }, []);

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 p-8 bg-gray-50 min-h-screen">
        <h1 className="text-3xl font-bold mb-6">School Dashboard</h1>
        {loading ? <p>Loading...</p> : (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">All students</h2>
            <p className="text-gray-500 mb-4">{students.length} students shown</p>
            {/* Yahan aap apna purana student list ka table design paste karein */}
            <ul>
              {students.map((s) => (
                <li key={s.id} className="border-b p-2 flex justify-between">
                  <span>{s.name} (Class {s.class_name})</span>
                  <span className="text-gray-400">{s.admission_number}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;