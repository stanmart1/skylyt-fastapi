import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CreditCard } from 'lucide-react';
import { usePayment } from '@/hooks/usePayment';

interface PaystackPaymentProps {
  amount: number;
  currency: string;
  bookingId: number;
  onSuccess: (payment: any) => void;
  onError: (error: string) => void;
}

export const PaystackPayment = ({ 
  amount, 
  currency, 
  bookingId, 
  onSuccess, 
  onError 
}: PaystackPaymentProps) => {
  const { isProcessing, processPayment } = usePayment();

  const handlePayment = async () => {
    try {
      const paymentData = {
        booking_id: bookingId,
        gateway: 'paystack',
        amount,
        currency,
        payment_method: 'paystack',
      };

      const result = await processPayment(paymentData);
      onSuccess(result);
    } catch (error) {
      onError('Paystack payment failed. Please try again.');
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="h-5 w-5" />
          Paystack Payment
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center space-y-4">
          <p className="text-gray-600">
            You will be redirected to Paystack to complete your payment securely.
          </p>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="font-semibold">Payment Summary</p>
            <p className="text-lg">{currency} {amount}</p>
          </div>

          <Button
            onClick={handlePayment}
            disabled={isProcessing}
            className="w-full bg-green-600 hover:bg-green-700"
          >
            {isProcessing ? 'Redirecting...' : `Pay with Paystack`}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};