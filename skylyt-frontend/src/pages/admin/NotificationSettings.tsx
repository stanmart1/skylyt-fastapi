import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Bell, Mail, Save } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { NotificationSender } from '@/components/admin/NotificationSender';
import { NotificationCenter } from '@/components/admin/NotificationCenter';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import Navigation from '@/components/Navigation';

export const NotificationSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

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
      await apiService.request('/settings/notifications', {
        method: 'PUT',
        body: JSON.stringify(notificationForm)
      });
      
      toast({
        title: "Success",
        description: "Notification settings updated successfully"
      });
    } catch (error) {
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
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Notification Settings</h1>
          <p className="text-gray-600">Configure email and push notification settings</p>
        </div>
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
                />
              </div>
              <div>
                <Label htmlFor="smtp_port">SMTP Port</Label>
                <Input
                  id="smtp_port"
                  type="number"
                  value={notificationForm.smtp_port}
                  onChange={(e) => setNotificationForm({...notificationForm, smtp_port: parseInt(e.target.value)})}
                />
              </div>
              <div>
                <Label htmlFor="smtp_username">SMTP Username</Label>
                <Input
                  id="smtp_username"
                  value={notificationForm.smtp_username}
                  onChange={(e) => setNotificationForm({...notificationForm, smtp_username: e.target.value})}
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
                />
              </div>
              <div>
                <Label htmlFor="from_email">From Email</Label>
                <Input
                  id="from_email"
                  type="email"
                  value={notificationForm.from_email}
                  onChange={(e) => setNotificationForm({...notificationForm, from_email: e.target.value})}
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
                />
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="email_notifications_enabled"
                  checked={notificationForm.email_notifications_enabled}
                  onCheckedChange={(checked) => setNotificationForm({...notificationForm, email_notifications_enabled: checked})}
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
                />
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="push_notifications_enabled"
                  checked={notificationForm.push_notifications_enabled}
                  onCheckedChange={(checked) => setNotificationForm({...notificationForm, push_notifications_enabled: checked})}
                />
                <Label htmlFor="push_notifications_enabled">Enable Push Notifications</Label>
              </div>
            </div>

            <Button onClick={saveNotificationSettings} disabled={saving}>
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Notification Settings'}
            </Button>
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
      </div>
    </div>
  );
};