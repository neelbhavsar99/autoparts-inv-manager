import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { api } from './services/api';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import BusinessSettings from './pages/BusinessSettings';
import Customers from './pages/Customers';
import Invoices from './pages/Invoices';
import CreateInvoice from './pages/CreateInvoice';
import ViewInvoice from './pages/ViewInvoice';
import Users from './pages/Users';
import LoadingSpinner from './components/LoadingSpinner';

function App() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }
      const response = await api.get('/auth/me');
      setUser(response.user);
    } catch (error) {
      localStorage.removeItem('token');
      console.error('Not authenticated');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData: any) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout');
      localStorage.removeItem('token');
      setUser(null);
    } catch (error) {
      localStorage.removeItem('token');
      setUser(null);
      console.error('Logout failed:', error);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={
            user ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />
          } 
        />
        <Route
          path="/"
          element={
            user ? <Layout user={user} onLogout={handleLogout} /> : <Navigate to="/login" />
          }
        >
          <Route index element={<Navigate to="/dashboard" />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="business" element={<BusinessSettings />} />
          <Route path="customers" element={<Customers />} />
          <Route path="invoices" element={<Invoices />} />
          <Route path="invoices/new" element={<CreateInvoice />} />
          <Route path="invoices/:id" element={<ViewInvoice />} />
          <Route path="users" element={<Users />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;