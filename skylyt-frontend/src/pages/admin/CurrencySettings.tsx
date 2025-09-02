import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Globe, Shield } from 'lucide-react';
import { CurrencyRateManagement } from '@/components/admin/CurrencyRateManagement';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { useAuth } from '@/contexts/AuthContext';

export const CurrencySettings = () => {
  const { hasPermission } = useAuth();
  
  if (!hasPermission('settings.view_currency')) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Currency Settings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">You don't have permission to view currency settings</p>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe className="h-5 w-5" />
          Currency Settings
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ErrorBoundary>
          <CurrencyRateManagement />
        </ErrorBoundary>
      </CardContent>
    </Card>
  );
};