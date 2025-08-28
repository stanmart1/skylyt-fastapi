import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import HotelBookingManagement from '@/components/admin/HotelBookingManagement';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import Navigation from '@/components/Navigation';

const HotelBookingsPage = () => {
  const { hasRole, hasPermission } = useAuth();
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
      <div className="container mx-auto px-6 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Hotel Bookings</h1>
          <p className="text-gray-600">Manage all hotel booking reservations</p>
        </div>
        <ErrorBoundary>
          <HotelBookingManagement />
        </ErrorBoundary>
      </div>
    </div>
  );
};

export default HotelBookingsPage;