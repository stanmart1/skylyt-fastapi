
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

import { Car, Hotel, Users, DollarSign, TrendingUp, Settings, LogOut, Shield, CreditCard, BarChart3, Calendar, User } from 'lucide-react';
import { UserManagement } from '@/components/admin/UserManagement';
import { EnhancedBookingManagement } from '@/components/admin/EnhancedBookingManagement';
import { BookingProvider } from '@/contexts/BookingContext';
import { ToastProvider } from '@/components/ui/toast';
import { PaymentManagement } from '@/components/admin/PaymentManagement';
import { AnalyticsDashboard } from '@/components/analytics/AnalyticsDashboard';
import { SystemHealth } from '@/components/admin/SystemHealth';
import { SettingsManagement } from '@/components/admin/SettingsManagement';
import HotelImageManagement from '@/components/admin/hotel-images/HotelImageManagement';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { apiService } from '@/services/api';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import { Plus, Edit, Trash2, Star, Heart, X, Menu, Monitor } from 'lucide-react';
import Navigation from '@/components/Navigation';

interface AdminStats {
  totalBookings: number;
  bookingChange: number;
  totalRevenue: number;
  revenueChange: number;
  activeUsers: number;
  fleetSize: number;
  totalCars: number;
  totalHotels: number;
}

const AdminDashboard = () => {
  const { user, logout, hasRole, hasPermission } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [activeUsers, setActiveUsers] = useState<number>(0);
  const [activityFilter, setActivityFilter] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [activityLoading, setActivityLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [roleModalOpen, setRoleModalOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState(null);
  const [rolePermissions, setRolePermissions] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [savingPermissions, setSavingPermissions] = useState(false);

  useEffect(() => {
    if (!hasRole('admin') && !hasRole('superadmin')) {
      navigate('/dashboard');
      return;
    }
    
    const fetchStats = async () => {
      try {
        const response = await apiService.getAdminStats();
        setStats(response);
      } catch (error) {
        console.error('Failed to fetch admin stats:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchStats();
    fetchRecentActivity();
    fetchActiveUsers();
  }, [hasRole, navigate]);

  const fetchRecentActivity = async (filter = '') => {
    try {
      setActivityLoading(true);
      const url = filter ? `/admin/recent-activity?activity_type=${filter}` : '/admin/recent-activity';
      const response = await apiService.request(url);
      setRecentActivity(response.activities || []);
    } catch (error) {
      console.error('Failed to fetch recent activity:', error);
    } finally {
      setActivityLoading(false);
    }
  };
  
  const fetchActiveUsers = async () => {
    try {
      const response = await apiService.request('/admin/active-users');
      setActiveUsers(response.active_users || 0);
    } catch (error) {
      console.error('Failed to fetch active users:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleRoleSettings = async (roleName, roleDisplayName) => {
    setSelectedRole({ name: roleName, displayName: roleDisplayName });
    try {
      const response = await apiService.request(`/admin/roles/${roleName}/permissions`);
      setRolePermissions(response.permissions || []);
    } catch (error) {
      console.error('Failed to load role permissions:', error);
      setRolePermissions([]);
    }
    setRoleModalOpen(true);
  };

  const handleSavePermissions = async () => {
    if (!selectedRole) return;
    
    setSavingPermissions(true);
    try {
      const assignedPermissions = rolePermissions
        .filter(p => p.assigned)
        .map(p => p.name);
      
      await apiService.request(`/admin/roles/${selectedRole.name}/permissions`, {
        method: 'PUT',
        body: JSON.stringify({ permissions: assignedPermissions })
      });
      
      alert('Permissions updated successfully!');
      setEditMode(false);
    } catch (error) {
      console.error('Failed to save permissions:', error);
      alert('Failed to save permissions. Please try again.');
    } finally {
      setSavingPermissions(false);
    }
  };

  if (!hasRole('admin') && !hasRole('superadmin')) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="flex">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setSidebarOpen(false)} />
          <div className="fixed left-0 top-0 h-full w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out">
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-teal-600 rounded-lg flex items-center justify-center">
                    <Settings className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gray-900">Admin Panel</h2>
                  </div>
                </div>
                <button onClick={() => setSidebarOpen(false)}>
                  <X className="h-6 w-6" />
                </button>
              </div>
            </div>
            <nav className="flex-1 p-4 space-y-2">
              <Button
                variant={activeTab === 'overview' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => { setActiveTab('overview'); setSidebarOpen(false); }}
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Overview
              </Button>
              {hasPermission('dashboard.view_analytics') && (
                <Button
                  variant={activeTab === 'analytics' ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => { setActiveTab('analytics'); setSidebarOpen(false); }}
                >
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Analytics
                </Button>
              )}
              {hasPermission('dashboard.view_users') && (
                <Button
                  variant={activeTab === 'users' ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => { setActiveTab('users'); setSidebarOpen(false); }}
                >
                  <Users className="h-4 w-4 mr-2" />
                  Users
                </Button>
              )}
              {hasPermission('dashboard.view_roles') && (
                <Button
                  variant={activeTab === 'roles' ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => { setActiveTab('roles'); setSidebarOpen(false); }}
                >
                  <Shield className="h-4 w-4 mr-2" />
                  Roles
                </Button>
              )}
              {hasPermission('dashboard.view_bookings') && (
                <Button
                  variant={activeTab === 'bookings' ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => { setActiveTab('bookings'); setSidebarOpen(false); }}
                >
                  <Calendar className="h-4 w-4 mr-2" />
                  Bookings
                </Button>
              )}
              {hasPermission('dashboard.view_payments') && (
                <Button
                  variant={activeTab === 'payments' ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => { setActiveTab('payments'); setSidebarOpen(false); }}
                >
                  <CreditCard className="h-4 w-4 mr-2" />
                  Payments
                </Button>
              )}
              {hasPermission('dashboard.view_system') && (
                <Button
                  variant={activeTab === 'system' ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => { setActiveTab('system'); setSidebarOpen(false); }}
                >
                  <Monitor className="h-4 w-4 mr-2" />
                  System
                </Button>
              )}
              {hasPermission('dashboard.view_cars') && (
                <Button
                  variant={activeTab === 'cars' ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => { setActiveTab('cars'); setSidebarOpen(false); }}
                >
                  <Car className="h-4 w-4 mr-2" />
                  Car Management
                </Button>
              )}
              {hasPermission('dashboard.view_hotels') && (
                <Button
                  variant={activeTab === 'hotels' ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => { setActiveTab('hotels'); setSidebarOpen(false); }}
                >
                  <Hotel className="h-4 w-4 mr-2" />
                  Hotel Management
                </Button>
              )}
              {hasPermission('dashboard.view_hotels') && (
                <Button
                  variant={activeTab === 'hotel-images' ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => { setActiveTab('hotel-images'); setSidebarOpen(false); }}
                >
                  <Hotel className="h-4 w-4 mr-2" />
                  Hotel Images
                </Button>
              )}
              {hasPermission('dashboard.view_settings') && (
                <Button
                  variant={activeTab === 'settings' ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => { setActiveTab('settings'); setSidebarOpen(false); }}
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </Button>
              )}
            </nav>
          </div>
        </div>
      )}
      
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex w-64 bg-white shadow-sm border-r flex-col fixed left-0 top-16 h-[calc(100vh-4rem)] z-30">
        {/* Sidebar Header */}
        <div className="p-6 border-b">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-teal-600 rounded-lg flex items-center justify-center">
              <Settings className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">Admin Panel</h2>
            </div>
          </div>
        </div>

        {/* Sidebar Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          <Button
            variant={activeTab === 'overview' ? 'default' : 'ghost'}
            className="w-full justify-start"
            onClick={() => setActiveTab('overview')}
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            Overview
          </Button>
          {hasPermission('dashboard.view_analytics') && (
            <Button
              variant={activeTab === 'analytics' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setActiveTab('analytics')}
            >
              <TrendingUp className="h-4 w-4 mr-2" />
              Analytics
            </Button>
          )}
          {hasPermission('dashboard.view_users') && (
            <Button
              variant={activeTab === 'users' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setActiveTab('users')}
            >
              <Users className="h-4 w-4 mr-2" />
              Users
            </Button>
          )}
          {hasPermission('dashboard.view_roles') && (
            <Button
              variant={activeTab === 'roles' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setActiveTab('roles')}
            >
              <Shield className="h-4 w-4 mr-2" />
              Roles
            </Button>
          )}
          {hasPermission('dashboard.view_bookings') && (
            <Button
              variant={activeTab === 'bookings' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setActiveTab('bookings')}
            >
              <Calendar className="h-4 w-4 mr-2" />
              Bookings
            </Button>
          )}
          {hasPermission('dashboard.view_payments') && (
            <Button
              variant={activeTab === 'payments' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setActiveTab('payments')}
            >
              <CreditCard className="h-4 w-4 mr-2" />
              Payments
            </Button>
          )}
          {hasPermission('dashboard.view_system') && (
            <Button
              variant={activeTab === 'system' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setActiveTab('system')}
            >
              <Monitor className="h-4 w-4 mr-2" />
              System
            </Button>
          )}
          {hasPermission('dashboard.view_cars') && (
            <Button
              variant={activeTab === 'cars' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setActiveTab('cars')}
            >
              <Car className="h-4 w-4 mr-2" />
              Car Management
            </Button>
          )}
          {hasPermission('dashboard.view_hotels') && (
            <Button
              variant={activeTab === 'hotels' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setActiveTab('hotels')}
            >
              <Hotel className="h-4 w-4 mr-2" />
              Hotel Management
            </Button>
          )}
          {hasPermission('dashboard.view_hotels') && (
            <Button
              variant={activeTab === 'hotel-images' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setActiveTab('hotel-images')}
            >
              <Hotel className="h-4 w-4 mr-2" />
              Hotel Images
            </Button>
          )}
          {hasPermission('dashboard.view_settings') && (
            <Button
              variant={activeTab === 'settings' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setActiveTab('settings')}
            >
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
          )}
        </nav>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col lg:ml-64">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="px-6 py-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-4">
                <button 
                  className="lg:hidden"
                  onClick={() => setSidebarOpen(true)}
                >
                  <Menu className="h-6 w-6" />
                </button>
              </div>
            </div>
          </div>
        </header>

        <div className="flex-1 p-6 overflow-auto">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Stats Overview */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Bookings</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalBookings}</div>
                  <p className={`text-xs ${stats.bookingChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {stats.bookingChange >= 0 ? '+' : ''}{stats.bookingChange}% from last month
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Revenue</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">${stats.totalRevenue.toLocaleString()}</div>
                  <p className={`text-xs ${stats.revenueChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {stats.revenueChange >= 0 ? '+' : ''}{stats.revenueChange}% from last month
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Users Online</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{activeUsers}</div>
                  <p className="text-xs text-gray-600">Currently online</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Fleet Size</CardTitle>
                  <Car className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.fleetSize}</div>
                  <p className="text-xs text-gray-600">{stats.totalCars} Cars, {stats.totalHotels} Hotels</p>
                </CardContent>
              </Card>
            </>
          ) : (
            <div className="col-span-4 text-center py-8">
              <p className="text-gray-600">Failed to load statistics</p>
            </div>
          )}
              </div>
            {/* Management Sections */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Car Management */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Car className="h-5 w-5" />
                    <span>Car Fleet Management</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {stats ? (
                    <>
                      <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                        <div>
                          <h4 className="font-semibold">Total Cars</h4>
                          <p className="text-gray-600">{stats.totalCars} cars in fleet</p>
                        </div>
                        <Badge className="bg-green-100 text-green-800">Active</Badge>
                      </div>
                      <Button 
                        className="w-full"
                        onClick={() => setActiveTab('cars')}
                      >
                        Manage Fleet
                      </Button>
                    </>
                  ) : (
                    <div className="animate-pulse space-y-4">
                      <div className="h-16 bg-gray-200 rounded-lg" />
                      <div className="h-10 bg-gray-200 rounded" />
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Hotel Management */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Hotel className="h-5 w-5" />
                    <span>Hotel Management</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {stats ? (
                    <>
                      <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                        <div>
                          <h4 className="font-semibold">Partner Hotels</h4>
                          <p className="text-gray-600">{stats.totalHotels} hotels in network</p>
                        </div>
                        <Badge className="bg-blue-100 text-blue-800">Active</Badge>
                      </div>
                      <Button 
                        className="w-full"
                        onClick={() => setActiveTab('hotels')}
                      >
                        Manage Hotels
                      </Button>
                    </>
                  ) : (
                    <div className="animate-pulse space-y-4">
                      <div className="h-16 bg-gray-200 rounded-lg" />
                      <div className="h-10 bg-gray-200 rounded" />
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card className="mt-8">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Recent Activity</CardTitle>
                  <select 
                    value={activityFilter} 
                    onChange={(e) => {
                      setActivityFilter(e.target.value);
                      fetchRecentActivity(e.target.value);
                    }}
                    className="px-3 py-1 border rounded-md text-sm"
                  >
                    <option value="">All Activities</option>
                    <option value="user">Users</option>
                    <option value="booking">Bookings</option>
                    <option value="payment">Payments</option>
                  </select>
                </div>
              </CardHeader>
              <CardContent>
                {activityLoading ? (
                  <div className="space-y-4">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="animate-pulse flex items-center space-x-3 p-3">
                        <div className="w-8 h-8 bg-gray-200 rounded-full" />
                        <div className="flex-1">
                          <div className="h-4 bg-gray-200 rounded mb-1" />
                          <div className="h-3 bg-gray-200 rounded w-2/3" />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : recentActivity.length > 0 ? (
                  <div className="space-y-4">
                    {recentActivity.map((activity) => {
                      const getActivityIcon = (type: string) => {
                        switch (type) {
                          case 'booking': return <Calendar className="h-4 w-4" />;
                          case 'user': return <User className="h-4 w-4" />;
                          case 'payment': return <DollarSign className="h-4 w-4" />;
                          default: return <Monitor className="h-4 w-4" />;
                        }
                      };
                      
                      const getStatusColor = (status: string) => {
                        switch (status) {
                          case 'confirmed': case 'completed': case 'active': return 'bg-green-100 text-green-800';
                          case 'pending': return 'bg-yellow-100 text-yellow-800';
                          case 'cancelled': case 'failed': case 'inactive': return 'bg-red-100 text-red-800';
                          default: return 'bg-gray-100 text-gray-800';
                        }
                      };
                      
                      return (
                        <div key={activity.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600">
                              {getActivityIcon(activity.type)}
                            </div>
                            <div>
                              <h4 className="font-medium text-sm">{activity.title}</h4>
                              <p className="text-xs text-gray-600">{activity.description}</p>
                              <p className="text-xs text-gray-500">
                                {new Date(activity.timestamp).toLocaleString()}
                              </p>
                            </div>
                          </div>
                          <Badge className={getStatusColor(activity.status)}>
                            {activity.status}
                          </Badge>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-600">No recent activity</p>
                  </div>
                )}
              </CardContent>
            </Card>
            </div>
          )}

          {activeTab === 'analytics' && hasPermission('dashboard.view_analytics') && (
            <div className="space-y-6">
            <ErrorBoundary>
              <AnalyticsDashboard />
            </ErrorBoundary>
            </div>
          )}

          {activeTab === 'users' && hasPermission('dashboard.view_users') && (
            <div className="space-y-6">
              <ErrorBoundary>
                <UserManagement />
              </ErrorBoundary>
            </div>
          )}

          {activeTab === 'bookings' && hasPermission('dashboard.view_bookings') && (
            <div className="space-y-6">
            <ErrorBoundary>
              <BookingProvider>
                <ToastProvider>
                  <EnhancedBookingManagement />
                </ToastProvider>
              </BookingProvider>
            </ErrorBoundary>
            </div>
          )}

          {activeTab === 'payments' && hasPermission('dashboard.view_payments') && (
            <div className="space-y-6">
            <ErrorBoundary>
              <PaymentManagement />
            </ErrorBoundary>
            </div>
          )}

          {activeTab === 'system' && hasPermission('dashboard.view_system') && (
            <div className="space-y-6">
            <ErrorBoundary>
              <SystemHealth />
            </ErrorBoundary>
            </div>
          )}

          {activeTab === 'cars' && hasPermission('dashboard.view_cars') && (
            <CarManagementTab />
          )}

          {activeTab === 'hotels' && hasPermission('dashboard.view_hotels') && (
            <HotelManagementTab />
          )}

          {activeTab === 'hotel-images' && hasPermission('dashboard.view_hotels') && (
            <div className="space-y-6">
              <div>
                <h1 className="text-3xl font-bold mb-2">Hotel Image Management</h1>
                <p className="text-gray-600">Manage hotel images and galleries</p>
              </div>
              <ErrorBoundary>
                <HotelImageManagement />
              </ErrorBoundary>
            </div>
          )}

          {activeTab === 'roles' && hasPermission('dashboard.view_roles') && (
            <div className="space-y-6">
              <div>
                <h1 className="text-3xl font-bold mb-2">Role Management</h1>
                <p className="text-gray-600">Manage user roles and permissions</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="border-2 border-red-200 bg-red-50 relative">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="absolute top-2 right-2 h-8 w-8 p-0 hover:bg-red-100"
                    onClick={() => handleRoleSettings('superadmin', 'Super Admin')}
                  >
                    <Settings className="h-4 w-4 text-red-600" />
                  </Button>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-10 h-10 bg-red-600 rounded-lg flex items-center justify-center">
                        <Shield className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-red-800">Super Admin</h3>
                        <p className="text-sm text-red-600">All Permissions</p>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600">Super Administrator with all permissions</p>
                  </CardContent>
                </Card>
                
                <Card className="border-2 border-blue-200 bg-blue-50 relative">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="absolute top-2 right-2 h-8 w-8 p-0 hover:bg-blue-100"
                    onClick={() => handleRoleSettings('admin', 'Admin')}
                  >
                    <Settings className="h-4 w-4 text-blue-600" />
                  </Button>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                        <Monitor className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-blue-800">Admin</h3>
                        <p className="text-sm text-blue-600">Management Access</p>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600">Administrator with management permissions</p>
                  </CardContent>
                </Card>
                
                <Card className="border-2 border-green-200 bg-green-50 relative">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="absolute top-2 right-2 h-8 w-8 p-0 hover:bg-green-100"
                    onClick={() => handleRoleSettings('accountant', 'Accountant')}
                  >
                    <Settings className="h-4 w-4 text-green-600" />
                  </Button>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                        <DollarSign className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-green-800">Accountant</h3>
                        <p className="text-sm text-green-600">Financial Access</p>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600">Accountant with financial permissions</p>
                  </CardContent>
                </Card>
                
                <Card className="border-2 border-gray-200 bg-gray-50 relative">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="absolute top-2 right-2 h-8 w-8 p-0 hover:bg-gray-100"
                    onClick={() => handleRoleSettings('customer', 'Customer')}
                  >
                    <Settings className="h-4 w-4 text-gray-600" />
                  </Button>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-10 h-10 bg-gray-600 rounded-lg flex items-center justify-center">
                        <User className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-800">Customer</h3>
                        <p className="text-sm text-gray-600">Basic Access</p>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600">Customer with basic permissions</p>
                  </CardContent>
                </Card>
              </div>
              
              {/* Role Permissions Modal */}
              <Dialog open={roleModalOpen} onOpenChange={setRoleModalOpen}>
                <DialogContent className="max-w-4xl">
                  <DialogHeader>
                    <div className="flex items-center justify-between">
                      <DialogTitle>{selectedRole?.displayName} Permissions</DialogTitle>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => setEditMode(!editMode)}
                      >
                        {editMode ? 'View Mode' : 'Edit Permissions'}
                      </Button>
                    </div>
                  </DialogHeader>
                  <div className="max-h-96 overflow-y-auto">
                    {editMode ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {rolePermissions.map((permission) => (
                          <Card key={permission.name} className={`p-3 relative cursor-pointer hover:shadow-md transition-shadow ${
                            permission.assigned ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'
                          }`}>
                            <input
                              type="checkbox"
                              checked={permission.assigned}
                              onChange={(e) => {
                                setRolePermissions(prev => 
                                  prev.map(p => 
                                    p.name === permission.name 
                                      ? { ...p, assigned: e.target.checked }
                                      : p
                                  )
                                );
                              }}
                              className="absolute top-2 right-2 w-4 h-4 text-blue-600"
                            />
                            <div className="pr-6">
                              <h4 className={`font-medium text-sm ${
                                permission.assigned ? 'text-blue-800' : 'text-gray-800'
                              }`}>{permission.name}</h4>
                              <p className={`text-xs mt-1 ${
                                permission.assigned ? 'text-blue-600' : 'text-gray-600'
                              }`}>{permission.description}</p>
                              <p className="text-xs text-gray-500 mt-1">{permission.resource} • {permission.action}</p>
                            </div>
                          </Card>
                        ))}
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {rolePermissions.filter(p => p.assigned).map((permission) => (
                          <Card key={permission.name} className="p-3 bg-blue-50 border-blue-200">
                            <div>
                              <h4 className="font-medium text-sm text-blue-800">{permission.name}</h4>
                              <p className="text-xs text-blue-600 mt-1">{permission.description}</p>
                              <p className="text-xs text-gray-500 mt-1">{permission.resource} • {permission.action}</p>
                            </div>
                          </Card>
                        ))}
                        {rolePermissions.filter(p => p.assigned).length === 0 && (
                          <p className="text-gray-500 col-span-full text-center py-8">No permissions assigned to this role</p>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2 pt-4">
                    {editMode && (
                      <Button onClick={handleSavePermissions} disabled={savingPermissions}>Save Changes</Button>
                    )}
                    <Button variant="outline" onClick={() => { setRoleModalOpen(false); setEditMode(false); }}>Close</Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          )}

          {activeTab === 'settings' && hasPermission('dashboard.view_settings') && (
            <div className="space-y-6">
              <div>
                <h1 className="text-3xl font-bold mb-2">Admin Settings</h1>
                <p className="text-gray-600">Configure system settings and preferences</p>
              </div>
              <ErrorBoundary>
                <SettingsManagement />
              </ErrorBoundary>
            </div>
          )}
        </div>
      </div>
      </div>
    </div>
  );
};

// Car Management Tab Component
const CarManagementTab = () => {
  const [cars, setCars] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCar, setEditingCar] = useState<any>(null);
  const [carForm, setCarForm] = useState({
    name: '',
    category: '',
    price: 0,
    image_url: '',
    passengers: 4,
    transmission: 'automatic',
    features: ''
  });
  const [carImageFile, setCarImageFile] = useState<File | null>(null);
  const [uploadingCarImage, setUploadingCarImage] = useState(false);

  useEffect(() => {
    fetchCars();
  }, []);

  const fetchCars = async () => {
    try {
      const data = await apiService.request('/admin/cars');
      setCars(data);
    } catch (error) {
      console.error('Failed to fetch cars:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCar = () => {
    setEditingCar(null);
    setCarForm({ name: '', category: '', price: 0, image_url: '', passengers: 4, transmission: 'automatic', features: '' });
    setIsModalOpen(true);
  };

  const handleEditCar = (car: any) => {
    setEditingCar(car);
    setCarForm({
      name: car.name,
      category: car.category,
      price: car.price,
      image_url: car.image_url || '',
      passengers: car.passengers,
      transmission: car.transmission,
      features: car.features.join(', ')
    });
    setIsModalOpen(true);
  };

  const handleCarImageUpload = async (file: File) => {
    setUploadingCarImage(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('upload_type', 'cars');
      
      const response = await apiService.uploadFile(formData);
      setCarForm({ ...carForm, image_url: `http://localhost:8000${response.url}` });
    } catch (error) {
      console.error('Failed to upload image:', error);
    } finally {
      setUploadingCarImage(false);
    }
  };

  const handleSaveCar = async () => {
    try {
      let finalCarData = { ...carForm, features: carForm.features.split(',').map(f => f.trim()).filter(f => f) };
      
      // Upload image if selected
      if (carImageFile) {
        await handleCarImageUpload(carImageFile);
        finalCarData = { ...carForm, features: carForm.features.split(',').map(f => f.trim()).filter(f => f) };
      }
      
      if (editingCar) {
        await apiService.request(`/admin/cars/${editingCar.id}`, { method: 'PUT', body: JSON.stringify(finalCarData) });
      } else {
        await apiService.request('/admin/cars', { method: 'POST', body: JSON.stringify(finalCarData) });
      }
      await fetchCars();
      setIsModalOpen(false);
      setCarImageFile(null);
    } catch (error) {
      console.error('Failed to save car:', error);
    }
  };

  const handleDeleteCar = async (carId: string) => {
    if (!confirm('Are you sure you want to delete this car?')) return;
    try {
      await apiService.request(`/admin/cars/${carId}`, { method: 'DELETE' });
      await fetchCars();
    } catch (error) {
      console.error('Failed to delete car:', error);
    }
  };

  const handleFeatureCar = async (carId: string) => {
    try {
      await apiService.request(`/admin/cars/${carId}/feature`, { method: 'POST' });
      await fetchCars();
    } catch (error) {
      console.error('Failed to feature car:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Car Management</h2>
        <Button onClick={handleAddCar}>
          <Plus className="h-4 w-4 mr-2" />
          Add Car
        </Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-32 bg-gray-200 rounded mb-4" />
                <div className="h-4 bg-gray-200 rounded mb-2" />
                <div className="h-4 bg-gray-200 rounded w-2/3" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cars.map((car) => (
            <Card key={car.id}>
              <CardContent className="p-6">
                {car.image_url ? (
                  <div className="w-full h-32 mb-4 rounded-lg overflow-hidden">
                    <img src={car.image_url} alt={car.name} className="w-full h-full object-cover" />
                  </div>
                ) : (
                  <div className="flex items-center justify-center w-full h-32 mb-4 bg-gray-100 rounded-lg">
                    <Car className="h-8 w-8 text-gray-400" />
                  </div>
                )}
                <h3 className="font-semibold text-lg">{car.name}</h3>
                <p className="text-gray-600 mb-2">{car.category}</p>
                <p className="text-lg font-bold text-blue-600">${car.price}/day</p>
                <div className="mt-4 space-y-1 text-sm text-gray-600">
                  <p>{car.passengers} passengers • {car.transmission}</p>
                </div>
                <div className="flex gap-2 mt-4">
                  <Button variant="outline" size="sm" onClick={() => handleEditCar(car)}>
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleFeatureCar(car.id)}
                    className={car.is_featured ? 'text-yellow-600 hover:text-yellow-700' : 'text-gray-600 hover:text-gray-700'}
                  >
                    <Star className={`h-3 w-3 ${car.is_featured ? 'fill-current' : ''}`} />
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => handleDeleteCar(car.id)} className="text-red-600 hover:text-red-700">
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingCar ? 'Edit Car' : 'Add New Car'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Car Name</Label>
              <Input id="name" value={carForm.name} onChange={(e) => setCarForm({...carForm, name: e.target.value})} />
            </div>
            <div>
              <Label htmlFor="category">Category</Label>
              <Input id="category" value={carForm.category} onChange={(e) => setCarForm({...carForm, category: e.target.value})} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="price">Price per day</Label>
                <Input id="price" type="number" value={carForm.price} onChange={(e) => setCarForm({...carForm, price: Number(e.target.value)})} />
              </div>
              <div>
                <Label htmlFor="passengers">Passengers</Label>
                <Input id="passengers" type="number" value={carForm.passengers} onChange={(e) => setCarForm({...carForm, passengers: Number(e.target.value)})} />
              </div>
            </div>
            <div>
              <Label htmlFor="transmission">Transmission</Label>
              <Input id="transmission" value={carForm.transmission} onChange={(e) => setCarForm({...carForm, transmission: e.target.value})} />
            </div>
            <div>
              <Label htmlFor="car_image">Car Image</Label>
              <div className="flex items-center gap-2">
                <input
                  id="car_image"
                  type="file"
                  accept="image/*"
                  onChange={(e) => setCarImageFile(e.target.files?.[0] || null)}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => document.getElementById('car_image')?.click()}
                  disabled={uploadingCarImage}
                >
                  {uploadingCarImage ? 'Uploading...' : 'Choose File'}
                </Button>
                {carImageFile && <span className="text-sm text-gray-600">{carImageFile.name}</span>}
              </div>
            </div>
            <div>
              <Label htmlFor="features">Features (comma separated)</Label>
              <Input id="features" value={carForm.features} onChange={(e) => setCarForm({...carForm, features: e.target.value})} placeholder="GPS, AC, Bluetooth" />
            </div>
            <div className="flex gap-2 pt-4">
              <Button onClick={handleSaveCar}>{editingCar ? 'Update Car' : 'Add Car'}</Button>
              <Button variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Hotel Management Tab Component
const HotelManagementTab = () => {
  const [hotels, setHotels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingHotel, setEditingHotel] = useState<any>(null);
  const [hotelForm, setHotelForm] = useState({
    name: '',
    location: '',
    rating: 4,
    price: 0,
    image_url: '',
    amenities: '',
    description: ''
  });
  const [hotelImageFile, setHotelImageFile] = useState<File | null>(null);
  const [uploadingHotelImage, setUploadingHotelImage] = useState(false);

  useEffect(() => {
    fetchHotels();
  }, []);

  const fetchHotels = async () => {
    try {
      const data = await apiService.request('/admin/hotels');
      setHotels(data);
    } catch (error) {
      console.error('Failed to fetch hotels:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddHotel = () => {
    setEditingHotel(null);
    setHotelForm({ name: '', location: '', rating: 4, price: 0, image_url: '', amenities: '', description: '' });
    setIsModalOpen(true);
  };

  const handleEditHotel = (hotel: any) => {
    setEditingHotel(hotel);
    setHotelForm({
      name: hotel.name,
      location: hotel.location,
      rating: hotel.rating,
      price: hotel.price,
      image_url: hotel.image_url || '',
      amenities: hotel.amenities.join(', '),
      description: hotel.description
    });
    setIsModalOpen(true);
  };

  const handleHotelImageUpload = async (file: File) => {
    setUploadingHotelImage(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('upload_type', 'hotels');
      
      const response = await apiService.uploadFile(formData);
      setHotelForm({ ...hotelForm, image_url: `http://localhost:8000${response.url}` });
    } catch (error) {
      console.error('Failed to upload image:', error);
    } finally {
      setUploadingHotelImage(false);
    }
  };

  const handleSaveHotel = async () => {
    try {
      let finalHotelData = { ...hotelForm, amenities: hotelForm.amenities.split(',').map(a => a.trim()).filter(a => a) };
      
      // Upload image if selected
      if (hotelImageFile) {
        await handleHotelImageUpload(hotelImageFile);
        finalHotelData = { ...hotelForm, amenities: hotelForm.amenities.split(',').map(a => a.trim()).filter(a => a) };
      }
      
      if (editingHotel) {
        await apiService.request(`/admin/hotels/${editingHotel.id}`, { method: 'PUT', body: JSON.stringify(finalHotelData) });
      } else {
        await apiService.request('/admin/hotels', { method: 'POST', body: JSON.stringify(finalHotelData) });
      }
      await fetchHotels();
      setIsModalOpen(false);
      setHotelImageFile(null);
    } catch (error) {
      console.error('Failed to save hotel:', error);
    }
  };

  const handleFeatureHotel = async (hotelId: string) => {
    try {
      await apiService.request(`/admin/hotels/${hotelId}/feature`, { method: 'POST' });
      await fetchHotels();
    } catch (error) {
      console.error('Failed to feature hotel:', error);
    }
  };

  const handleDeleteHotel = async (hotelId: string) => {
    if (!confirm('Are you sure you want to delete this hotel?')) return;
    try {
      await apiService.request(`/admin/hotels/${hotelId}`, { method: 'DELETE' });
      await fetchHotels();
    } catch (error) {
      console.error('Failed to delete hotel:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Hotel Management</h2>
        <Button onClick={handleAddHotel}>
          <Plus className="h-4 w-4 mr-2" />
          Add Hotel
        </Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-32 bg-gray-200 rounded mb-4" />
                <div className="h-4 bg-gray-200 rounded mb-2" />
                <div className="h-4 bg-gray-200 rounded w-2/3" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {hotels.map((hotel) => (
            <Card key={hotel.id}>
              <CardContent className="p-6">
                {hotel.image_url ? (
                  <div className="w-full h-32 mb-4 rounded-lg overflow-hidden">
                    <img src={hotel.image_url} alt={hotel.name} className="w-full h-full object-cover" />
                  </div>
                ) : (
                  <div className="flex items-center justify-center w-full h-32 mb-4 bg-gray-100 rounded-lg">
                    <Hotel className="h-8 w-8 text-gray-400" />
                  </div>
                )}
                <h3 className="font-semibold text-lg">{hotel.name}</h3>
                <p className="text-gray-600 mb-2">{hotel.location}</p>
                <div className="flex items-center gap-1 mb-2">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className={`h-4 w-4 ${i < hotel.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} />
                  ))}
                  <span className="text-sm text-gray-600 ml-1">({hotel.rating})</span>
                </div>
                <p className="text-lg font-bold text-blue-600">${hotel.price}/night</p>
                <p className="text-sm text-gray-600 mt-2 line-clamp-2">{hotel.description}</p>
                <div className="flex gap-2 mt-4">
                  <Button variant="outline" size="sm" onClick={() => handleEditHotel(hotel)}>
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleFeatureHotel(hotel.id)}
                    className={hotel.is_featured ? 'bg-yellow-100 text-yellow-800' : ''}
                    title={hotel.is_featured ? 'Remove from featured' : 'Add to featured'}
                  >
                    <Star className={`h-3 w-3 ${hotel.is_featured ? 'fill-current' : ''}`} />
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => handleDeleteHotel(hotel.id)} className="text-red-600 hover:text-red-700">
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingHotel ? 'Edit Hotel' : 'Add New Hotel'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Hotel Name</Label>
              <Input id="name" value={hotelForm.name} onChange={(e) => setHotelForm({...hotelForm, name: e.target.value})} />
            </div>
            <div>
              <Label htmlFor="location">Location</Label>
              <Input id="location" value={hotelForm.location} onChange={(e) => setHotelForm({...hotelForm, location: e.target.value})} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="rating">Rating (1-5)</Label>
                <Input id="rating" type="number" min="1" max="5" value={hotelForm.rating} onChange={(e) => setHotelForm({...hotelForm, rating: Number(e.target.value)})} />
              </div>
              <div>
                <Label htmlFor="price">Price per night</Label>
                <Input id="price" type="number" value={hotelForm.price} onChange={(e) => setHotelForm({...hotelForm, price: Number(e.target.value)})} />
              </div>
            </div>
            <div>
              <Label htmlFor="hotel_image">Hotel Image</Label>
              <div className="flex items-center gap-2">
                <input
                  id="hotel_image"
                  type="file"
                  accept="image/*"
                  onChange={(e) => setHotelImageFile(e.target.files?.[0] || null)}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => document.getElementById('hotel_image')?.click()}
                  disabled={uploadingHotelImage}
                >
                  {uploadingHotelImage ? 'Uploading...' : 'Choose File'}
                </Button>
                {hotelImageFile && <span className="text-sm text-gray-600">{hotelImageFile.name}</span>}
              </div>
            </div>
            <div>
              <Label htmlFor="amenities">Amenities (comma separated)</Label>
              <Input id="amenities" value={hotelForm.amenities} onChange={(e) => setHotelForm({...hotelForm, amenities: e.target.value})} placeholder="WiFi, Pool, Gym, Spa" />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Input id="description" value={hotelForm.description} onChange={(e) => setHotelForm({...hotelForm, description: e.target.value})} placeholder="Hotel description..." />
            </div>
            <div className="flex gap-2 pt-4">
              <Button onClick={handleSaveHotel}>{editingHotel ? 'Update Hotel' : 'Add Hotel'}</Button>
              <Button variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminDashboard;
