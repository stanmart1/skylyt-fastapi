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
  
  const fromCurrency = isNGNStored ? 'NGN' : (currency || 'NGN');
  const convertedAmount = convertAmount(amount, fromCurrency);
  const formattedPrice = formatPrice(convertedAmount, currentCurrency);

  return (
    <span className={className}>
      <span className="font-semibold text-lg">{formattedPrice}</span>
      {showOriginal && originalAmount && originalCurrency && originalCurrency !== displayCurrency && (
        <span className="text-sm text-gray-500 ml-2">
          (was {formatPrice(originalAmount, originalCurrency)})
        </span>
      )}
    </span>
  );
};

export default PriceDisplay;