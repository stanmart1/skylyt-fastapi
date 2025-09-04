import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
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

  const [notificationForm, setNotificationForm] = useState({
    smtp_server: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    from_email: '',
    resend_api_key: '',
    onesignal_app_id: '',
    onesignal_api_key: '',
    email_notifications_enabled: true,
    push_notifications_enabled: true
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const { apiService } = await import('@/services/api');
      const data = await apiService.request('/settings/');
      
      setNotificationForm({
        smtp_server: data.smtp_server || '',
        smtp_port: data.smtp_port || 587,
        smtp_username: data.smtp_username || '',
        smtp_password: '',
        from_email: data.from_email || '',
        resend_api_key: '',
        onesignal_app_id: data.onesignal_app_id || '',
        onesignal_api_key: '',
        email_notifications_enabled: data.email_notifications_enabled ?? true,
        push_notifications_enabled: data.push_notifications_enabled ?? true
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
    setSaving(true);
    try {
      const { apiService } = await import('@/services/api');
      const response = await apiService.request('/settings/notifications', {
        method: 'PUT',
        body: JSON.stringify(notificationForm)
      });
      
      // Update form with saved values
      if (response.settings) {
        setNotificationForm(prev => ({
          ...prev,
          ...response.settings,
          smtp_password: '',
          resend_api_key: '',
          onesignal_api_key: ''
        }));
      }
      
      toast({
        title: "Success",
        description: "Notification settings updated successfully"
      });
    } catch (error) {
      console.error('Save error:', error);
      toast({
        title: "Error",
        description: "Failed to update notification settings",
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
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="animate-pulse h-16 bg-gray-200 rounded" />
            ))}
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
                  onChange={(e) => setNotificationForm({...notificationForm, smtp_port: parseInt(e.target.value)})}
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

            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Push Notification Settings
              </h3>
              <div>
                <Label htmlFor="onesignal_app_id">OneSignal App ID</Label>
                <Input
                  id="onesignal_app_id"
                  value={notificationForm.onesignal_app_id}
                  onChange={(e) => setNotificationForm({...notificationForm, onesignal_app_id: e.target.value})}
                  disabled={!canManage}
                />
              </div>
              <div>
                <Label htmlFor="onesignal_api_key">OneSignal API Key</Label>
                <Input
                  id="onesignal_api_key"
                  type="password"
                  value={notificationForm.onesignal_api_key}
                  onChange={(e) => setNotificationForm({...notificationForm, onesignal_api_key: e.target.value})}
                  placeholder="Enter to update"
                  disabled={!canManage}
                />
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="push_notifications_enabled"
                  checked={notificationForm.push_notifications_enabled}
                  onCheckedChange={(checked) => setNotificationForm({...notificationForm, push_notifications_enabled: checked})}
                  disabled={!canManage}
                />
                <Label htmlFor="push_notifications_enabled">Enable Push Notifications</Label>
              </div>
            </div>

            {canManage && (
              <Button onClick={saveNotificationSettings} disabled={saving}>
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