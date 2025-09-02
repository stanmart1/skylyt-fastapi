import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '@/services/api';

interface Currency {
  id: number;
  code: string;
  name: string;
  symbol: string;
  rate_to_ngn: number;
  is_active: boolean;
}

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
  currencies: Currency[];
  exchangeRates: Record<string, number>;
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

export const CurrencyProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currency, setCurrencyState] = useState<string>('NGN');
  const [location, setLocation] = useState<LocationData | null>(null);
  const [supportedCurrencies, setSupportedCurrencies] = useState<string[]>(['NGN', 'USD', 'GBP', 'EUR']);
  const [currencySymbols, setCurrencySymbols] = useState<Record<string, string>>({
    NGN: '₦', USD: '$', GBP: '£', EUR: '€'
  });
  const [currencies, setCurrencies] = useState<Currency[]>([]);
  const [exchangeRates, setExchangeRates] = useState<Record<string, number>>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadCurrencies();
    detectUserLocation();
    
    // Listen for currency rate updates
    const handleRatesUpdate = () => {
      loadCurrencies();
    };
    
    window.addEventListener('currencyRatesUpdated', handleRatesUpdate);
    
    return () => {
      window.removeEventListener('currencyRatesUpdated', handleRatesUpdate);
    };
  }, []);

  const loadCurrencies = async () => {
    try {
      const currencyData = await apiService.request<Currency[]>('/currencies');
      setCurrencies(currencyData);
      
      const symbols: Record<string, string> = {};
      const rates: Record<string, number> = {};
      const codes: string[] = [];
      
      currencyData.forEach(curr => {
        symbols[curr.code] = curr.symbol;
        rates[curr.code] = curr.rate_to_ngn;
        codes.push(curr.code);
      });
      
      setCurrencySymbols(symbols);
      setExchangeRates(rates);
      setSupportedCurrencies(codes);
    } catch (error) {
      console.error('Failed to load currencies:', error);
    }
  };

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
      
      // Set currency from localStorage or default to NGN
      const savedCurrency = localStorage.getItem('preferred_currency');
      
      setCurrencyState(savedCurrency || 'NGN');
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
    const safeAmount = typeof amount === 'number' && !isNaN(amount) ? amount : 0;
    if (fromCurrency === currency) return safeAmount;
    
    // Convert through NGN base currency
    let amountInNGN = safeAmount;
    if (fromCurrency !== 'NGN') {
      const fromRate = exchangeRates[fromCurrency] || 1;
      amountInNGN = safeAmount * fromRate;
    }
    
    if (currency === 'NGN') {
      return Math.round(amountInNGN * 100) / 100;
    }
    
    const toRate = exchangeRates[currency] || 1;
    return Math.round((amountInNGN / toRate) * 100) / 100;
  };

  const formatPrice = (amount: number, curr: string = currency): string => {
    const symbol = currencySymbols[curr] || curr;
    const safeAmount = typeof amount === 'number' && !isNaN(amount) ? amount : 0;
    return `${symbol}${safeAmount.toLocaleString('en-US', { 
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
      isLoading,
      currencies,
      exchangeRates
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