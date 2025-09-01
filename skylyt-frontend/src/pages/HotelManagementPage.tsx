import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Hotel, BarChart3, Calendar, CreditCard, Settings, MessageSquare, ArrowLeft, Menu, TrendingUp, DollarSign, Users } from 'lucide-react';
import Navigation from '@/components/Navigation';
import { HotelManagement } from '@/components/admin/HotelManagement';
import HotelBookingManagement from '@/components/admin/HotelBookingManagement';
import { PaymentManagement } from '@/components/admin/PaymentManagement';
import { ReviewManagement } from '@/components/admin/ReviewManagement';
import { AnalyticsDashboard } from '@/components/analytics/AnalyticsDashboard';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { apiService } from '@/services/api';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';

interface HotelStats {
  totalHotels: number;
  totalRooms: number;
  activeBookings: number;
  totalRevenue: number;
  revenueChange: number;
  occupancyRate: number;
}

const HotelManagementPage = () => {
  const { user, hasRole } = useAuth();
  const { currency } = useCurrency();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('analytics');
  const [stats, setStats] = useState<HotelStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!hasRole('admin') && !hasRole('superadmin')) {
      navigate('/dashboard');
      return;
    }
    fetchHotelStats();
  }, [hasRole, navigate]);

  const fetchHotelStats = async () => {
    try {
      const response = await apiService.request('/admin/hotel-stats');
      setStats(response);
    } catch (error) {
      console.error('Failed to fetch hotel stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!hasRole('admin') && !hasRole('superadmin')) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white shadow-sm border-b mt-16">
          <div className="px-6 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-4">
                <Button variant="outline" size="sm" onClick={() => navigate('/admin')}>
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Admin
                </Button>
                <div>
                  <h1 className="text-3xl font-bold flex items-center space-x-2">
                    <Hotel className="h-8 w-8" />
                    <span>Hotel Management Dashboard</span>
                  </h1>
                  <p className="text-gray-600">Comprehensive hotel business management</p>
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="flex-1 p-6 overflow-auto">
          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            {loading ? (
              [...Array(4)].map((_, i) => (
                <Card key={i}>
                  <CardContent className="p-6">
                    <div className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded mb-2" />
                      <div className="h-8 bg-gray-200 rounded mb-1" />
                      <div className="h-3 bg-gray-200 rounded w-2/3" />
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : stats ? (
              <>
                <Card className="border-l-4 border-blue-500">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Properties</CardTitle>
                    <Hotel className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stats.totalHotels}</div>
                    <p className="text-xs text-muted-foreground">
                      {stats.totalRooms} total rooms
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-l-4 border-green-500">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Active Bookings</CardTitle>
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stats.activeBookings}</div>
                    <p className="text-xs text-muted-foreground">
                      Current reservations
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-l-4 border-yellow-500">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Revenue</CardTitle>
                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      <PriceDisplay amount={stats.totalRevenue} currency={currency} />
                    </div>
                    <p className={`text-xs ${stats.revenueChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {stats.revenueChange >= 0 ? '+' : ''}{stats.revenueChange}% from last month
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-l-4 border-purple-500">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Occupancy Rate</CardTitle>
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stats.occupancyRate}%</div>
                    <p className="text-xs text-muted-foreground">
                      Current occupancy
                    </p>
                  </CardContent>
                </Card>
              </>
            ) : (
              <div className="col-span-4 text-center py-8">
                <p className="text-gray-600">Failed to load statistics</p>
              </div>
            )}
          </div>

          {/* Navigation Tabs */}
          <Card className="mb-6">
            <CardHeader>
              <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
                <Button
                  variant={activeTab === 'analytics' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveTab('analytics')}
                  className="flex items-center space-x-2"
                >
                  <BarChart3 className="h-4 w-4" />
                  <span>Analytics</span>
                </Button>
                <Button
                  variant={activeTab === 'bookings' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveTab('bookings')}
                  className="flex items-center space-x-2"
                >
                  <Calendar className="h-4 w-4" />
                  <span>Bookings</span>
                </Button>
                <Button
                  variant={activeTab === 'payments' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveTab('payments')}
                  className="flex items-center space-x-2"
                >
                  <CreditCard className="h-4 w-4" />
                  <span>Payments</span>
                </Button>
                <Button
                  variant={activeTab === 'management' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveTab('management')}
                  className="flex items-center space-x-2"
                >
                  <Settings className="h-4 w-4" />
                  <span>Properties</span>
                </Button>
                <Button
                  variant={activeTab === 'reviews' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveTab('reviews')}
                  className="flex items-center space-x-2"
                >
                  <MessageSquare className="h-4 w-4" />
                  <span>Reviews</span>
                </Button>
              </div>
            </CardHeader>
          </Card>

          {/* Tab Content */}
          {activeTab === 'analytics' && (
            <ErrorBoundary>
              <AnalyticsDashboard />
            </ErrorBoundary>
          )}

          {activeTab === 'bookings' && (
            <ErrorBoundary>
              <HotelBookingManagement />
            </ErrorBoundary>
          )}

          {activeTab === 'payments' && (
            <ErrorBoundary>
              <PaymentManagement />
            </ErrorBoundary>
          )}

          {activeTab === 'management' && (
            <ErrorBoundary>
              <HotelManagement />
            </ErrorBoundary>
          )}

          {activeTab === 'reviews' && (
            <ErrorBoundary>
              <ReviewManagement />
            </ErrorBoundary>
          )}
        </div>
      </div>
    </div>
  );
};

export default HotelManagementPage;