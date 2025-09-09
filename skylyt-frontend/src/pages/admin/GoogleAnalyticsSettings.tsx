import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { BarChart3, Save, Shield } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

export const GoogleAnalyticsSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { hasPermission } = useAuth();
  const { toast } = useToast();
  
  const canManage = hasPermission('settings.manage_google_analytics');

  const [analyticsForm, setAnalyticsForm] = useState({
    google_analytics_tracking_id: '',
    google_analytics_measurement_id: '',
    google_analytics_api_key: '',
    google_analytics_enabled: false
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const { apiService } = await import('@/services/api');
      const data = await apiService.request('/settings/');
      
      setAnalyticsForm({
        google_analytics_tracking_id: data.google_analytics_tracking_id || '',
        google_analytics_measurement_id: data.google_analytics_measurement_id || '',
        google_analytics_api_key: '',
        google_analytics_enabled: data.google_analytics_enabled || false
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

  const saveAnalyticsSettings = async () => {
    setSaving(true);
    try {
      const { apiService } = await import('@/services/api');
      await apiService.request('/settings/google-analytics', {
        method: 'PUT',
        body: JSON.stringify(analyticsForm)
      });
      
      toast({
        title: "Success",
        description: "Google Analytics settings updated successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update Google Analytics settings",
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
            <BarChart3 className="h-5 w-5" />
            Google Analytics Settings
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

  if (!hasPermission('settings.view_google_analytics')) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Google Analytics Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">You don't have permission to view Google Analytics settings</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Google Analytics Settings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <Switch
              id="google_analytics_enabled"
              checked={analyticsForm.google_analytics_enabled}
              onCheckedChange={(checked) => setAnalyticsForm({...analyticsForm, google_analytics_enabled: checked})}
              disabled={!canManage}
            />
            <Label htmlFor="google_analytics_enabled">Enable Google Analytics</Label>
          </div>
          
          <div>
            <Label htmlFor="google_analytics_tracking_id">Tracking ID (GA4)</Label>
            <Input
              id="google_analytics_tracking_id"
              value={analyticsForm.google_analytics_tracking_id}
              onChange={(e) => setAnalyticsForm({...analyticsForm, google_analytics_tracking_id: e.target.value})}
              placeholder="G-XXXXXXXXXX"
              disabled={!canManage}
            />
            <p className="text-xs text-gray-500 mt-1">Your Google Analytics 4 property ID</p>
          </div>
          
          <div>
            <Label htmlFor="google_analytics_measurement_id">Measurement ID</Label>
            <Input
              id="google_analytics_measurement_id"
              value={analyticsForm.google_analytics_measurement_id}
              onChange={(e) => setAnalyticsForm({...analyticsForm, google_analytics_measurement_id: e.target.value})}
              placeholder="G-XXXXXXXXXX"
              disabled={!canManage}
            />
            <p className="text-xs text-gray-500 mt-1">Your GA4 measurement ID for enhanced tracking</p>
          </div>
          
          <div>
            <Label htmlFor="google_analytics_api_key">API Key (Optional)</Label>
            <Input
              id="google_analytics_api_key"
              type="password"
              value={analyticsForm.google_analytics_api_key}
              onChange={(e) => setAnalyticsForm({...analyticsForm, google_analytics_api_key: e.target.value})}
              placeholder="Enter API key for reporting access"
              disabled={!canManage}
            />
            <p className="text-xs text-gray-500 mt-1">Required for server-side analytics reporting</p>
          </div>
          
          {canManage && (
            <Button onClick={saveAnalyticsSettings} disabled={saving}>
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Google Analytics Settings'}
            </Button>
          )}
          
          {!canManage && (
            <div className="text-sm text-gray-500 p-3 bg-gray-50 rounded-md">
              You don't have permission to modify Google Analytics settings. Contact your administrator for access.
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};