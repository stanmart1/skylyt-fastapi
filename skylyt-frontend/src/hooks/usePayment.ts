import { useState } from 'react';
import { Payment } from '@/types/api';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

export const usePayment = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [payment, setPayment] = useState<Payment | null>(null);
  const { toast } = useToast();

  const processPayment = async (paymentData: Partial<Payment>) => {
    setIsProcessing(true);
    try {
      const result = await apiService.processPayment(paymentData);
      setPayment(result);
      
      if (result.status === 'completed') {
        toast({
          title: 'Payment Successful',
          description: 'Your payment has been processed successfully.',
        });
      } else if (result.status === 'pending') {
        toast({
          title: 'Payment Pending',
          description: 'Your payment is being processed. You will receive a confirmation shortly.',
        });
      }
      
      return result;
    } catch (error) {
      toast({
        title: 'Payment Failed',
        description: 'Unable to process payment. Please try again.',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setIsProcessing(false);
    }
  };

  const getPaymentStatus = async (paymentId: number) => {
    try {
      const result = await apiService.getPayment(paymentId);
      setPayment(result);
      return result;
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Unable to fetch payment status.',
        variant: 'destructive',
      });
      throw error;
    }
  };

  return {
    isProcessing,
    payment,
    processPayment,
    getPaymentStatus,
  };
};