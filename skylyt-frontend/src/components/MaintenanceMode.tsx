import { useSettings } from '@/contexts/SettingsContext';
import { Card, CardContent } from '@/components/ui/card';
import { Settings, Wrench } from 'lucide-react';

export const MaintenanceMode = ({ children }: { children: React.ReactNode }) => {
  const { settings, loading } = useSettings();

  if (loading) {
    return <div>{children}</div>;
  }

  if (settings?.maintenance_mode) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Wrench className="h-8 w-8 text-orange-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Under Maintenance</h1>
            <p className="text-gray-600 mb-4">
              {settings.site_name || 'Our system'} is currently undergoing maintenance. 
              We'll be back shortly!
            </p>
            <p className="text-sm text-gray-500">
              Thank you for your patience.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return <div>{children}</div>;
};