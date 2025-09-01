import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Shield, Save } from 'lucide-react';
import { useSettings } from '@/contexts/SettingsContext';
import { useToast } from '@/hooks/use-toast';

export const SecuritySettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { updateSettings } = useSettings();
  const { toast } = useToast();

  const [securityForm, setSecurityForm] = useState({
    password_min_length: '8',
    session_timeout: '30',
    two_factor_enabled: false,
    login_attempts_limit: '5'
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
        login_attempts_limit: data.login_attempts_limit || '5'
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
              value={securityForm.password_min_length}
              onChange={(e) => setSecurityForm({...securityForm, password_min_length: e.target.value})}
            />
          </div>
          
          <div>
            <Label htmlFor="session_timeout">Session Timeout (minutes)</Label>
            <Input
              id="session_timeout"
              type="number"
              value={securityForm.session_timeout}
              onChange={(e) => setSecurityForm({...securityForm, session_timeout: e.target.value})}
            />
          </div>
          
          <div>
            <Label htmlFor="login_attempts_limit">Login Attempts Limit</Label>
            <Input
              id="login_attempts_limit"
              type="number"
              value={securityForm.login_attempts_limit}
              onChange={(e) => setSecurityForm({...securityForm, login_attempts_limit: e.target.value})}
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Switch
              id="two_factor_enabled"
              checked={securityForm.two_factor_enabled}
              onCheckedChange={(checked) => setSecurityForm({...securityForm, two_factor_enabled: checked})}
            />
            <Label htmlFor="two_factor_enabled">Enable Two-Factor Authentication</Label>
          </div>
          
          <Button onClick={saveSecuritySettings} disabled={saving}>
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save Security Settings'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};