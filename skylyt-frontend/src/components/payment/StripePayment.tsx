import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { CreditCard } from 'lucide-react';
import { usePayment } from '@/hooks/usePayment';

interface StripePaymentProps {
  amount: number;
  currency: string;
  bookingId: number;
  onSuccess: (payment: any) => void;
  onError: (error: string) => void;
}

export const StripePayment = ({ 
  amount, 
  currency, 
  bookingId, 
  onSuccess, 
  onError 
}: StripePaymentProps) => {
  const [cardData, setCardData] = useState({
    cardNumber: '',
    expiryDate: '',
    cvv: '',
    cardName: '',
  });

  const { isProcessing, processPayment } = usePayment();

  const handleInputChange = (field: string, value: string) => {
    setCardData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const paymentData = {
        booking_id: bookingId,
        gateway: 'stripe',
        amount,
        currency,
        payment_method: 'card',
        card_details: cardData,
      };

      const result = await processPayment(paymentData);
      onSuccess(result);
    } catch (error) {
      onError('Payment failed. Please check your card details and try again.');
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="h-5 w-5" />
          Card Payment
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="cardName">Cardholder Name</Label>
            <Input
              id="cardName"
              value={cardData.cardName}
              onChange={(e) => handleInputChange('cardName', e.target.value)}
              placeholder="John Doe"
              required
            />
          </div>

          <div>
            <Label htmlFor="cardNumber">Card Number</Label>
            <Input
              id="cardNumber"
              value={cardData.cardNumber}
              onChange={(e) => handleInputChange('cardNumber', e.target.value)}
              placeholder="1234 5678 9012 3456"
              maxLength={19}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="expiryDate">Expiry Date</Label>
              <Input
                id="expiryDate"
                value={cardData.expiryDate}
                onChange={(e) => handleInputChange('expiryDate', e.target.value)}
                placeholder="MM/YY"
                maxLength={5}
                required
              />
            </div>
            <div>
              <Label htmlFor="cvv">CVV</Label>
              <Input
                id="cvv"
                value={cardData.cvv}
                onChange={(e) => handleInputChange('cvv', e.target.value)}
                placeholder="123"
                maxLength={4}
                required
              />
            </div>
          </div>

          <div className="pt-4">
            <Button
              type="submit"
              disabled={isProcessing}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {isProcessing ? 'Processing...' : `Pay ${currency} ${amount}`}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};