import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/useToast';
import { apiService } from '@/services/api';
import { Save } from 'lucide-react';

interface ContactSettings {
  page_title: string;
  page_description: string;
  contact_email: string;
  contact_phone: string;
  contact_address: string;
  office_hours: string;
}

export const ContactManagement = () => {
  const [settings, setSettings] = useState<ContactSettings>({
    page_title: '',
    page_description: '',
    contact_email: '',
    contact_phone: '',
    contact_address: '',
    office_hours: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const data = await apiService.request('/admin/contact-settings');
      setSettings(data);
    } catch (error) {
      console.error('Failed to fetch contact settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to load contact settings',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await apiService.request('/admin/contact-settings', {
        method: 'PUT',
        body: JSON.stringify(settings)
      });
      
      toast({
        title: 'Settings Saved Successfully',
        description: 'Contact page settings have been updated',
        variant: 'default'
      });
    } catch (error) {
      console.error('Failed to update contact settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to update contact settings',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (field: keyof ContactSettings, value: string) => {
    setSettings(prev => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-4 bg-gray-200 rounded w-1/4" />
        <div className="h-10 bg-gray-200 rounded" />
        <div className="h-4 bg-gray-200 rounded w-1/4" />
        <div className="h-20 bg-gray-200 rounded" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-end">
        <Button onClick={handleSave} disabled={saving} className="flex items-center gap-2">
          <Save className="h-4 w-4" />
          {saving ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Page Content */}
        <Card>
          <CardHeader>
            <CardTitle>Page Content</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="page_title">Page Title</Label>
              <Input
                id="page_title"
                value={settings.page_title}
                onChange={(e) => handleInputChange('page_title', e.target.value)}
                placeholder="Contact Us"
              />
            </div>
            
            <div>
              <Label htmlFor="page_description">Page Description</Label>
              <Textarea
                id="page_description"
                value={settings.page_description}
                onChange={(e) => handleInputChange('page_description', e.target.value)}
                placeholder="Get in touch with our team..."
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="office_hours">Office Hours</Label>
              <Textarea
                id="office_hours"
                value={settings.office_hours}
                onChange={(e) => handleInputChange('office_hours', e.target.value)}
                placeholder="Monday - Friday: 9:00 AM - 6:00 PM..."
                rows={4}
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
              <Label htmlFor="contact_email">Email Address</Label>
              <Input
                id="contact_email"
                type="email"
                value={settings.contact_email}
                onChange={(e) => handleInputChange('contact_email', e.target.value)}
                placeholder="support@skylytluxury.com"
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
              <Label htmlFor="contact_address">Address</Label>
              <Textarea
                id="contact_address"
                value={settings.contact_address}
                onChange={(e) => handleInputChange('contact_address', e.target.value)}
                placeholder="123 Business Ave, Suite 100&#10;New York, NY 10001"
                rows={3}
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};