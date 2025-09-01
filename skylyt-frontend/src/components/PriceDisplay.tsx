import React from 'react';
import { useCurrency } from '@/contexts/CurrencyContext';

interface PriceDisplayProps {
  amount: number;
  currency?: string;
  className?: string;
  showOriginal?: boolean;
  originalAmount?: number;
  originalCurrency?: string;
}

const PriceDisplay: React.FC<PriceDisplayProps> = ({
  amount,
  currency,
  className = '',
  showOriginal = false,
  originalAmount,
  originalCurrency
}) => {
  const { formatPrice, currency: currentCurrency } = useCurrency();
  
  const displayCurrency = currency || currentCurrency;
  const formattedPrice = formatPrice(amount, displayCurrency);

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