import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Settings, Save, Shield } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

export const FeatureSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { hasPermission } = useAuth();
  const { toast } = useToast();
  
  const canManage = hasPermission('settings.manage_features');

  const [featureForm, setFeatureForm] = useState({
    car_rental_enabled: true,
    hotel_booking_enabled: true,
    driver_service_enabled: true,
    multi_currency_enabled: true,
    reviews_enabled: true,
    loyalty_program_enabled: false,
    referral_program_enabled: false,
    chat_support_enabled: true,
    mobile_app_enabled: false,
    api_access_enabled: false,
    booking_modifications_enabled: true,
    cancellation_enabled: true,
    partial_payments_enabled: false,
    group_bookings_enabled: false,
    corporate_accounts_enabled: false,
    maintenance_notifications: true,
    feature_announcements: true,
    beta_features_enabled: false
  });

  const handleFieldChange = useCallback((field, value) => {
    setFeatureForm(prev => ({ ...prev, [field]: value }));
  }, []);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const { apiService } = await import('@/services/api');
      const data = await apiService.request('/settings/features');
      
      setFeatureForm({
        car_rental_enabled: data.car_rental_enabled ?? true,
        hotel_booking_enabled: data.hotel_booking_enabled ?? true,
        driver_service_enabled: data.driver_service_enabled ?? true,
        multi_currency_enabled: data.multi_currency_enabled ?? true,
        reviews_enabled: data.reviews_enabled ?? true,
        loyalty_program_enabled: data.loyalty_program_enabled ?? false,
        referral_program_enabled: data.referral_program_enabled ?? false,
        chat_support_enabled: data.chat_support_enabled ?? true,
        mobile_app_enabled: data.mobile_app_enabled ?? false,
        api_access_enabled: data.api_access_enabled ?? false,
        booking_modifications_enabled: data.booking_modifications_enabled ?? true,
        cancellation_enabled: data.cancellation_enabled ?? true,
        partial_payments_enabled: data.partial_payments_enabled ?? false,
        group_bookings_enabled: data.group_bookings_enabled ?? false,
        corporate_accounts_enabled: data.corporate_accounts_enabled ?? false,
        maintenance_notifications: data.maintenance_notifications ?? true,
        feature_announcements: data.feature_announcements ?? true,
        beta_features_enabled: data.beta_features_enabled ?? false
      });
    } catch (error) {
      console.error('Failed to fetch feature settings:', error);
      toast({
        title: "Error",
        description: "Failed to load feature settings",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const saveFeatureSettings = async () => {
    setSaving(true);
    try {
      const { apiService } = await import('@/services/api');
      await apiService.request('/settings/features', {
        method: 'PUT',
        body: JSON.stringify(featureForm)
      });
      
      toast({
        title: "Success",
        description: "Feature settings updated successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || "Failed to update feature settings",
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
            <Settings className="h-5 w-5" />
            Feature Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="animate-pulse h-16 bg-gray-200 rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!hasPermission('settings.view_features')) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Feature Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">You don't have permission to view feature settings</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Feature Settings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-6">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Core Services</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <Switch
                  id="car_rental_enabled"
                  checked={featureForm.car_rental_enabled}
                  onCheckedChange={(checked) => handleFieldChange('car_rental_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="car_rental_enabled">Car Rental Service</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="hotel_booking_enabled"
                  checked={featureForm.hotel_booking_enabled}
                  onCheckedChange={(checked) => handleFieldChange('hotel_booking_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="hotel_booking_enabled">Hotel Booking Service</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="driver_service_enabled"
                  checked={featureForm.driver_service_enabled}
                  onCheckedChange={(checked) => handleFieldChange('driver_service_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="driver_service_enabled">Driver Service</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="multi_currency_enabled"
                  checked={featureForm.multi_currency_enabled}
                  onCheckedChange={(checked) => handleFieldChange('multi_currency_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="multi_currency_enabled">Multi-Currency Support</Label>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Customer Features</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <Switch
                  id="reviews_enabled"
                  checked={featureForm.reviews_enabled}
                  onCheckedChange={(checked) => handleFieldChange('reviews_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="reviews_enabled">Customer Reviews</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="loyalty_program_enabled"
                  checked={featureForm.loyalty_program_enabled}
                  onCheckedChange={(checked) => handleFieldChange('loyalty_program_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="loyalty_program_enabled">Loyalty Program</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="referral_program_enabled"
                  checked={featureForm.referral_program_enabled}
                  onCheckedChange={(checked) => handleFieldChange('referral_program_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="referral_program_enabled">Referral Program</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="chat_support_enabled"
                  checked={featureForm.chat_support_enabled}
                  onCheckedChange={(checked) => handleFieldChange('chat_support_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="chat_support_enabled">Live Chat Support</Label>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Booking Features</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <Switch
                  id="booking_modifications_enabled"
                  checked={featureForm.booking_modifications_enabled}
                  onCheckedChange={(checked) => handleFieldChange('booking_modifications_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="booking_modifications_enabled">Booking Modifications</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="cancellation_enabled"
                  checked={featureForm.cancellation_enabled}
                  onCheckedChange={(checked) => handleFieldChange('cancellation_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="cancellation_enabled">Booking Cancellation</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="partial_payments_enabled"
                  checked={featureForm.partial_payments_enabled}
                  onCheckedChange={(checked) => handleFieldChange('partial_payments_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="partial_payments_enabled">Partial Payments</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="group_bookings_enabled"
                  checked={featureForm.group_bookings_enabled}
                  onCheckedChange={(checked) => handleFieldChange('group_bookings_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="group_bookings_enabled">Group Bookings</Label>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Advanced Features</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <Switch
                  id="corporate_accounts_enabled"
                  checked={featureForm.corporate_accounts_enabled}
                  onCheckedChange={(checked) => handleFieldChange('corporate_accounts_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="corporate_accounts_enabled">Corporate Accounts</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="mobile_app_enabled"
                  checked={featureForm.mobile_app_enabled}
                  onCheckedChange={(checked) => handleFieldChange('mobile_app_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="mobile_app_enabled">Mobile App Access</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="api_access_enabled"
                  checked={featureForm.api_access_enabled}
                  onCheckedChange={(checked) => handleFieldChange('api_access_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="api_access_enabled">API Access</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="beta_features_enabled"
                  checked={featureForm.beta_features_enabled}
                  onCheckedChange={(checked) => handleFieldChange('beta_features_enabled', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="beta_features_enabled">Beta Features</Label>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">System Notifications</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <Switch
                  id="maintenance_notifications"
                  checked={featureForm.maintenance_notifications}
                  onCheckedChange={(checked) => handleFieldChange('maintenance_notifications', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="maintenance_notifications">Maintenance Notifications</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="feature_announcements"
                  checked={featureForm.feature_announcements}
                  onCheckedChange={(checked) => handleFieldChange('feature_announcements', checked)}
                  disabled={!canManage}
                />
                <Label htmlFor="feature_announcements">Feature Announcements</Label>
              </div>
            </div>
          </div>

          {canManage && (
            <Button onClick={saveFeatureSettings} disabled={saving}>
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Save Feature Settings'}
            </Button>
          )}
          
          {!canManage && (
            <div className="text-sm text-gray-500 p-3 bg-gray-50 rounded-md">
              You don't have permission to modify feature settings. Contact your administrator for access.
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};