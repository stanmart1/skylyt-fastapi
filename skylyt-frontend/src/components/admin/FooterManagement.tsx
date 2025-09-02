import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/useToast';
import { apiService } from '@/services/api';
import { Settings, Save } from 'lucide-react';

interface FooterSettings {
  company_name: string;
  company_description: string;
  twitter_url: string;
  instagram_url: string;
  linkedin_url: string;
  contact_address: string;
  contact_phone: string;
  contact_email: string;
}

export const FooterManagement = () => {
  const [settings, setSettings] = useState<FooterSettings>({
    company_name: '',
    company_description: '',
    twitter_url: '',
    instagram_url: '',
    linkedin_url: '',
    contact_address: '',
    contact_phone: '',
    contact_email: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const data = await apiService.request('/admin/footer-settings');
      setSettings(data);
    } catch (error) {
      console.error('Failed to fetch footer settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to load footer settings',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await apiService.request('/admin/footer-settings', {
        method: 'PUT',
        body: JSON.stringify(settings)
      });
      
      toast({
        title: 'Success',
        description: 'Footer settings updated successfully',
        variant: 'default'
      });
    } catch (error) {
      console.error('Failed to update footer settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to update footer settings',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (field: keyof FooterSettings, value: string) => {
    setSettings(prev => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Footer Management
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-1/4" />
            <div className="h-10 bg-gray-200 rounded" />
            <div className="h-4 bg-gray-200 rounded w-1/4" />
            <div className="h-20 bg-gray-200 rounded" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Footer Management</h1>
          <p className="text-gray-600">Manage company information and contact details</p>
        </div>
        <Button onClick={handleSave} disabled={saving} className="flex items-center gap-2">
          <Save className="h-4 w-4" />
          {saving ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Company Information */}
        <Card>
          <CardHeader>
            <CardTitle>Company Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="company_name">Company Name</Label>
              <Input
                id="company_name"
                value={settings.company_name}
                onChange={(e) => handleInputChange('company_name', e.target.value)}
                placeholder="Skylyt Luxury"
              />
            </div>
            
            <div>
              <Label htmlFor="company_description">Company Description</Label>
              <Textarea
                id="company_description"
                value={settings.company_description}
                onChange={(e) => handleInputChange('company_description', e.target.value)}
                placeholder="Your perfect journey awaits..."
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="twitter_url">Twitter URL</Label>
              <Input
                id="twitter_url"
                value={settings.twitter_url}
                onChange={(e) => handleInputChange('twitter_url', e.target.value)}
                placeholder="https://twitter.com/skylytluxury"
              />
            </div>

            <div>
              <Label htmlFor="instagram_url">Instagram URL</Label>
              <Input
                id="instagram_url"
                value={settings.instagram_url}
                onChange={(e) => handleInputChange('instagram_url', e.target.value)}
                placeholder="https://instagram.com/skylytluxury"
              />
            </div>

            <div>
              <Label htmlFor="linkedin_url">LinkedIn URL</Label>
              <Input
                id="linkedin_url"
                value={settings.linkedin_url}
                onChange={(e) => handleInputChange('linkedin_url', e.target.value)}
                placeholder="https://linkedin.com/company/skylytluxury"
              />
            </div>
          </CardContent>
        </Card>

        {/* Contact Information */}
        <Card>
          <CardHeader>
            <CardTitle>Contact Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="contact_address">Address</Label>
              <Textarea
                id="contact_address"
                value={settings.contact_address}
                onChange={(e) => handleInputChange('contact_address', e.target.value)}
                placeholder="123 Business Ave, Suite 100&#10;New York, NY 10001"
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="contact_phone">Phone Number</Label>
              <Input
                id="contact_phone"
                value={settings.contact_phone}
                onChange={(e) => handleInputChange('contact_phone', e.target.value)}
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div>
              <Label htmlFor="contact_email">Email Address</Label>
              <Input
                id="contact_email"
                type="email"
                value={settings.contact_email}
                onChange={(e) => handleInputChange('contact_email', e.target.value)}
                placeholder="support@skylytluxury.com"
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};