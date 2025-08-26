import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CreditCard } from 'lucide-react';
import { usePayment } from '@/hooks/usePayment';

interface PayPalPaymentProps {
  amount: number;
  currency: string;
  bookingId: number;
  onSuccess: (payment: any) => void;
  onError: (error: string) => void;
}

export const PayPalPayment = ({ 
  amount, 
  currency, 
  bookingId, 
  onSuccess, 
  onError 
}: PayPalPaymentProps) => {
  const { isProcessing, processPayment } = usePayment();

  const handlePayment = async () => {
    try {
      const paymentData = {
        booking_id: bookingId,
        gateway: 'paypal',
        amount,
        currency,
        payment_method: 'paypal',
      };

      const result = await processPayment(paymentData);
      onSuccess(result);
    } catch (error) {
      onError('PayPal payment failed. Please try again.');
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="h-5 w-5" />
          PayPal Payment
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center space-y-4">
          <p className="text-gray-600">
            You will be redirected to PayPal to complete your payment securely.
          </p>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="font-semibold">Payment Summary</p>
            <p className="text-lg">{currency} {amount}</p>
          </div>

          <Button
            onClick={handlePayment}
            disabled={isProcessing}
            className="w-full bg-blue-500 hover:bg-blue-600"
          >
            {isProcessing ? 'Redirecting...' : `Pay with PayPal`}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};