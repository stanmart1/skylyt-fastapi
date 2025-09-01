import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Car, BarChart3, Calendar, CreditCard, Settings, MessageSquare, ArrowLeft, Menu, TrendingUp, DollarSign, Users, X } from 'lucide-react';
import Navigation from '@/components/Navigation';
import { CarManagement } from '@/components/admin/CarManagement';
import CarBookingManagement from '@/components/admin/CarBookingManagement';
import { PaymentManagement } from '@/components/admin/PaymentManagement';
import { ReviewManagement } from '@/components/admin/ReviewManagement';
import { AnalyticsDashboard } from '@/components/analytics/AnalyticsDashboard';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { apiService } from '@/services/api';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';

interface CarStats {
  total_cars: number;
  available: number;
  booked: number;
  maintenance: number;
  revenue_today: number;
  utilization_rate: number;
}

const CarsManagementPage = () => {
  const { user, hasRole } = useAuth();
  const { currency } = useCurrency();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('analytics');
  const [stats, setStats] = useState<CarStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!hasRole('admin') && !hasRole('superadmin')) {
      navigate('/dashboard');
      return;
    }
    fetchCarStats();
  }, [hasRole, navigate]);

  const fetchCarStats = async () => {
    try {
      const response = await apiService.request('/admin/cars/stats');
      setStats(response);
    } catch (error) {
      console.error('Failed to fetch car stats:', error);
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
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setSidebarOpen(false)} />
          <div className="fixed left-0 top-0 h-full w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out">
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-green-600 rounded-lg flex items-center justify-center">
                    <Car className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gray-900">Car Management</h2>
                  </div>
                </div>
                <button onClick={() => setSidebarOpen(false)}>
                  <X className="h-6 w-6" />
                </button>
              </div>
            </div>
            <nav className="flex-1 p-4 space-y-2">
              <Button
                variant={activeTab === 'analytics' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => { setActiveTab('analytics'); setSidebarOpen(false); }}
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Analytics
              </Button>
              <Button
                variant={activeTab === 'bookings' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => { setActiveTab('bookings'); setSidebarOpen(false); }}
              >
                <Calendar className="h-4 w-4 mr-2" />
                Bookings
              </Button>
              <Button
                variant={activeTab === 'payments' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => { setActiveTab('payments'); setSidebarOpen(false); }}
              >
                <CreditCard className="h-4 w-4 mr-2" />
                Payments
              </Button>
              <Button
                variant={activeTab === 'management' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => { setActiveTab('management'); setSidebarOpen(false); }}
              >
                <Settings className="h-4 w-4 mr-2" />
                Fleet
              </Button>
              <Button
                variant={activeTab === 'reviews' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => { setActiveTab('reviews'); setSidebarOpen(false); }}
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                Reviews
              </Button>
            </nav>
          </div>
        </div>
      )}
      
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex w-64 bg-white shadow-sm border-r flex-col fixed left-0 top-16 h-[calc(100vh-4rem)] z-30">
        <div className="p-6 border-b">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-green-600 rounded-lg flex items-center justify-center">
              <Car className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">Car Management</h2>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Button
            variant={activeTab === 'analytics' ? 'default' : 'ghost'}
            className="w-full justify-start"
            onClick={() => setActiveTab('analytics')}
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            Analytics
          </Button>
          <Button
            variant={activeTab === 'bookings' ? 'default' : 'ghost'}
            className="w-full justify-start"
            onClick={() => setActiveTab('bookings')}
          >
            <Calendar className="h-4 w-4 mr-2" />
            Bookings
          </Button>
          <Button
            variant={activeTab === 'payments' ? 'default' : 'ghost'}
            className="w-full justify-start"
            onClick={() => setActiveTab('payments')}
          >
            <CreditCard className="h-4 w-4 mr-2" />
            Payments
          </Button>
          <Button
            variant={activeTab === 'management' ? 'default' : 'ghost'}
            className="w-full justify-start"
            onClick={() => setActiveTab('management')}
          >
            <Settings className="h-4 w-4 mr-2" />
            Fleet
          </Button>
          <Button
            variant={activeTab === 'reviews' ? 'default' : 'ghost'}
            className="w-full justify-start"
            onClick={() => setActiveTab('reviews')}
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            Reviews
          </Button>
        </nav>
      </div>

      <div className="flex-1 flex flex-col lg:ml-64">
        {/* Header */}
        <header className="bg-white shadow-sm border-b mt-16">
          <div className="px-4 sm:px-6 py-4">
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-4 sm:space-y-0">
              <div className="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
                <div className="flex items-center space-x-4">
                  <button 
                    className="lg:hidden"
                    onClick={() => setSidebarOpen(true)}
                  >
                    <Menu className="h-6 w-6" />
                  </button>
                  <Button variant="outline" size="sm" onClick={() => navigate('/admin')} className="w-fit">
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to Admin
                  </Button>
                </div>
                <div>
                  <h1 className="text-2xl sm:text-3xl font-bold flex items-center space-x-2">
                    <Car className="h-6 w-6 sm:h-8 sm:w-8" />
                    <span className="hidden sm:inline">Car Management Dashboard</span>
                    <span className="sm:hidden">Car Management</span>
                  </h1>
                  <p className="text-sm sm:text-base text-gray-600">Comprehensive car rental business management</p>
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="flex-1 p-4 sm:p-6 overflow-auto">
          {/* Stats Overview */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6">
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
                <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-white">Total Fleet</CardTitle>
                    <Car className="h-4 w-4 text-white" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-white">{stats.total_cars}</div>
                    <p className="text-xs text-blue-100">
                      {stats.available} available
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-white">Active Bookings</CardTitle>
                    <Calendar className="h-4 w-4 text-white" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-white">{stats.booked}</div>
                    <p className="text-xs text-green-100">
                      Currently rented
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-white">Revenue</CardTitle>
                    <DollarSign className="h-4 w-4 text-white" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-white">
                      <PriceDisplay amount={stats.revenue_today} currency={currency} />
                    </div>
                    <p className="text-xs text-yellow-100">
                      Today's revenue
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-white">Utilization</CardTitle>
                    <TrendingUp className="h-4 w-4 text-white" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-white">
                      {stats.utilization_rate}%
                    </div>
                    <p className="text-xs text-purple-100">
                      Fleet utilization
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



          {/* Tab Content */}
          {activeTab === 'analytics' && (
            <div className="space-y-4">
              {loading ? (
                <Card><CardContent className="p-6"><div className="animate-pulse h-64 bg-gray-200 rounded" /></CardContent></Card>
              ) : (
                <ErrorBoundary><AnalyticsDashboard /></ErrorBoundary>
              )}
            </div>
          )}

          {activeTab === 'bookings' && (
            <div className="space-y-4">
              {loading ? (
                <Card><CardContent className="p-6"><div className="animate-pulse h-64 bg-gray-200 rounded" /></CardContent></Card>
              ) : (
                <ErrorBoundary><CarBookingManagement /></ErrorBoundary>
              )}
            </div>
          )}

          {activeTab === 'payments' && (
            <div className="space-y-4">
              {loading ? (
                <Card><CardContent className="p-6"><div className="animate-pulse h-64 bg-gray-200 rounded" /></CardContent></Card>
              ) : (
                <ErrorBoundary><PaymentManagement /></ErrorBoundary>
              )}
            </div>
          )}

          {activeTab === 'management' && (
            <div className="space-y-4">
              {loading ? (
                <Card><CardContent className="p-6"><div className="animate-pulse h-64 bg-gray-200 rounded" /></CardContent></Card>
              ) : (
                <ErrorBoundary><CarManagement /></ErrorBoundary>
              )}
            </div>
          )}

          {activeTab === 'reviews' && (
            <div className="space-y-4">
              {loading ? (
                <Card><CardContent className="p-6"><div className="animate-pulse h-64 bg-gray-200 rounded" /></CardContent></Card>
              ) : (
                <ErrorBoundary><ReviewManagement /></ErrorBoundary>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CarsManagementPage;