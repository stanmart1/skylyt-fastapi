import React, { useEffect } from 'react';
import { Globe, ChevronDown } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { useCurrency } from '@/contexts/CurrencyContext';

const CurrencySelector: React.FC = () => {
  const { currency, supportedCurrencies, currencySymbols, setCurrency, location, isLoading } = useCurrency();

  useEffect(() => {
    if (!isLoading && currency) {
      window.dispatchEvent(new CustomEvent('currencyChanged', { detail: { currency } }));
    }
  }, [currency, isLoading]);

  const countryFlags: Record<string, string> = {
    NGN: '🇳🇬',
    USD: '🇺🇸',
    GBP: '🇬🇧',
    EUR: '🇪🇺'
  };

  const currencyNames: Record<string, string> = {
    NGN: 'Nigerian Naira',
    USD: 'US Dollar',
    GBP: 'British Pound',
    EUR: 'Euro'
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Globe className="h-4 w-4" />
          <span className="hidden sm:inline">
            {countryFlags[currency]} {currencySymbols[currency]}
          </span>
          <span className="sm:hidden">{currency}</span>
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        {supportedCurrencies.map((curr) => (
          <DropdownMenuItem
            key={curr}
            onClick={() => setCurrency(curr)}
            className={`flex items-center gap-3 ${curr === currency ? 'bg-accent' : ''}`}
          >
            <span className="text-lg">{countryFlags[curr]}</span>
            <div className="flex flex-col">
              <span className="font-medium">{currencySymbols[curr]} {curr}</span>
              <span className="text-xs text-muted-foreground">{currencyNames[curr]}</span>
            </div>
            {curr === currency && (
              <span className="ml-auto text-xs text-primary">Current</span>
            )}
          </DropdownMenuItem>
        ))}
        {location?.is_nigeria && (
          <div className="px-2 py-1 text-xs text-muted-foreground border-t mt-1">
            📍 Detected: {location.city || location.country_name}
          </div>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default CurrencySelector;