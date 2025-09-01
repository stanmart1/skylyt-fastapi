import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import Navigation from '@/components/Navigation';
import { CarDashboard } from '@/components/admin/CarDashboard';
import { ErrorBoundary } from '@/components/ErrorBoundary';

const CarsManagementPage = () => {
  const { user, hasRole } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!hasRole('admin') && !hasRole('superadmin')) {
      navigate('/dashboard');
      return;
    }
  }, [hasRole, navigate]);

  if (!hasRole('admin') && !hasRole('superadmin')) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="pt-16">
        <div className="container mx-auto px-6 py-8">
          <ErrorBoundary>
            <CarDashboard onBack={() => navigate('/admin')} />
          </ErrorBoundary>
        </div>
      </div>
    </div>
  );
};

export default CarsManagementPage;