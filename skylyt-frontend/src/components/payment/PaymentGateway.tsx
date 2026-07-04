import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { CreditCard, Building2, Smartphone, Upload } from 'lucide-react';
import { PAYMENT_GATEWAYS } from '@/utils/constants';
import { StripePayment } from './StripePayment';
import { FlutterwavePayment } from './FlutterwavePayment';
import { PaystackPayment } from './PaystackPayment';
import { PayPalPayment } from './PayPalPayment';
import { BankTransferUpload } from './BankTransferUpload';
import { apiService } from '@/services/api';

interface PaymentGatewayProps {
  amount: number;
  currency: string;
  bookingId: number;
  onSuccess: (payment: any) => void;
  onError: (error: string) => void;
}

export const PaymentGateway = ({ 
  amount, 
  currency, 
  bookingId, 
  onSuccess, 
  onError 
}: PaymentGatewayProps) => {
  const [selectedGateway, setSelectedGateway] = useState(PAYMENT_GATEWAYS.STRIPE);
  const [availableGateways, setAvailableGateways] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const allGateways = [
    {
      id: PAYMENT_GATEWAYS.STRIPE,
      name: 'Credit/Debit Card',
      description: 'Pay with Visa, Mastercard, or American Express',
      icon: CreditCard,
      component: StripePayment,
    },
    {
      id: PAYMENT_GATEWAYS.FLUTTERWAVE,
      name: 'Flutterwave',
      description: 'Pay with mobile money, bank transfer, or card',
      icon: Smartphone,
      component: FlutterwavePayment,
    },
    {
      id: PAYMENT_GATEWAYS.PAYSTACK,
      name: 'Paystack',
      description: 'Pay with card, bank transfer, or USSD',
      icon: CreditCard,
      component: PaystackPayment,
    },
    {
      id: PAYMENT_GATEWAYS.PAYPAL,
      name: 'PayPal',
      description: 'Pay with your PayPal account',
      icon: CreditCard,
      component: PayPalPayment,
    },
    {
      id: PAYMENT_GATEWAYS.BANK_TRANSFER,
      name: 'Bank Transfer',
      description: 'Pay via bank transfer and upload proof',
      icon: Building2,
      component: BankTransferUpload,
    },
  ];

  useEffect(() => {
    const fetchAvailableGateways = async () => {
      try {
        const response = await apiService.request('/payment-config/gateways');
        if (response.success && response.gateways) {
          // Filter only configured gateways
          const configured = response.gateways.filter((g: any) => g.configured);
          setAvailableGateways(configured);
          
          // Set default to first available gateway if current selection is not available
          if (configured.length > 0 && !configured.find((g: any) => g.id === selectedGateway)) {
            setSelectedGateway(configured[0].id);
          }
        }
      } catch (error) {
        console.error('Failed to fetch available gateways:', error);
        // Fallback to all gateways if API fails
        setAvailableGateways(allGateways);
      } finally {
        setLoading(false);
      }
    };

    fetchAvailableGateways();
  }, [selectedGateway]);

  // Filter gateways to show only configured ones
  const gateways = allGateways.filter(gateway => 
    availableGateways.find(ag => ag.id === gateway.id)
  );

  const selectedGatewayConfig = gateways.find(g => g.id === selectedGateway);
  const PaymentComponent = selectedGatewayConfig?.component;

  if (loading) {
    return <div className="text-center py-8">Loading payment options...</div>;
  }

  if (gateways.length === 0) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-gray-600">
            No payment gateways are currently configured. Please contact support.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Gateway Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Choose Payment Method
          </CardTitle>
        </CardHeader>
        <CardContent>
          <RadioGroup value={selectedGateway} onValueChange={setSelectedGateway}>
            <div className="space-y-3">
              {gateways.map((gateway) => {
                const Icon = gateway.icon;
                return (
                  <div key={gateway.id} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50">
                    <RadioGroupItem value={gateway.id} id={gateway.id} />
                    <Icon className="h-5 w-5 text-gray-600" />
                    <div className="flex-1">
                      <Label htmlFor={gateway.id} className="font-medium cursor-pointer">
                        {gateway.name}
                      </Label>
                      <p className="text-sm text-gray-600">{gateway.description}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </RadioGroup>
        </CardContent>
      </Card>

      {/* Payment Form */}
      {PaymentComponent && (
        <PaymentComponent
          amount={amount}
          currency={currency}
          bookingId={bookingId}
          onSuccess={onSuccess}
          onError={onError}
        />
      )}
    </div>
  );
};