import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Shield, Save } from 'lucide-react';
import { useSettings } from '@/contexts/SettingsContext';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';

export const SecuritySettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { updateSettings } = useSettings();
  const { toast } = useToast();
  const { hasPermission } = useAuth();
  
  const canView = hasPermission('settings.view_security');
  const canManage = hasPermission('settings.manage_security');
  
  if (!canView) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Security Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">You don't have permission to view security settings</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const [securityForm, setSecurityForm] = useState({
    password_min_length: '8',
    session_timeout: '30',
    two_factor_enabled: false,
    login_attempts_limit: '5',
    general_rate_limit_enabled: true,
    general_rate_limit_requests: '100',
    general_rate_limit_window: '60',
    auth_rate_limit_enabled: true,
    auth_rate_limit_requests: '5',
    auth_rate_limit_window: '60',
    booking_rate_limit_enabled: true,
    booking_rate_limit_requests: '20',
    booking_rate_limit_window: '60',
    admin_rate_limit_enabled: true,
    admin_rate_limit_requests: '30',
    admin_rate_limit_window: '600'
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const { apiService } = await import('@/services/api');
      const data = await apiService.request('/settings/');
      
      setSecurityForm({
        password_min_length: data.password_min_length || '8',
        session_timeout: data.session_timeout || '30',
        two_factor_enabled: data.two_factor_enabled || false,
        login_attempts_limit: data.login_attempts_limit || '5',
        general_rate_limit_enabled: data.general_rate_limit_enabled ?? true,
        general_rate_limit_requests: data.general_rate_limit_requests || '100',
        general_rate_limit_window: data.general_rate_limit_window || '60',
        auth_rate_limit_enabled: data.auth_rate_limit_enabled ?? true,
        auth_rate_limit_requests: data.auth_rate_limit_requests || '5',
        auth_rate_limit_window: data.auth_rate_limit_window || '60',
        booking_rate_limit_enabled: data.booking_rate_limit_enabled ?? true,
        booking_rate_limit_requests: data.booking_rate_limit_requests || '20',
        booking_rate_limit_window: data.booking_rate_limit_window || '60',
        admin_rate_limit_enabled: data.admin_rate_limit_enabled ?? true,
        admin_rate_limit_requests: data.admin_rate_limit_requests || '30',
        admin_rate_limit_window: data.admin_rate_limit_window || '600'
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

  const saveSecuritySettings = async () => {
    setSaving(true);
    try {
      const { apiService } = await import('@/services/api');
      await apiService.request('/settings/security', {
        method: 'PUT',
        body: JSON.stringify(securityForm)
      });
      
      const updatedSettings = await apiService.request('/settings/');
      updateSettings(updatedSettings);
      
      toast({
        title: "Success",
        description: "Security settings updated successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update security settings",
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
            <Shield className="h-5 w-5" />
            Security Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="animate-pulse h-16 bg-gray-200 rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5" />
          Security Settings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div>
            <Label htmlFor="password_min_length">Minimum Password Length</Label>
            <Input
              id="password_min_length"
              type="number"
              min="6"
              max="50"
              value={securityForm.password_min_length}
              onChange={(e) => setSecurityForm({...securityForm, password_min_length: e.target.value})}
              disabled={!canManage}
            />
          </div>
          
          <div>
            <Label htmlFor="session_timeout">Session Timeout (minutes)</Label>
            <Input
              id="session_timeout"
              type="number"
              min="5"
              max="1440"
              value={securityForm.session_timeout}
              onChange={(e) => setSecurityForm({...securityForm, session_timeout: e.target.value})}
              disabled={!canManage}
            />
          </div>
          
          <div>
            <Label htmlFor="login_attempts_limit">Login Attempts Limit</Label>
            <Input
              id="login_attempts_limit"
              type="number"
              min="1"
              max="20"
              value={securityForm.login_attempts_limit}
              onChange={(e) => setSecurityForm({...securityForm, login_attempts_limit: e.target.value})}
              disabled={!canManage}
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Switch
              id="two_factor_enabled"
              checked={securityForm.two_factor_enabled}
              onCheckedChange={(checked) => setSecurityForm({...securityForm, two_factor_enabled: checked})}
              disabled={!canManage}
            />
            <Label htmlFor="two_factor_enabled">Enable Two-Factor Authentication</Label>
          </div>
          
          <div className="space-y-6 border-t pt-4">
            <h3 className="text-lg font-semibold">API Rate Limiting</h3>
            
            {/* General Browsing/Search */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Switch
                  id="general_rate_limit_enabled"
                  checked={securityForm.general_rate_limit_enabled}
                  onCheckedChange={(checked) => setSecurityForm({...securityForm, general_rate_limit_enabled: checked})}
                  disabled={!canManage}
                />
                <Label htmlFor="general_rate_limit_enabled">General Browsing/Search</Label>
              </div>
              {securityForm.general_rate_limit_enabled && (
                <div className="grid grid-cols-2 gap-4 ml-6">
                  <div>
                    <Label>Requests</Label>
                    <Input
                      type="number"
                      value={securityForm.general_rate_limit_requests}
                      onChange={(e) => setSecurityForm({...securityForm, general_rate_limit_requests: e.target.value})}
                      disabled={!canManage}
                    />
                  </div>
                  <div>
                    <Label>Window (seconds)</Label>
                    <Input
                      type="number"
                      value={securityForm.general_rate_limit_window}
                      onChange={(e) => setSecurityForm({...securityForm, general_rate_limit_window: e.target.value})}
                      disabled={!canManage}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Authentication */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Switch
                  id="auth_rate_limit_enabled"
                  checked={securityForm.auth_rate_limit_enabled}
                  onCheckedChange={(checked) => setSecurityForm({...securityForm, auth_rate_limit_enabled: checked})}
                  disabled={!canManage}
                />
                <Label htmlFor="auth_rate_limit_enabled">Authentication</Label>
              </div>
              {securityForm.auth_rate_limit_enabled && (
                <div className="grid grid-cols-2 gap-4 ml-6">
                  <div>
                    <Label>Requests</Label>
                    <Input
                      type="number"
                      value={securityForm.auth_rate_limit_requests}
                      onChange={(e) => setSecurityForm({...securityForm, auth_rate_limit_requests: e.target.value})}
                      disabled={!canManage}
                    />
                  </div>
                  <div>
                    <Label>Window (seconds)</Label>
                    <Input
                      type="number"
                      value={securityForm.auth_rate_limit_window}
                      onChange={(e) => setSecurityForm({...securityForm, auth_rate_limit_window: e.target.value})}
                      disabled={!canManage}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Booking/Payment */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Switch
                  id="booking_rate_limit_enabled"
                  checked={securityForm.booking_rate_limit_enabled}
                  onCheckedChange={(checked) => setSecurityForm({...securityForm, booking_rate_limit_enabled: checked})}
                  disabled={!canManage}
                />
                <Label htmlFor="booking_rate_limit_enabled">Booking/Payment</Label>
              </div>
              {securityForm.booking_rate_limit_enabled && (
                <div className="grid grid-cols-2 gap-4 ml-6">
                  <div>
                    <Label>Requests</Label>
                    <Input
                      type="number"
                      value={securityForm.booking_rate_limit_requests}
                      onChange={(e) => setSecurityForm({...securityForm, booking_rate_limit_requests: e.target.value})}
                      disabled={!canManage}
                    />
                  </div>
                  <div>
                    <Label>Window (seconds)</Label>
                    <Input
                      type="number"
                      value={securityForm.booking_rate_limit_window}
                      onChange={(e) => setSecurityForm({...securityForm, booking_rate_limit_window: e.target.value})}
                      disabled={!canManage}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Admin/Management */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Switch
                  id="admin_rate_limit_enabled"
                  checked={securityForm.admin_rate_limit_enabled}
                  onCheckedChange={(checked) => setSecurityForm({...securityForm, admin_rate_limit_enabled: checked})}
                  disabled={!canManage}
                />
                <Label htmlFor="admin_rate_limit_enabled">Admin/Management</Label>
              </div>
              {securityForm.admin_rate_limit_enabled && (
                <div className="grid grid-cols-2 gap-4 ml-6">
                  <div>
                    <Label>Requests</Label>
                    <Input
                      type="number"
                      value={securityForm.admin_rate_limit_requests}
                      onChange={(e) => setSecurityForm({...securityForm, admin_rate_limit_requests: e.target.value})}
                      disabled={!canManage}
                    />
                  </div>
                  <div>
                    <Label>Window (seconds)</Label>
                    <Input
                      type="number"
                      value={securityForm.admin_rate_limit_window}
                      onChange={(e) => setSecurityForm({...securityForm, admin_rate_limit_window: e.target.value})}
                      disabled={!canManage}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {canManage && (
            <Button onClick={saveSecuritySettings} disabled={saving}>
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Security Settings'}
            </Button>
          )}
          
          {!canManage && (
            <div className="text-sm text-gray-500 p-3 bg-gray-50 rounded-md">
              You don't have permission to modify security settings. Contact your administrator for access.
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};