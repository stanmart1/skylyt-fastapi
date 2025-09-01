import React from 'react';
import { useCurrency } from '@/contexts/CurrencyContext';

interface PriceDisplayProps {
  amount: number;
  currency?: string;
  className?: string;
  showOriginal?: boolean;
  originalAmount?: number;
  originalCurrency?: string;
  isNGNStored?: boolean;
}

const PriceDisplay: React.FC<PriceDisplayProps> = ({
  amount,
  currency,
  className = '',
  showOriginal = false,
  originalAmount,
  originalCurrency,
  isNGNStored = false
}) => {
  const { formatPrice, convertAmount, currency: currentCurrency } = useCurrency();
  
  // If currency is provided and different from current currency, convert it
  // If isNGNStored is true, treat the amount as NGN regardless of currency param
  const fromCurrency = isNGNStored ? 'NGN' : (currency || currentCurrency);
  const convertedAmount = convertAmount(amount, fromCurrency);
  const formattedPrice = formatPrice(convertedAmount, currentCurrency);

  return (
    <span className={className}>
      <span className="font-semibold text-lg">{formattedPrice}</span>
      {showOriginal && originalAmount && originalCurrency && originalCurrency !== currentCurrency && (
        <span className="text-sm text-gray-500 ml-2">
          (was {formatPrice(originalAmount, originalCurrency)})
        </span>
      )}
    </span>
  );
};

export default PriceDisplay;