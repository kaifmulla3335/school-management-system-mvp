import api from './axios';

export const getStudentsApi = async () => {
  const res = await api.get('/students');
  return res.data;
};

export const createStudentAccountApi = async (data) => {
  const res = await api.post('/admin/student-accounts', data);
  return res.data;
};

// Yahan aur bhi API calls aa sakti hain (Delete, Update, etc.)