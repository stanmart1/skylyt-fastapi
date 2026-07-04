import { useState, useEffect } from 'react';
import { apiService } from '@/services/api';

export interface PaymentGateway {
  id: string;
  name: string;
  description: string;
  configured: boolean;
}

export const usePaymentGateways = () => {
  const [gateways, setGateways] = useState<PaymentGateway[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAvailableGateways = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiService.request('/payment-config/gateways');
        if (response.success && response.gateways) {
          // Filter only configured gateways
          const configured = response.gateways.filter((g: PaymentGateway) => g.configured);
          setGateways(configured);
        } else {
          setGateways([]);
        }
      } catch (err) {
        console.error('Failed to fetch available payment gateways:', err);
        setError('Failed to load payment options');
        setGateways([]);
      } finally {
        setLoading(false);
      }
    };

    fetchAvailableGateways();
  }, []);

  return { gateways, loading, error };
};
