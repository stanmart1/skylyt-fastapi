import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Skeleton } from '@/components/ui/skeleton';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Bell, Mail, Save, Shield } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { NotificationSender } from '@/components/admin/NotificationSender';
import { NotificationCenter } from '@/components/admin/NotificationCenter';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { useAuth } from '@/contexts/AuthContext';

export const NotificationSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();
  const { hasPermission } = useAuth();
  const [notificationForm, setNotificationForm] = useState({
    smtp_server: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    from_email: '',
    resend_api_key: '',
    email_notifications_enabled: true,
    sms_enabled: false,
    push_notifications_enabled: true,
    booking_notifications: true,
    payment_notifications: true,
    system_notifications: true,
    driver_notifications: true,
    admin_notifications: true,
    notification_frequency: 'immediate',
    quiet_hours_start: '22:00',
    quiet_hours_end: '08:00',
    timezone: 'UTC'
  });
  
  const canView = hasPermission('settings.view_notification_config');
  const canManage = hasPermission('settings.manage_notification_config');
  
  if (!canView) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notification Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">You don't have permission to view notification settings</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  useEffect(() => {
    // Defer API call to after initial render
    const timer = setTimeout(() => {
      fetchSettings();
    }, 0);
    
    return () => clearTimeout(timer);
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const { apiService } = await import('@/services/api');
      const data = await apiService.request('/settings/');
      
      // Remove console.log for production
      
      setNotificationForm({
        smtp_server: data.smtp_server || '',
        smtp_port: data.smtp_port || 587,
        smtp_username: data.smtp_username || '',
        smtp_password: '',
        from_email: data.from_email || '',
        resend_api_key: '',
        email_notifications_enabled: data.email_notifications_enabled ?? true,
        sms_enabled: data.sms_enabled ?? false,
        push_notifications_enabled: data.push_notifications_enabled ?? true,
        booking_notifications: data.booking_notifications ?? true,
        payment_notifications: data.payment_notifications ?? true,
        system_notifications: data.system_notifications ?? true,
        driver_notifications: data.driver_notifications ?? true,
        admin_notifications: data.admin_notifications ?? true,
        notification_frequency: data.notification_frequency || 'immediate',
        quiet_hours_start: data.quiet_hours_start || '22:00',
        quiet_hours_end: data.quiet_hours_end || '08:00',
        timezone: data.timezone || 'UTC'
      });
    } catch (error) {
      console.error('Failed to fetch settings:', error);
      toast({
        title: "Error",
        description: "Failed to load settings",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const saveNotificationSettings = async () => {
    if (saving) return;
    
    setSaving(true);
    try {
      const { apiService } = await import('@/services/api');
      
      // Only send non-empty password fields
      const dataToSend = { ...notificationForm };
      if (!dataToSend.smtp_password) delete dataToSend.smtp_password;
      if (!dataToSend.resend_api_key) delete dataToSend.resend_api_key;
      
      // Remove console.log for production
      
      const response = await apiService.request('/settings/notifications', {
        method: 'PUT',
        body: JSON.stringify(dataToSend)
      });
      
      // Remove console.log for production
      
      // Clear password fields after successful save
      setNotificationForm(prev => ({
        ...prev,
        smtp_password: '',
        resend_api_key: ''
      }));
      
      toast({
        title: "Success",
        description: "Notification settings saved successfully"
      });
      
      // Refresh settings to confirm save
      await fetchSettings();
      
    } catch (error) {
      console.error('Save error:', error);
      toast({
        title: "Error",
        description: error.message || "Failed to save notification settings",
        variant: "destructive"
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notification Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-6 w-48" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notification Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-6">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Mail className="h-5 w-5" />
                Email Settings
              </h3>
              <div>
                <Label htmlFor="smtp_server">SMTP Server</Label>
                <Input
                  id="smtp_server"
                  value={notificationForm.smtp_server}
                  onChange={(e) => setNotificationForm({...notificationForm, smtp_server: e.target.value})}
                  placeholder="smtp.gmail.com"
                  disabled={!canManage}
                />
              </div>
              <div>
                <Label htmlFor="smtp_port">SMTP Port</Label>
                <Input
                  id="smtp_port"
                  type="number"
                  value={notificationForm.smtp_port}
                  onChange={(e) => setNotificationForm({...notificationForm, smtp_port: Number(e.target.value) || 587})}
                  disabled={!canManage}
                />
              </div>
              <div>
                <Label htmlFor="smtp_username">SMTP Username</Label>
                <Input
                  id="smtp_username"
                  value={notificationForm.smtp_username}
                  onChange={(e) => setNotificationForm({...notificationForm, smtp_username: e.target.value})}
                  disabled={!canManage}
                />
              </div>
              <div>
                <Label htmlFor="smtp_password">SMTP Password</Label>
                <Input
                  id="smtp_password"
                  type="password"
                  value={notificationForm.smtp_password}
                  onChange={(e) => setNotificationForm({...notificationForm, smtp_password: e.target.value})}
                  placeholder="Enter to update"
                  disabled={!canManage}
                />
              </div>
              <div>
                <Label htmlFor="from_email">From Email</Label>
                <Input
                  id="from_email"
                  type="email"
                  value={notificationForm.from_email}
                  onChange={(e) => setNotificationForm({...notificationForm, from_email: e.target.value})}
                  disabled={!canManage}
                />
              </div>
              <div>
                <Label htmlFor="resend_api_key">Resend API Key</Label>
                <Input
                  id="resend_api_key"
                  type="password"
                  value={notificationForm.resend_api_key}
                  onChange={(e) => setNotificationForm({...notificationForm, resend_api_key: e.target.value})}
                  placeholder="Enter to update"
                  disabled={!canManage}
                />
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="email_notifications_enabled"
                  checked={notificationForm.email_notifications_enabled}
                  onCheckedChange={(checked) => setNotificationForm({...notificationForm, email_notifications_enabled: checked})}
                  disabled={!canManage}
                />
                <Label htmlFor="email_notifications_enabled">Enable Email Notifications</Label>
              </div>
            </div>

            {/* Notification Channels */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notification Channels
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="sms_enabled"
                    checked={notificationForm.sms_enabled}
                    onCheckedChange={(checked) => setNotificationForm({...notificationForm, sms_enabled: checked})}
                    disabled={!canManage}
                  />
                  <Label htmlFor="sms_enabled">SMS Notifications</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="push_notifications_enabled"
                    checked={notificationForm.push_notifications_enabled}
                    onCheckedChange={(checked) => setNotificationForm({...notificationForm, push_notifications_enabled: checked})}
                    disabled={!canManage}
                  />
                  <Label htmlFor="push_notifications_enabled">Push Notifications</Label>
                </div>
              </div>
            </div>

            {/* Event Types */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Event Types</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="booking_notifications"
                    checked={notificationForm.booking_notifications}
                    onCheckedChange={(checked) => setNotificationForm({...notificationForm, booking_notifications: checked})}
                    disabled={!canManage}
                  />
                  <Label htmlFor="booking_notifications">Booking Events</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="payment_notifications"
                    checked={notificationForm.payment_notifications}
                    onCheckedChange={(checked) => setNotificationForm({...notificationForm, payment_notifications: checked})}
                    disabled={!canManage}
                  />
                  <Label htmlFor="payment_notifications">Payment Events</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="system_notifications"
                    checked={notificationForm.system_notifications}
                    onCheckedChange={(checked) => setNotificationForm({...notificationForm, system_notifications: checked})}
                    disabled={!canManage}
                  />
                  <Label htmlFor="system_notifications">System Events</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="driver_notifications"
                    checked={notificationForm.driver_notifications}
                    onCheckedChange={(checked) => setNotificationForm({...notificationForm, driver_notifications: checked})}
                    disabled={!canManage}
                  />
                  <Label htmlFor="driver_notifications">Driver Events</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="admin_notifications"
                    checked={notificationForm.admin_notifications}
                    onCheckedChange={(checked) => setNotificationForm({...notificationForm, admin_notifications: checked})}
                    disabled={!canManage}
                  />
                  <Label htmlFor="admin_notifications">Admin Events</Label>
                </div>
              </div>
            </div>

            {/* Notification Preferences */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Notification Preferences</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="notification_frequency">Notification Frequency</Label>
                  <Select value={notificationForm.notification_frequency} onValueChange={(value) => setNotificationForm({...notificationForm, notification_frequency: value})} disabled={!canManage}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select frequency" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="immediate">Immediate</SelectItem>
                      <SelectItem value="hourly">Hourly Digest</SelectItem>
                      <SelectItem value="daily">Daily Digest</SelectItem>
                      <SelectItem value="weekly">Weekly Digest</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="timezone">Timezone</Label>
                  <Select value={notificationForm.timezone} onValueChange={(value) => setNotificationForm({...notificationForm, timezone: value})} disabled={!canManage}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select timezone" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="UTC">UTC</SelectItem>
                      <SelectItem value="Africa/Lagos">Africa/Lagos (WAT)</SelectItem>
                      <SelectItem value="America/New_York">America/New_York (EST)</SelectItem>
                      <SelectItem value="Europe/London">Europe/London (GMT)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="quiet_hours_start">Quiet Hours Start</Label>
                  <Input
                    id="quiet_hours_start"
                    type="time"
                    value={notificationForm.quiet_hours_start}
                    onChange={(e) => setNotificationForm({...notificationForm, quiet_hours_start: e.target.value})}
                    disabled={!canManage}
                  />
                </div>
                <div>
                  <Label htmlFor="quiet_hours_end">Quiet Hours End</Label>
                  <Input
                    id="quiet_hours_end"
                    type="time"
                    value={notificationForm.quiet_hours_end}
                    onChange={(e) => setNotificationForm({...notificationForm, quiet_hours_end: e.target.value})}
                    disabled={!canManage}
                  />
                </div>
              </div>
            </div>

            {canManage && (
              <Button onClick={saveNotificationSettings} disabled={saving || loading}>
                <Save className="h-4 w-4 mr-2" />
                {saving ? 'Saving...' : 'Save Notification Settings'}
              </Button>
            )}
            
            {!canManage && (
              <div className="text-sm text-gray-500 p-3 bg-gray-50 rounded-md">
                You don't have permission to modify notification settings. Contact your administrator for access.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Notification Management Section */}
      <Card>
        <CardHeader>
          <CardTitle>Notification Management</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Send Push Notification */}
          <div className="space-y-4">
            <h4 className="font-medium">Send Push Notification</h4>
            <ErrorBoundary>
              <NotificationSender />
            </ErrorBoundary>
          </div>
          
          {/* Notification Center */}
          <div className="space-y-4">
            <h4 className="font-medium">Notification Center</h4>
            <ErrorBoundary>
              <NotificationCenter />
            </ErrorBoundary>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};