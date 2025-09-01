import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Globe } from 'lucide-react';
import { CurrencyRateManagement } from '@/components/admin/CurrencyRateManagement';
import { ErrorBoundary } from '@/components/ErrorBoundary';

export const CurrencySettings = () => {
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