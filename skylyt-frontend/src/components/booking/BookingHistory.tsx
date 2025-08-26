import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar, MapPin, Car, Hotel, X, Eye } from 'lucide-react';
import { useBookingHistory } from '@/hooks/useBookingHistory';
import { format } from 'date-fns';
import BookingDetailsModal from './BookingDetailsModal';

export const BookingHistory = () => {
  const { bookings, isLoading, cancelBooking } = useBookingHistory();
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  const handleViewDetails = (booking: any) => {
    setSelectedBooking(booking);
    setShowDetailsModal(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getBookingIcon = (type: string) => {
    switch (type) {
      case 'hotel': return Hotel;
      case 'car': return Car;
      default: return Calendar;
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Booking History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-20 bg-gray-200 rounded" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Booking History</CardTitle>
      </CardHeader>
      <CardContent>
        {bookings.length === 0 ? (
          <div className="text-center py-8">
            <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No bookings found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {bookings.map((booking) => {
              const Icon = getBookingIcon(booking.booking_type);
              return (
                <div key={booking.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <Icon className="h-5 w-5 text-blue-600 mt-1" />
                      <div>
                        <h3 className="font-semibold">
                          {booking.hotel_name || booking.car_name || 'Booking'}
                        </h3>
                        <p className="text-sm text-gray-600">
                          Reference: {booking.booking_reference}
                        </p>
                        <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                          {booking.check_in_date && (
                            <div className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {format(new Date(booking.check_in_date), 'MMM dd, yyyy')}
                            </div>
                          )}
                          <div className="flex items-center gap-1">
                            <span className="font-medium">${booking.total_amount}</span>
                            <span>{booking.currency}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(booking.status)}>
                        {booking.status}
                      </Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleViewDetails(booking)}
                      >
                        <Eye className="h-3 w-3 mr-1" />
                        View Details
                      </Button>
                      {booking.status === 'confirmed' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => cancelBooking(booking.id)}
                        >
                          <X className="h-3 w-3 mr-1" />
                          Cancel
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
      
      <BookingDetailsModal
        booking={selectedBooking}
        isOpen={showDetailsModal}
        onClose={() => setShowDetailsModal(false)}
      />
    </Card>
  );
};