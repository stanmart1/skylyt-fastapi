import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Car, Hotel } from 'lucide-react';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/useToast';

interface ModuleSettings {
  car_rental_enabled: boolean;
  hotel_booking_enabled: boolean;
}

export const ModuleManagement = () => {
  const [settings, setSettings] = useState<ModuleSettings>({
    car_rental_enabled: true,
    hotel_booking_enabled: true
  });
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    fetchModuleSettings();
  }, []);

  const fetchModuleSettings = async () => {
    try {
      const response = await apiService.request('/admin/module-settings');
      setSettings(response);
    } catch (error) {
      console.error('Failed to fetch module settings:', error);
      toast({
        title: 'Error',
        description: 'Failed to load module settings',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const updateModuleSetting = async (module: keyof ModuleSettings, enabled: boolean) => {
    setUpdating(module);
    try {
      await apiService.request('/admin/module-settings', {
        method: 'PUT',
        body: JSON.stringify({ [module]: enabled })
      });
      
      setSettings(prev => ({ ...prev, [module]: enabled }));
      
      // Refresh features context to update navigation
      window.location.reload();
      
      toast({
        title: 'Success',
        description: `${module === 'car_rental_enabled' ? 'Car Rental' : 'Hotel Booking'} ${enabled ? 'enabled' : 'disabled'} successfully`,
        variant: 'success'
      });
    } catch (error) {
      console.error('Failed to update module setting:', error);
      toast({
        title: 'Error',
        description: 'Failed to update module setting',
        variant: 'error'
      });
    } finally {
      setUpdating(null);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[1, 2].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Car className="h-5 w-5 text-blue-600" />
              <span>Car Rental Module</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="car-rental-toggle" className="text-sm font-medium">
                Enable Car Rental Service
              </Label>
              <Switch
                id="car-rental-toggle"
                checked={settings.car_rental_enabled}
                onCheckedChange={(checked) => updateModuleSetting('car_rental_enabled', checked)}
                disabled={updating === 'car_rental_enabled'}
              />
            </div>
            <p className="text-sm text-gray-600">
              {settings.car_rental_enabled 
                ? 'Car rental bookings are currently active and available to customers'
                : 'Car rental service is disabled. Customers cannot make new car bookings'
              }
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Hotel className="h-5 w-5 text-green-600" />
              <span>Hotel Booking Module</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="hotel-booking-toggle" className="text-sm font-medium">
                Enable Hotel Booking Service
              </Label>
              <Switch
                id="hotel-booking-toggle"
                checked={settings.hotel_booking_enabled}
                onCheckedChange={(checked) => updateModuleSetting('hotel_booking_enabled', checked)}
                disabled={updating === 'hotel_booking_enabled'}
              />
            </div>
            <p className="text-sm text-gray-600">
              {settings.hotel_booking_enabled 
                ? 'Hotel bookings are currently active and available to customers'
                : 'Hotel booking service is disabled. Customers cannot make new hotel reservations'
              }
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};