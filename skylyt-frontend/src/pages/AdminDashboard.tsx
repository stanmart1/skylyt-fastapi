
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';

import { Car, Hotel, Users, DollarSign, Settings, LogOut, Shield, CreditCard, BarChart3, Calendar, User, MessageSquare, Ticket, Bell, ChevronDown, ChevronRight } from 'lucide-react';
import { UserManagement } from '@/components/admin/UserManagement';
import { EnhancedBookingManagement } from '@/components/admin/EnhancedBookingManagement';
import HotelBookingManagement from '@/components/admin/HotelBookingManagement';
import CarBookingManagement from '@/components/admin/CarBookingManagement';
import { BookingProvider } from '@/contexts/BookingContext';
import { ToastProvider } from '@/components/ui/toast';
import { PaymentManagement } from '@/components/admin/PaymentManagement';

import { SystemHealth } from '@/components/admin/SystemHealth';
import { SettingsManagement } from '@/components/admin/SettingsManagement';
import { GeneralSettings } from '@/pages/admin/GeneralSettings';
import { PaymentSettings } from '@/pages/admin/PaymentSettings';
import { BankTransferSettings } from '@/pages/admin/BankTransferSettings';
import { CurrencySettings } from '@/pages/admin/CurrencySettings';
import { NotificationSettings } from '@/pages/admin/NotificationSettings';
import { SecuritySettings } from '@/pages/admin/SecuritySettings';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { apiService } from '@/services/api';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import { Plus, Edit, Trash2, Star, Heart, X, Menu, Monitor } from 'lucide-react';
import Navigation from '@/components/Navigation';
import { CarManagement } from '@/components/admin/CarManagement';
import { HotelManagement } from '@/components/admin/HotelManagement';
import { ReviewManagement } from '@/components/admin/ReviewManagement';
import { SupportTicketManagement } from '@/components/admin/SupportTicketManagement';
import { NotificationCenter } from '@/components/admin/NotificationCenter';
import { NotificationSender } from '@/components/admin/NotificationSender';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { Toaster } from '@/components/ui/sonner';
import { useToast } from '@/hooks/useToast';
import { AnalyticsDashboard } from '@/components/analytics/AnalyticsDashboard';
import { CarFleetStats } from '@/components/admin/CarFleetStats';
import { HotelOverviewStats } from '@/components/admin/HotelOverviewStats';
import { DriverManagement } from '@/components/admin/DriverManagement';

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
  const { currency } = useCurrency();
  const { toast, dismiss, toasts } = useToast();
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
  const [settingsDropdownOpen, setSettingsDropdownOpen] = useState(false);
  const [activeSettingsTab, setActiveSettingsTab] = useState<string | null>(null);
  const [carDropdownOpen, setCarDropdownOpen] = useState(false);
  const [activeCarTab, setActiveCarTab] = useState<string | null>(null);
  const [hotelDropdownOpen, setHotelDropdownOpen] = useState(false);
  const [activeHotelTab, setActiveHotelTab] = useState<string | null>(null);

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
      setRecentActivity(Array.isArray(response?.activities) ? response.activities : Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Failed to fetch recent activity:', error);
      setRecentActivity([]);
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
      setRolePermissions(Array.isArray(response?.permissions) ? response.permissions : Array.isArray(response) ? response : []);
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
      const assignedPermissions = Array.isArray(rolePermissions) 
        ? rolePermissions.filter(p => p && p.assigned).map(p => p.name)
        : [];
      
      await apiService.request(`/admin/roles/${selectedRole.name}/permissions`, {
        method: 'PUT',
        body: JSON.stringify({ permissions: assignedPermissions })
      });
      
      toast({
        title: 'Success',
        description: 'Permissions updated successfully!',
        variant: 'success'
      });
      setEditMode(false);
    } catch (error) {
      console.error('Failed to save permissions:', error);
      toast({
        title: 'Error',
        description: 'Failed to save permissions. Please try again.',
        variant: 'error'
      });
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
            <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
              <Button
                variant={activeTab === 'overview' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => { setActiveTab('overview'); setSidebarOpen(false); }}
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Overview
              </Button>

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
                <div className="space-y-1">
                  <Button
                    variant="ghost"
                    className="w-full justify-between"
                    onClick={() => setCarDropdownOpen(!carDropdownOpen)}
                  >
                    <div className="flex items-center">
                      <Car className="h-4 w-4 mr-2" />
                      Car Management
                    </div>
                    {carDropdownOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  </Button>
                  {carDropdownOpen && (
                    <div className="ml-6 space-y-1">
                      <Button
                        variant={activeCarTab === 'overview' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('car-management'); setActiveCarTab('overview'); setSidebarOpen(false); }}
                      >
                        Overview
                      </Button>
                      <Button
                        variant={activeCarTab === 'bookings' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('car-management'); setActiveCarTab('bookings'); setSidebarOpen(false); }}
                      >
                        Bookings
                      </Button>
                      <Button
                        variant={activeCarTab === 'payments' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('car-management'); setActiveCarTab('payments'); setSidebarOpen(false); }}
                      >
                        Payments
                      </Button>
                      <Button
                        variant={activeCarTab === 'fleet' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('car-management'); setActiveCarTab('fleet'); setSidebarOpen(false); }}
                      >
                        Fleet
                      </Button>
                      <Button
                        variant={activeCarTab === 'reviews' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('car-management'); setActiveCarTab('reviews'); setSidebarOpen(false); }}
                      >
                        Reviews
                      </Button>
                      <Button
                        variant={activeCarTab === 'drivers' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('car-management'); setActiveCarTab('drivers'); setSidebarOpen(false); }}
                      >
                        Drivers
                      </Button>
                    </div>
                  )}
                </div>
              )}
              {hasPermission('dashboard.view_hotels') && (
                <div className="space-y-1">
                  <Button
                    variant="ghost"
                    className="w-full justify-between"
                    onClick={() => setHotelDropdownOpen(!hotelDropdownOpen)}
                  >
                    <div className="flex items-center">
                      <Hotel className="h-4 w-4 mr-2" />
                      Hotel Management
                    </div>
                    {hotelDropdownOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  </Button>
                  {hotelDropdownOpen && (
                    <div className="ml-6 space-y-1">
                      <Button
                        variant={activeHotelTab === 'overview' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('hotel-management'); setActiveHotelTab('overview'); setSidebarOpen(false); }}
                      >
                        Overview
                      </Button>
                      <Button
                        variant={activeHotelTab === 'bookings' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('hotel-management'); setActiveHotelTab('bookings'); setSidebarOpen(false); }}
                      >
                        Bookings
                      </Button>
                      <Button
                        variant={activeHotelTab === 'payments' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('hotel-management'); setActiveHotelTab('payments'); setSidebarOpen(false); }}
                      >
                        Payments
                      </Button>
                      <Button
                        variant={activeHotelTab === 'hotels' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('hotel-management'); setActiveHotelTab('hotels'); setSidebarOpen(false); }}
                      >
                        Hotels
                      </Button>
                      <Button
                        variant={activeHotelTab === 'reviews' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('hotel-management'); setActiveHotelTab('reviews'); setSidebarOpen(false); }}
                      >
                        Reviews
                      </Button>
                    </div>
                  )}
                </div>
              )}
              {/* Notifications moved to Settings tab */}
              {/* {hasPermission('dashboard.view_notifications') && (
                <Button
                  variant={activeTab === 'notifications' ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => { setActiveTab('notifications'); setSidebarOpen(false); }}
                >
                  <Bell className="h-4 w-4 mr-2" />
                  Notifications
                </Button>
              )} */}
              {hasPermission('dashboard.view_settings') && (
                <div className="space-y-1">
                  <Button
                    variant="ghost"
                    className="w-full justify-between"
                    onClick={() => setSettingsDropdownOpen(!settingsDropdownOpen)}
                  >
                    <div className="flex items-center">
                      <Settings className="h-4 w-4 mr-2" />
                      Settings
                    </div>
                    {settingsDropdownOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  </Button>
                  {settingsDropdownOpen && (
                    <div className="ml-6 space-y-1">
                      <Button
                        variant={activeSettingsTab === 'general' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('settings'); setActiveSettingsTab('general'); setSidebarOpen(false); }}
                      >
                        General
                      </Button>
                      <Button
                        variant={activeSettingsTab === 'payment' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('settings'); setActiveSettingsTab('payment'); setSidebarOpen(false); }}
                      >
                        Payment Gateway
                      </Button>
                      <Button
                        variant={activeSettingsTab === 'bank-transfer' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('settings'); setActiveSettingsTab('bank-transfer'); setSidebarOpen(false); }}
                      >
                        Bank Transfer
                      </Button>
                      <Button
                        variant={activeSettingsTab === 'currency' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('settings'); setActiveSettingsTab('currency'); setSidebarOpen(false); }}
                      >
                        Currency
                      </Button>
                      <Button
                        variant={activeSettingsTab === 'notifications' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('settings'); setActiveSettingsTab('notifications'); setSidebarOpen(false); }}
                      >
                        Notifications
                      </Button>
                      <Button
                        variant={activeSettingsTab === 'security' ? 'default' : 'ghost'}
                        size="sm"
                        className="w-full justify-start text-sm"
                        onClick={() => { setActiveTab('settings'); setActiveSettingsTab('security'); setSidebarOpen(false); }}
                      >
                        Security
                      </Button>
                    </div>
                  )}
                </div>
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
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          <Button
            variant={activeTab === 'overview' ? 'default' : 'ghost'}
            className="w-full justify-start"
            onClick={() => setActiveTab('overview')}
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            Overview
          </Button>

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
            <div className="space-y-1">
              <Button
                variant="ghost"
                className="w-full justify-between"
                onClick={() => setCarDropdownOpen(!carDropdownOpen)}
              >
                <div className="flex items-center">
                  <Car className="h-4 w-4 mr-2" />
                  Car Management
                </div>
                {carDropdownOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
              </Button>
              {carDropdownOpen && (
                <div className="ml-6 space-y-1">
                  <Button
                    variant={activeCarTab === 'overview' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('car-management'); setActiveCarTab('overview'); }}
                  >
                    Overview
                  </Button>
                  <Button
                    variant={activeCarTab === 'bookings' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('car-management'); setActiveCarTab('bookings'); }}
                  >
                    Bookings
                  </Button>
                  <Button
                    variant={activeCarTab === 'payments' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('car-management'); setActiveCarTab('payments'); }}
                  >
                    Payments
                  </Button>
                  <Button
                    variant={activeCarTab === 'fleet' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('car-management'); setActiveCarTab('fleet'); }}
                  >
                    Fleet
                  </Button>
                  <Button
                    variant={activeCarTab === 'reviews' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('car-management'); setActiveCarTab('reviews'); }}
                  >
                    Reviews
                  </Button>
                  <Button
                    variant={activeCarTab === 'drivers' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('car-management'); setActiveCarTab('drivers'); }}
                  >
                    Drivers
                  </Button>
                </div>
              )}
            </div>
          )}
          {hasPermission('dashboard.view_hotels') && (
            <div className="space-y-1">
              <Button
                variant="ghost"
                className="w-full justify-between"
                onClick={() => setHotelDropdownOpen(!hotelDropdownOpen)}
              >
                <div className="flex items-center">
                  <Hotel className="h-4 w-4 mr-2" />
                  Hotel Management
                </div>
                {hotelDropdownOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
              </Button>
              {hotelDropdownOpen && (
                <div className="ml-6 space-y-1">
                  <Button
                    variant={activeHotelTab === 'overview' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('hotel-management'); setActiveHotelTab('overview'); }}
                  >
                    Overview
                  </Button>
                  <Button
                    variant={activeHotelTab === 'bookings' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('hotel-management'); setActiveHotelTab('bookings'); }}
                  >
                    Bookings
                  </Button>
                  <Button
                    variant={activeHotelTab === 'payments' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('hotel-management'); setActiveHotelTab('payments'); }}
                  >
                    Payments
                  </Button>
                  <Button
                    variant={activeHotelTab === 'hotels' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('hotel-management'); setActiveHotelTab('hotels'); }}
                  >
                    Hotels
                  </Button>
                  <Button
                    variant={activeHotelTab === 'reviews' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('hotel-management'); setActiveHotelTab('reviews'); }}
                  >
                    Reviews
                  </Button>
                </div>
              )}
            </div>
          )}
          {/* Notifications moved to Settings tab */}
          {/* {hasPermission('dashboard.view_notifications') && (
            <Button
              variant={activeTab === 'notifications' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setActiveTab('notifications')}
            >
              <Bell className="h-4 w-4 mr-2" />
              Notifications
            </Button>
          )} */}
          {hasPermission('dashboard.view_settings') && (
            <div className="space-y-1">
              <Button
                variant="ghost"
                className="w-full justify-between"
                onClick={() => setSettingsDropdownOpen(!settingsDropdownOpen)}
              >
                <div className="flex items-center">
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </div>
                {settingsDropdownOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
              </Button>
              {settingsDropdownOpen && (
                <div className="ml-6 space-y-1">
                  <Button
                    variant={activeSettingsTab === 'general' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('settings'); setActiveSettingsTab('general'); }}
                  >
                    General
                  </Button>
                  <Button
                    variant={activeSettingsTab === 'payment' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('settings'); setActiveSettingsTab('payment'); }}
                  >
                    Payment Gateway
                  </Button>
                  <Button
                    variant={activeSettingsTab === 'bank-transfer' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('settings'); setActiveSettingsTab('bank-transfer'); }}
                  >
                    Bank Transfer
                  </Button>
                  <Button
                    variant={activeSettingsTab === 'currency' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('settings'); setActiveSettingsTab('currency'); }}
                  >
                    Currency
                  </Button>
                  <Button
                    variant={activeSettingsTab === 'notifications' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('settings'); setActiveSettingsTab('notifications'); }}
                  >
                    Notifications
                  </Button>
                  <Button
                    variant={activeSettingsTab === 'security' ? 'default' : 'ghost'}
                    size="sm"
                    className="w-full justify-start text-sm"
                    onClick={() => { setActiveTab('settings'); setActiveSettingsTab('security'); }}
                  >
                    Security
                  </Button>
                </div>
              )}
            </div>
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
              <Card className="border-l-2 border-red-500 bg-red-50">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-red-800">Total Bookings</CardTitle>
                  <BarChart3 className="h-4 w-4 text-red-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-700">{stats.totalBookings}</div>
                  <p className={`text-xs ${stats.bookingChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {stats.bookingChange >= 0 ? '+' : ''}{stats.bookingChange}% from last month
                  </p>
                </CardContent>
              </Card>

              <Card className="border-l-2 border-blue-500 bg-blue-50">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-blue-800">Revenue</CardTitle>
                  <DollarSign className="h-4 w-4 text-blue-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-blue-700">
                    <PriceDisplay amount={stats.totalRevenue} currency="NGN" isNGNStored={true} />
                  </div>
                  <p className={`text-xs ${stats.revenueChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {stats.revenueChange >= 0 ? '+' : ''}{stats.revenueChange}% from last month
                  </p>
                </CardContent>
              </Card>



              <Card className="border-l-2 border-green-500 bg-green-50">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-green-800">Fleet Size</CardTitle>
                  <Car className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-700">{stats.fleetSize}</div>
                  <p className="text-xs text-gray-600">{stats.totalCars} Cars, {stats.totalHotels} Hotels</p>
                </CardContent>
              </Card>

              <Card className="border-l-2 border-purple-500 bg-purple-50">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-purple-800">Total Users</CardTitle>
                  <Users className="h-4 w-4 text-purple-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-purple-700">{stats.activeUsers}</div>
                  <p className="text-xs text-gray-600">Registered users</p>
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
                    <span>Car Fleet Overview</span>
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

                    </>
                  ) : (
                    <div className="animate-pulse space-y-4">
                      <div className="h-16 bg-gray-200 rounded-lg" />
                      <div className="h-6 bg-gray-200 rounded" />
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Hotel Management */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Hotel className="h-5 w-5" />
                    <span>Hotel Network Overview</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {stats ? (
                    <>
                      <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                        <div>
                          <h4 className="font-semibold">Hotels</h4>
                          <p className="text-gray-600">{stats.totalHotels} hotels in network</p>
                        </div>
                        <Badge className="bg-blue-100 text-blue-800">Active</Badge>
                      </div>

                    </>
                  ) : (
                    <div className="animate-pulse space-y-4">
                      <div className="h-16 bg-gray-200 rounded-lg" />
                      <div className="h-6 bg-gray-200 rounded" />
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
                ) : Array.isArray(recentActivity) && recentActivity.length > 0 ? (
                  <div className="space-y-4">
                    {(Array.isArray(recentActivity) ? recentActivity : []).map((activity) => {
                      if (!activity || typeof activity !== 'object') return null;
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
                        <div key={activity.id || Math.random()} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600">
                              {getActivityIcon(activity.type || 'default')}
                            </div>
                            <div>
                              <h4 className="font-medium text-sm">{activity.title || 'No title'}</h4>
                              <p className="text-xs text-gray-600">{activity.description || 'No description'}</p>
                              <p className="text-xs text-gray-500">
                                {activity.timestamp ? new Date(activity.timestamp).toLocaleString() : 'No date'}
                              </p>
                            </div>
                          </div>
                          <Badge className={getStatusColor(activity.status || 'unknown')}>
                            {activity.status || 'unknown'}
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



          {activeTab === 'users' && hasPermission('dashboard.view_users') && (
            <div className="space-y-6">
              <ErrorBoundary>
                <UserManagement />
              </ErrorBoundary>
            </div>
          )}

          {activeTab === 'hotel-bookings' && hasPermission('dashboard.view_bookings') && (
            <div className="space-y-6">
              <div>
                <h1 className="text-3xl font-bold mb-2">Hotel Bookings</h1>
                <p className="text-gray-600">Manage all hotel booking reservations</p>
              </div>
              <ErrorBoundary>
                <HotelBookingManagement />
              </ErrorBoundary>
            </div>
          )}

          {activeTab === 'car-bookings' && hasPermission('dashboard.view_bookings') && (
            <div className="space-y-6">
              <div>
                <h1 className="text-3xl font-bold mb-2">Car Bookings</h1>
                <p className="text-gray-600">Manage all car rental reservations</p>
              </div>
              <ErrorBoundary>
                <CarBookingManagement />
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
            <ErrorBoundary>
              <CarManagement />
            </ErrorBoundary>
          )}

          {activeTab === 'hotels' && hasPermission('dashboard.view_hotels') && (
            <ErrorBoundary>
              <HotelManagement />
            </ErrorBoundary>
          )}

          {activeTab === 'reviews' && hasPermission('dashboard.view_reviews') && (
            <ErrorBoundary>
              <ReviewManagement />
            </ErrorBoundary>
          )}

          {activeTab === 'support' && hasPermission('dashboard.view_support') && (
            <ErrorBoundary>
              <SupportTicketManagement />
            </ErrorBoundary>
          )}

          {/* Notifications moved to Settings tab */}
          {/* {activeTab === 'notifications' && hasPermission('dashboard.view_notifications') && (
            <div className="space-y-6">
              <ErrorBoundary>
                <NotificationSender />
              </ErrorBoundary>
              <ErrorBoundary>
                <NotificationCenter />
              </ErrorBoundary>
            </div>
          )} */}

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
                        {Array.isArray(rolePermissions) && rolePermissions.map((permission) => (
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
                        {Array.isArray(rolePermissions) && rolePermissions.filter(p => p && p.assigned).map((permission) => (
                          <Card key={permission.name} className="p-3 bg-blue-50 border-blue-200">
                            <div>
                              <h4 className="font-medium text-sm text-blue-800">{permission.name}</h4>
                              <p className="text-xs text-blue-600 mt-1">{permission.description}</p>
                              <p className="text-xs text-gray-500 mt-1">{permission.resource} • {permission.action}</p>
                            </div>
                          </Card>
                        ))}
                        {(!Array.isArray(rolePermissions) || rolePermissions.filter(p => p && p.assigned).length === 0) && (
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
                <h1 className="text-3xl font-bold mb-2">
                  {activeSettingsTab === 'general' && 'General Settings'}
                  {activeSettingsTab === 'payment' && 'Payment Gateway Settings'}
                  {activeSettingsTab === 'bank-transfer' && 'Bank Transfer Settings'}
                  {activeSettingsTab === 'currency' && 'Currency Settings'}
                  {activeSettingsTab === 'notifications' && 'Notification Settings'}
                  {activeSettingsTab === 'security' && 'Security Settings'}
                  {!activeSettingsTab && 'Admin Settings'}
                </h1>
                <p className="text-gray-600">
                  {activeSettingsTab === 'general' && 'Configure general system settings and preferences'}
                  {activeSettingsTab === 'payment' && 'Configure payment gateway integrations'}
                  {activeSettingsTab === 'bank-transfer' && 'Configure bank transfer payment options'}
                  {activeSettingsTab === 'currency' && 'Manage currency rates and exchange settings'}
                  {activeSettingsTab === 'notifications' && 'Configure email and push notification settings'}
                  {activeSettingsTab === 'security' && 'Configure security and authentication settings'}
                  {!activeSettingsTab && 'Configure system settings and preferences'}
                </p>
              </div>
              <ErrorBoundary>
                {activeSettingsTab === 'general' && <GeneralSettings />}
                {activeSettingsTab === 'payment' && <PaymentSettings />}
                {activeSettingsTab === 'bank-transfer' && <BankTransferSettings />}
                {activeSettingsTab === 'currency' && <CurrencySettings />}
                {activeSettingsTab === 'notifications' && <NotificationSettings />}
                {activeSettingsTab === 'security' && <SecuritySettings />}
                {!activeSettingsTab && <SettingsManagement />}
              </ErrorBoundary>
            </div>
          )}

          {activeTab === 'car-management' && hasPermission('dashboard.view_cars') && (
            <div className="space-y-6">
              <div>
                <h1 className="text-3xl font-bold mb-2">
                  {activeCarTab === 'overview' && 'Car Fleet Overview'}
                  {activeCarTab === 'bookings' && 'Car Bookings'}
                  {activeCarTab === 'payments' && 'Car Payments'}
                  {activeCarTab === 'fleet' && 'Fleet Management'}
                  {activeCarTab === 'reviews' && 'Car Reviews'}
                  {activeCarTab === 'drivers' && 'Driver Management'}
                  {!activeCarTab && 'Car Management'}
                </h1>
                <p className="text-gray-600">
                  {activeCarTab === 'overview' && 'Monitor car fleet performance and analytics'}
                  {activeCarTab === 'bookings' && 'Manage car rental reservations'}
                  {activeCarTab === 'payments' && 'Track car booking payments'}
                  {activeCarTab === 'fleet' && 'Manage your car fleet inventory'}
                  {activeCarTab === 'reviews' && 'Monitor and respond to car reviews'}
                  {activeCarTab === 'drivers' && 'Manage drivers and staff assignments'}
                  {!activeCarTab && 'Comprehensive car rental business management'}
                </p>
              </div>
              <ErrorBoundary>
                {activeCarTab === 'overview' && <CarFleetStats />}
                {activeCarTab === 'bookings' && <CarBookingManagement />}
                {activeCarTab === 'payments' && <PaymentManagement />}
                {activeCarTab === 'fleet' && <CarManagement />}
                {activeCarTab === 'reviews' && <ReviewManagement />}
                {activeCarTab === 'drivers' && <DriverManagement />}
                {!activeCarTab && <CarManagement />}
              </ErrorBoundary>
            </div>
          )}

          {activeTab === 'hotel-management' && hasPermission('dashboard.view_hotels') && (
            <div className="space-y-6">
              <div>
                <h1 className="text-3xl font-bold mb-2">
                  {activeHotelTab === 'overview' && 'Hotel Network Overview'}
                  {activeHotelTab === 'bookings' && 'Hotel Bookings'}
                  {activeHotelTab === 'payments' && 'Hotel Payments'}
                  {activeHotelTab === 'hotels' && 'Hotel Management'}
                  {activeHotelTab === 'reviews' && 'Hotel Reviews'}
                  {!activeHotelTab && 'Hotel Management'}
                </h1>
                <p className="text-gray-600">
                  {activeHotelTab === 'overview' && 'Monitor hotel network performance and analytics'}
                  {activeHotelTab === 'bookings' && 'Manage hotel reservations and check-ins'}
                  {activeHotelTab === 'payments' && 'Track hotel booking payments'}
                  {activeHotelTab === 'hotels' && 'Manage your hotel properties'}
                  {activeHotelTab === 'reviews' && 'Monitor and respond to hotel reviews'}
                  {!activeHotelTab && 'Comprehensive hotel business management'}
                </p>
              </div>
              <ErrorBoundary>
                {activeHotelTab === 'overview' && <HotelOverviewStats />}
                {activeHotelTab === 'bookings' && <HotelBookingManagement />}
                {activeHotelTab === 'payments' && <PaymentManagement />}
                {activeHotelTab === 'hotels' && <HotelManagement />}
                {activeHotelTab === 'reviews' && <ReviewManagement />}
                {!activeHotelTab && <HotelManagement />}
              </ErrorBoundary>
            </div>
          )}
        </div>
      </div>
      </div>
      <Toaster toasts={toasts} onDismiss={dismiss} />
    </div>
  );
};



export default AdminDashboard;
