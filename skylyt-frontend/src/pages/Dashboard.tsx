
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import { 
  Calendar, 
  User, 
  Settings,
  LogOut,
  Heart,
  Eye,
  EyeOff,
  TrendingUp,
  DollarSign,
  Clock,
  Star,
  Bell,
  AlertCircle,
  Info,
  CheckCircle2,
  XCircle
} from 'lucide-react';
import Navigation from '@/components/Navigation';
import { useAuth } from '@/contexts/AuthContext';
import { ProfileManager } from '@/components/profile/ProfileManager';
import { BookingHistory } from '@/components/booking/BookingHistory';
import { FavoritesManager } from '@/components/favorites/FavoritesManager';
import { apiService } from '@/services/api';
import PriceDisplay from '@/components/PriceDisplay';
import { useToast } from '@/hooks/use-toast';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const { user, logout } = useAuth();
  const { toast } = useToast();
  const [notifications, setNotifications] = useState({
    email: true,
    sms: false
  });
  const [passwordModalOpen, setPasswordModalOpen] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [saving, setSaving] = useState(false);
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  const [userStats, setUserStats] = useState({
    total_bookings: 0,
    active_bookings: 0,
    total_spent: 0,
    upcoming_bookings: 0,
    total_favorites: 0
  });
  const [statsLoading, setStatsLoading] = useState(true);
  const [userNotifications, setUserNotifications] = useState([]);
  const [notificationsLoading, setNotificationsLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const handleLogout = () => {
    toast({
      title: "Logging out...",
      description: "You are being signed out of your account.",
    });
    logout();
  };

  const handleNotificationChange = (type: 'email' | 'sms', checked: boolean) => {
    const updatedNotifications = { ...notifications, [type]: checked };
    setNotifications(updatedNotifications);
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      await apiService.request('/users/me/notifications', {
        method: 'PUT',
        body: JSON.stringify(notifications)
      });
      toast({
        title: "Settings saved!",
        description: "Your notification preferences have been updated.",
      });
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast({
        title: "Failed to save settings",
        description: "Please try again later.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = async () => {
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      toast({
        title: "Password mismatch",
        description: "New passwords do not match.",
        variant: "destructive",
      });
      return;
    }

    setSaving(true);
    try {
      await apiService.changePassword({
        current_password: passwordForm.currentPassword,
        new_password: passwordForm.newPassword
      });
      
      toast({
        title: "Password changed!",
        description: "Your password has been updated successfully.",
      });
      setPasswordModalOpen(false);
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error) {
      console.error('Failed to change password:', error);
      toast({
        title: "Failed to change password",
        description: "Please check your current password and try again.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const fetchUserNotifications = async () => {
    setNotificationsLoading(true);
    try {
      const response = await apiService.request('/notifications');
      setUserNotifications(response || []);
      setUnreadCount(response?.filter(n => !n.is_read).length || 0);
    } catch (error) {
      console.error('Failed to load user notifications:', error);
    } finally {
      setNotificationsLoading(false);
    }
  };

  const handleMarkNotificationAsRead = async (notificationId) => {
    try {
      await apiService.request(`/notifications/${notificationId}/read`, {
        method: 'PUT'
      });
      await fetchUserNotifications();
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const handleMarkAllNotificationsAsRead = async () => {
    try {
      await apiService.request('/notifications/mark-all-read', {
        method: 'PUT'
      });
      await fetchUserNotifications();
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'warning': return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'error': return <XCircle className="h-4 w-4 text-red-500" />;
      default: return <Info className="h-4 w-4 text-blue-500" />;
    }
  };

  // Load user notification preferences and stats on mount
  useEffect(() => {
    const loadNotifications = async () => {
      try {
        const response = await apiService.request('/users/me/notifications');
        setNotifications(response);
      } catch (error) {
        console.error('Failed to load notifications:', error);
      }
    };
    
    const loadUserStats = async () => {
      try {
        const response = await apiService.request('/users/me/stats');
        setUserStats(response);
      } catch (error) {
        console.error('Failed to load user stats:', error);
      } finally {
        setStatsLoading(false);
      }
    };
    
    if (user) {
      loadNotifications();
      loadUserStats();
      fetchUserNotifications();
    }
  }, [user]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24">
              <CardHeader className="text-center">
                <div className="w-20 h-20 bg-gradient-to-r from-blue-600 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <User className="h-10 w-10 text-white" />
                </div>
                <CardTitle className="text-xl">{user?.full_name || 'User'}</CardTitle>
                <p className="text-gray-600">{user?.email}</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Button
                    variant={activeTab === 'overview' ? 'default' : 'ghost'}
                    className="w-full justify-start"
                    onClick={() => setActiveTab('overview')}
                  >
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Overview
                  </Button>
                  <Button
                    variant={activeTab === 'bookings' ? 'default' : 'ghost'}
                    className="w-full justify-start"
                    onClick={() => setActiveTab('bookings')}
                  >
                    <Calendar className="h-4 w-4 mr-2" />
                    My Bookings
                  </Button>
                  <Button
                    variant={activeTab === 'profile' ? 'default' : 'ghost'}
                    className="w-full justify-start"
                    onClick={() => setActiveTab('profile')}
                  >
                    <User className="h-4 w-4 mr-2" />
                    Profile
                  </Button>
                  <Button
                    variant={activeTab === 'favorites' ? 'default' : 'ghost'}
                    className="w-full justify-start"
                    onClick={() => setActiveTab('favorites')}
                  >
                    <Heart className="h-4 w-4 mr-2" />
                    Favorites
                  </Button>
                  <Button
                    variant={activeTab === 'notifications' ? 'default' : 'ghost'}
                    className="w-full justify-start"
                    onClick={() => setActiveTab('notifications')}
                  >
                    <Bell className="h-4 w-4 mr-2" />
                    Notifications
                    {unreadCount > 0 && (
                      <span className="ml-auto bg-red-500 text-white text-xs rounded-full px-2 py-1">
                        {unreadCount}
                      </span>
                    )}
                  </Button>
                  <Button
                    variant={activeTab === 'settings' ? 'default' : 'ghost'}
                    className="w-full justify-start"
                    onClick={() => setActiveTab('settings')}
                  >
                    <Settings className="h-4 w-4 mr-2" />
                    Settings
                  </Button>
                  <Button 
                    variant="ghost" 
                    className="w-full justify-start text-red-600 hover:text-red-700"
                    onClick={handleLogout}
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div>
                  <h1 className="text-3xl font-bold mb-2">Dashboard Overview</h1>
                  <p className="text-gray-600">Your travel activity at a glance</p>
                </div>
                
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-600">Total Bookings</p>
                          <p className="text-2xl font-bold">
                            {statsLoading ? '...' : userStats.total_bookings}
                          </p>
                        </div>
                        <Calendar className="h-8 w-8 text-blue-600" />
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-600">Active Bookings</p>
                          <p className="text-2xl font-bold">
                            {statsLoading ? '...' : userStats.active_bookings}
                          </p>
                        </div>
                        <Clock className="h-8 w-8 text-green-600" />
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-600">Total Spent</p>
                          <p className="text-2xl font-bold">
                            {statsLoading ? '...' : <PriceDisplay amount={userStats.total_spent} currency="NGN" isNGNStored={true} />}
                          </p>
                        </div>
                        <DollarSign className="h-8 w-8 text-orange-600" />
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-600">Favorites</p>
                          <p className="text-2xl font-bold">
                            {statsLoading ? '...' : userStats.total_favorites}
                          </p>
                        </div>
                        <Star className="h-8 w-8 text-red-600" />
                      </div>
                    </CardContent>
                  </Card>
                </div>
                
                {/* Quick Actions */}
                <Card>
                  <CardHeader>
                    <CardTitle>Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <Button 
                        variant="outline" 
                        className="h-20 flex-col"
                        onClick={() => setActiveTab('bookings')}
                      >
                        <Calendar className="h-6 w-6 mb-2" />
                        View Bookings
                      </Button>
                      <Button 
                        variant="outline" 
                        className="h-20 flex-col"
                        onClick={() => window.location.href = '/cars'}
                      >
                        <TrendingUp className="h-6 w-6 mb-2" />
                        Book a Car
                      </Button>
                      <Button 
                        variant="outline" 
                        className="h-20 flex-col"
                        onClick={() => window.location.href = '/hotels'}
                      >
                        <Heart className="h-6 w-6 mb-2" />
                        Book a Hotel
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
            
            {activeTab === 'bookings' && (
              <div className="space-y-6">
                <div>
                  <h1 className="text-3xl font-bold mb-2">My Bookings</h1>
                  <p className="text-gray-600">Manage your travel bookings</p>
                </div>
                <BookingHistory />
              </div>
            )}

            {activeTab === 'profile' && (
              <div className="space-y-6">
                <div>
                  <h1 className="text-3xl font-bold mb-2">Profile Settings</h1>
                  <p className="text-gray-600">Manage your personal information</p>
                </div>
                <ProfileManager />
              </div>
            )}

            {activeTab === 'favorites' && (
              <div className="space-y-6">
                <div>
                  <h1 className="text-3xl font-bold mb-2">My Favorites</h1>
                  <p className="text-gray-600">Your saved hotels and cars</p>
                </div>
                <FavoritesManager />
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <div>
                  <h1 className="text-3xl font-bold mb-2">Notifications</h1>
                  <p className="text-gray-600">View and manage your notifications</p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="flex items-center gap-2">
                        <Bell className="h-5 w-5" />
                        Your Notifications
                        {unreadCount > 0 && (
                          <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1">
                            {unreadCount} unread
                          </span>
                        )}
                      </span>
                      {unreadCount > 0 && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handleMarkAllNotificationsAsRead}
                        >
                          Mark All Read
                        </Button>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {notificationsLoading ? (
                      <div className="space-y-3">
                        {[...Array(3)].map((_, i) => (
                          <div key={i} className="animate-pulse h-16 bg-gray-200 rounded" />
                        ))}
                      </div>
                    ) : userNotifications.length === 0 ? (
                      <div className="text-center py-8">
                        <Bell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-600">No notifications yet</p>
                      </div>
                    ) : (
                      <div className="space-y-3 max-h-96 overflow-y-auto">
                        {userNotifications.map((notification) => (
                          <div
                            key={notification.id}
                            className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                              notification.is_read 
                                ? 'bg-gray-50 border-gray-200' 
                                : 'bg-blue-50 border-blue-200'
                            }`}
                            onClick={() => !notification.is_read && handleMarkNotificationAsRead(notification.id)}
                          >
                            <div className="flex items-start gap-3">
                              {getNotificationIcon(notification.type)}
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between">
                                  <h4 className={`text-sm font-medium ${
                                    notification.is_read ? 'text-gray-700' : 'text-gray-900'
                                  }`}>
                                    {notification.title}
                                  </h4>
                                  <span className="text-xs text-gray-500">
                                    {new Date(notification.created_at).toLocaleDateString()}
                                  </span>
                                </div>
                                <p className={`text-sm mt-1 ${
                                  notification.is_read ? 'text-gray-600' : 'text-gray-800'
                                }`}>
                                  {notification.message}
                                </p>
                              </div>
                              {!notification.is_read && (
                                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="space-y-6">
                <div>
                  <h1 className="text-3xl font-bold mb-2">Account Settings</h1>
                  <p className="text-gray-600">Manage your account preferences</p>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle>Notifications</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium">Email Notifications</h4>
                        <p className="text-sm text-gray-600">Receive booking confirmations and updates</p>
                      </div>
                      <Switch 
                        checked={notifications.email}
                        onCheckedChange={(checked) => handleNotificationChange('email', checked)}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium">SMS Notifications</h4>
                        <p className="text-sm text-gray-600">Get text alerts for your bookings</p>
                      </div>
                      <Switch 
                        checked={notifications.sms}
                        onCheckedChange={(checked) => handleNotificationChange('sms', checked)}
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Security</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Button 
                      variant="outline" 
                      className="w-full justify-start"
                      onClick={() => setPasswordModalOpen(true)}
                    >
                      Change Password
                    </Button>
                    <Button 
                      onClick={handleSaveSettings}
                      disabled={saving}
                      className="w-full"
                    >
                      {saving ? 'Saving...' : 'Save Settings'}
                    </Button>
                  </CardContent>
                </Card>

                {/* Password Change Modal */}
                <Dialog open={passwordModalOpen} onOpenChange={setPasswordModalOpen}>
                  <DialogContent className="max-w-md">
                    <DialogHeader>
                      <DialogTitle>Change Password</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="currentPassword">Current Password</Label>
                        <div className="relative">
                          <Input 
                            id="currentPassword" 
                            type={showPasswords.current ? 'text' : 'password'}
                            value={passwordForm.currentPassword}
                            onChange={(e) => setPasswordForm({...passwordForm, currentPassword: e.target.value})}
                            className="pr-10"
                          />
                          <button
                            type="button"
                            onClick={() => setShowPasswords({...showPasswords, current: !showPasswords.current})}
                            className="absolute right-3 top-3 text-gray-500 hover:text-gray-700"
                          >
                            {showPasswords.current ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </button>
                        </div>
                      </div>
                      <div>
                        <Label htmlFor="newPassword">New Password</Label>
                        <div className="relative">
                          <Input 
                            id="newPassword" 
                            type={showPasswords.new ? 'text' : 'password'}
                            value={passwordForm.newPassword}
                            onChange={(e) => setPasswordForm({...passwordForm, newPassword: e.target.value})}
                            className="pr-10"
                          />
                          <button
                            type="button"
                            onClick={() => setShowPasswords({...showPasswords, new: !showPasswords.new})}
                            className="absolute right-3 top-3 text-gray-500 hover:text-gray-700"
                          >
                            {showPasswords.new ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </button>
                        </div>
                      </div>
                      <div>
                        <Label htmlFor="confirmPassword">Confirm New Password</Label>
                        <div className="relative">
                          <Input 
                            id="confirmPassword" 
                            type={showPasswords.confirm ? 'text' : 'password'}
                            value={passwordForm.confirmPassword}
                            onChange={(e) => setPasswordForm({...passwordForm, confirmPassword: e.target.value})}
                            className="pr-10"
                          />
                          <button
                            type="button"
                            onClick={() => setShowPasswords({...showPasswords, confirm: !showPasswords.confirm})}
                            className="absolute right-3 top-3 text-gray-500 hover:text-gray-700"
                          >
                            {showPasswords.confirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </button>
                        </div>
                      </div>
                      <div className="flex gap-2 pt-4">
                        <Button 
                          onClick={handlePasswordChange}
                          disabled={saving || !passwordForm.currentPassword || !passwordForm.newPassword || passwordForm.newPassword !== passwordForm.confirmPassword}
                        >
                          {saving ? 'Changing...' : 'Change Password'}
                        </Button>
                        <Button variant="outline" onClick={() => setPasswordModalOpen(false)}>Cancel</Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
