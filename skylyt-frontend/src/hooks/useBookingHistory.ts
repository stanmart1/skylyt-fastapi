import { useState, useEffect } from 'react';
import { Booking } from '@/types/api';
import { apiService } from '@/services/api';
import { useToast } from '@/hooks/use-toast';

export const useBookingHistory = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const fetchBookings = async () => {
    setIsLoading(true);
    try {
      const userBookings = await apiService.getBookings();
      setBookings(userBookings);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Unable to fetch bookings.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const cancelBooking = async (bookingId: number) => {
    try {
      const cancelledBooking = await apiService.cancelBooking(bookingId);
      setBookings(prev => 
        prev.map(booking => 
          booking.id === bookingId ? cancelledBooking : booking
        )
      );
      toast({
        title: 'Booking Cancelled',
        description: 'Your booking has been cancelled successfully.',
      });
    } catch (error) {
      toast({
        title: 'Cancellation Failed',
        description: 'Unable to cancel booking. Please try again.',
        variant: 'destructive',
      });
    }
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  return {
    bookings,
    isLoading,
    fetchBookings,
    cancelBooking,
  };
};