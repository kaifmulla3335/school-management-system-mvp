import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import { createStudentAccountApi } from '../api/students';
import { useNavigate } from 'react-router-dom';

const AddStudent = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '', class_name: '1', roll_number: '', date_of_birth: '',
    gender: 'Male', guardian_name: '', guardian_phone: '', address: '',
    admission_date: new Date().toISOString().split('T')[0], password: ''
  });

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createStudentAccountApi(formData);
      alert('Student added successfully!');
      navigate('/admin');
    } catch (error) {
      alert('Failed to add student. Check console.');
      console.error(error);
    }
  };

  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 p-8 bg-gray-50 min-h-screen">
        <h1 className="text-2xl font-bold mb-6">Add New Student</h1>
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow grid grid-cols-2 gap-4">
          <input name="name" placeholder="Full Name" onChange={handleChange} required className="border p-2 rounded" />
          <select name="class_name" onChange={handleChange} className="border p-2 rounded">
            {[1,2,3,4,5,6,7,8,9,10].map(c => <option key={c} value={c}>Class {c}</option>)}
          </select>
          <input name="roll_number" placeholder="Roll Number" onChange={handleChange} required className="border p-2 rounded" />
          <input type="date" name="date_of_birth" onChange={handleChange} required className="border p-2 rounded" />
          <select name="gender" onChange={handleChange} className="border p-2 rounded">
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
          </select>
          <input name="guardian_name" placeholder="Guardian Name" onChange={handleChange} required className="border p-2 rounded" />
          <input name="guardian_phone" placeholder="Guardian Phone" onChange={handleChange} required className="border p-2 rounded" />
          <input name="address" placeholder="Address" onChange={handleChange} required className="border p-2 rounded" />
          <input type="date" name="admission_date" onChange={handleChange} required className="border p-2 rounded" />
          <input type="password" name="password" placeholder="Initial Password (min 8 chars)" onChange={handleChange} required className="border p-2 rounded" />
          <button type="submit" className="col-span-2 bg-blue-600 text-white p-2 rounded hover:bg-blue-700">Add Student</button>
        </form>
      </div>
    </div>
  );
};

export default AddStudent;