import { useEffect, useState } from 'react';
import { useCurrency } from '@/contexts/CurrencyContext';
import { apiService } from '@/services/api';

export const useCurrencySearch = () => {
  const { currency } = useCurrency();
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    const handleCurrencyChange = () => {
      setRefreshTrigger(prev => prev + 1);
    };

    window.addEventListener('currencyChanged', handleCurrencyChange);
    return () => window.removeEventListener('currencyChanged', handleCurrencyChange);
  }, []);

  const searchHotels = async (params: any) => {
    return apiService.searchHotels({ ...params, currency });
  };

  const searchCars = async (params: any) => {
    return apiService.searchCars({ ...params, currency });
  };

  const getFeaturedHotels = async () => {
    return apiService.request(`/hotels/featured?currency=${currency}`);
  };

  const getFeaturedCars = async () => {
    return apiService.request(`/cars/featured?currency=${currency}`);
  };

  return {
    searchHotels,
    searchCars,
    getFeaturedHotels,
    getFeaturedCars,
    refreshTrigger,
    currency
  };
};