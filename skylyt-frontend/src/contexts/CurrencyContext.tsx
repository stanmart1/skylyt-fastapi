import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '@/services/api';

interface LocationData {
  country_code: string;
  country_name: string;
  city: string;
  currency: string;
  is_nigeria: boolean;
  is_supported_city: boolean;
}

interface CurrencyContextType {
  currency: string;
  location: LocationData | null;
  supportedCurrencies: string[];
  currencySymbols: Record<string, string>;
  setCurrency: (currency: string) => void;
  convertAmount: (amount: number, fromCurrency?: string) => number;
  formatPrice: (amount: number, currency?: string) => string;
  isLoading: boolean;
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

export const CurrencyProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currency, setCurrencyState] = useState<string>('NGN');
  const [location, setLocation] = useState<LocationData | null>(null);
  const [supportedCurrencies, setSupportedCurrencies] = useState<string[]>(['NGN', 'USD', 'GBP', 'EUR']);
  const [currencySymbols, setCurrencySymbols] = useState<Record<string, string>>({
    NGN: '₦', USD: '$', GBP: '£', EUR: '€'
  });
  const [exchangeRates, setExchangeRates] = useState<Record<string, number>>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    detectUserLocation();
  }, []);

  const detectUserLocation = async () => {
    try {
      const response = await apiService.request<{
        location: LocationData;
        supported_currencies: string[];
        currency_symbols: Record<string, string>;
      }>('/localization/detect');
      
      setLocation(response.location);
      setSupportedCurrencies(response.supported_currencies);
      setCurrencySymbols(response.currency_symbols);
      
      // Set currency from localStorage or detected location
      const savedCurrency = localStorage.getItem('preferred_currency');
      const detectedCurrency = response.location.currency;
      
      setCurrencyState(savedCurrency || detectedCurrency);
    } catch (error) {
      console.error('Failed to detect location:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const setCurrency = (newCurrency: string) => {
    setCurrencyState(newCurrency);
    localStorage.setItem('preferred_currency', newCurrency);
  };

  const convertAmount = (amount: number, fromCurrency: string = 'NGN'): number => {
    if (fromCurrency === currency) return amount;
    
    // Simple conversion logic - in production, use real-time rates
    const rates: Record<string, Record<string, number>> = {
      NGN: { USD: 0.0012, GBP: 0.001, EUR: 0.0011 },
      USD: { NGN: 830, GBP: 0.83, EUR: 0.92 },
      GBP: { NGN: 1000, USD: 1.2, EUR: 1.1 },
      EUR: { NGN: 910, USD: 1.08, GBP: 0.91 }
    };
    
    const rate = rates[fromCurrency]?.[currency] || 1;
    return amount * rate;
  };

  const formatPrice = (amount: number, curr: string = currency): string => {
    const symbol = currencySymbols[curr] || curr;
    return `${symbol}${amount.toLocaleString('en-US', { 
      minimumFractionDigits: 0,
      maximumFractionDigits: 2 
    })}`;
  };

  return (
    <CurrencyContext.Provider value={{
      currency,
      location,
      supportedCurrencies,
      currencySymbols,
      setCurrency,
      convertAmount,
      formatPrice,
      isLoading
    }}>
      {children}
    </CurrencyContext.Provider>
  );
};

export const useCurrency = () => {
  const context = useContext(CurrencyContext);
  if (!context) {
    throw new Error('useCurrency must be used within CurrencyProvider');
  }
  return context;
};