import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import Navigation from '@/components/Navigation';
import { HotelDashboard } from '@/components/admin/HotelDashboard';
import { ErrorBoundary } from '@/components/ErrorBoundary';

const HotelManagementPage = () => {
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
            <HotelDashboard onBack={() => navigate('/admin')} />
          </ErrorBoundary>
        </div>
      </div>
    </div>
  );
};

export default HotelManagementPage;