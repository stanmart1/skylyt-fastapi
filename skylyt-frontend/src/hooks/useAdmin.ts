import { useState, useCallback } from 'react';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

export const useAdmin = () => {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const getUsers = useCallback(async () => {
    setIsLoading(true);
    try {
      const users = await apiService.getUsers();
      return users;
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Unable to fetch users.',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  const updateUserRole = useCallback(async (userId: number, roleId: number) => {
    try {
      await apiService.updateUserRole(userId, roleId);
      toast({
        title: 'Role Updated',
        description: 'User role has been updated successfully.',
      });
    } catch (error) {
      toast({
        title: 'Update Failed',
        description: 'Unable to update user role.',
        variant: 'destructive',
      });
      throw error;
    }
  }, [toast]);

  const getAllBookings = async () => {
    setIsLoading(true);
    try {
      const bookings = await apiService.getAllBookings();
      return bookings;
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Unable to fetch bookings.',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const verifyPayment = async (paymentId: number) => {
    try {
      await apiService.verifyPayment(paymentId);
      toast({
        title: 'Payment Verified',
        description: 'Payment has been verified successfully.',
      });
    } catch (error) {
      toast({
        title: 'Verification Failed',
        description: 'Unable to verify payment.',
        variant: 'destructive',
      });
      throw error;
    }
  };

  return {
    isLoading,
    getUsers,
    updateUserRole,
    getAllBookings,
    verifyPayment,
  };
};