import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Globe } from 'lucide-react';
import { CurrencyRateManagement } from '@/components/admin/CurrencyRateManagement';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import Navigation from '@/components/Navigation';

export const CurrencySettings = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Currency Settings</h1>
          <p className="text-gray-600">Manage currency rates and exchange settings</p>
        </div>
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
      </div>
    </div>
  );
};