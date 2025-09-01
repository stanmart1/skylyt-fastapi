import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Globe, Save } from 'lucide-react';
import { useSettings } from '@/contexts/SettingsContext';
import { useToast } from '@/hooks/use-toast';
import Navigation from '@/components/Navigation';

export const GeneralSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { updateSettings } = useSettings();
  const { toast } = useToast();

  const [generalForm, setGeneralForm] = useState({
    site_name: '',
    site_description: '',
    contact_email: '',
    contact_phone: '',
    maintenance_mode: false
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const { apiService } = await import('@/services/api');
      const data = await apiService.request('/settings/');
      
      setGeneralForm({
        site_name: data.site_name || '',
        site_description: data.site_description || '',
        contact_email: data.contact_email || '',
        contact_phone: data.contact_phone || '',
        maintenance_mode: data.maintenance_mode || false
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

  const saveGeneralSettings = async () => {
    setSaving(true);
    try {
      const { apiService } = await import('@/services/api');
      await apiService.request('/settings/general', {
        method: 'PUT',
        body: JSON.stringify(generalForm)
      });
      
      const updatedSettings = await apiService.request('/settings/');
      updateSettings(updatedSettings);
      
      toast({
        title: "Success",
        description: "General settings updated successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update general settings",
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
            <Globe className="h-5 w-5" />
            General Settings
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
          <h1 className="text-3xl font-bold mb-2">General Settings</h1>
          <p className="text-gray-600">Configure general system settings and preferences</p>
        </div>
        <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe className="h-5 w-5" />
          General Settings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div>
            <Label htmlFor="site_name">Site Name</Label>
            <Input
              id="site_name"
              value={generalForm.site_name}
              onChange={(e) => setGeneralForm({...generalForm, site_name: e.target.value})}
            />
          </div>
          
          <div>
            <Label htmlFor="site_description">Site Description</Label>
            <Textarea
              id="site_description"
              value={generalForm.site_description}
              onChange={(e) => setGeneralForm({...generalForm, site_description: e.target.value})}
              rows={3}
            />
          </div>
          
          <div>
            <Label htmlFor="contact_email">Contact Email</Label>
            <Input
              id="contact_email"
              type="email"
              value={generalForm.contact_email}
              onChange={(e) => setGeneralForm({...generalForm, contact_email: e.target.value})}
            />
          </div>
          
          <div>
            <Label htmlFor="contact_phone">Contact Phone</Label>
            <Input
              id="contact_phone"
              value={generalForm.contact_phone}
              onChange={(e) => setGeneralForm({...generalForm, contact_phone: e.target.value})}
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Switch
              id="maintenance_mode"
              checked={generalForm.maintenance_mode}
              onCheckedChange={(checked) => setGeneralForm({...generalForm, maintenance_mode: checked})}
            />
            <Label htmlFor="maintenance_mode">Maintenance Mode</Label>
          </div>
          
          <Button onClick={saveGeneralSettings} disabled={saving}>
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save General Settings'}
          </Button>
        </div>
      </CardContent>
        </Card>
      </div>
    </div>
  );
};