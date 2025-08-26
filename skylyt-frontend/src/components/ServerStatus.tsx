import { useState, useEffect } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw, CheckCircle } from 'lucide-react';
import { apiService } from '@/services/api';

export const ServerStatus = () => {
  const [isOnline, setIsOnline] = useState(true);
  const [isChecking, setIsChecking] = useState(false);

  const checkServerStatus = async () => {
    setIsChecking(true);
    try {
      await fetch('https://skylytapi.scaleitpro.com/api/v1/health');
      setIsOnline(true);
    } catch (error) {
      setIsOnline(false);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkServerStatus();
    const interval = setInterval(checkServerStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  if (isOnline) {
    return null;
  }

  return (
    <Alert className="mb-4 border-red-200 bg-red-50">
      <AlertTriangle className="h-4 w-4 text-red-600" />
      <AlertDescription className="flex items-center justify-between">
        <span className="text-red-800">
          Backend server is not running. Please start the server to use the application.
        </span>
        <Button
          variant="outline"
          size="sm"
          onClick={checkServerStatus}
          disabled={isChecking}
          className="ml-4"
        >
          {isChecking ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <CheckCircle className="h-4 w-4" />
          )}
          {isChecking ? 'Checking...' : 'Retry'}
        </Button>
      </AlertDescription>
    </Alert>
  );
};