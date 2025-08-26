import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Calendar, 
  MapPin, 
  Users, 
  Car, 
  Hotel, 
  CreditCard,
  User,
  Mail,
  Phone
} from 'lucide-react';
import { format } from 'date-fns';
import { apiService } from '@/services/api';

interface BookingDetailsModalProps {
  booking: any;
  isOpen: boolean;
  onClose: () => void;
}

const BookingDetailsModal = ({ booking, isOpen, onClose }: BookingDetailsModalProps) => {
  const [serviceDetails, setServiceDetails] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (booking && booking.booking_data?.item_id && isOpen) {
      fetchServiceDetails();
    }
  }, [booking, isOpen]);

  const fetchServiceDetails = async () => {
    if (!booking?.booking_data?.item_id) return;
    
    setLoading(true);
    try {
      let details;
      if (booking.booking_type === 'car') {
        details = await apiService.request(`/cars/${booking.booking_data.item_id}`);
      } else if (booking.booking_type === 'hotel') {
        details = await apiService.request(`/hotels/${booking.booking_data.item_id}`);
      }
      setServiceDetails(details);
    } catch (error) {
      console.error('Failed to fetch service details:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!booking) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
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

  const Icon = getBookingIcon(booking.booking_type);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Icon className="h-5 w-5" />
            Booking Details - {booking.booking_reference}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Status and Basic Info */}
          <div className="flex items-center justify-between">
            <Badge className={getStatusColor(booking.status)}>
              {booking.status.toUpperCase()}
            </Badge>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">${booking.total_amount}</div>
              <div className="text-sm text-gray-600">{booking.currency}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Booking Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Booking Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Reference:</span>
                  <span className="font-medium">{booking.booking_reference}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Type:</span>
                  <span className="font-medium capitalize">{booking.booking_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Service:</span>
                  <span className="font-medium">
                    {loading ? 'Loading...' : (serviceDetails?.name || booking.hotel_name || booking.car_name || 'N/A')}
                  </span>
                </div>
                {booking.check_in_date && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Check-in:</span>
                    <span className="font-medium">
                      {new Date(booking.check_in_date).getTime() ? 
                        format(new Date(booking.check_in_date), 'MMM dd, yyyy') : 
                        'Invalid date'
                      }
                    </span>
                  </div>
                )}
                {booking.check_out_date && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Check-out:</span>
                    <span className="font-medium">
                      {new Date(booking.check_out_date).getTime() ? 
                        format(new Date(booking.check_out_date), 'MMM dd, yyyy') : 
                        'Invalid date'
                      }
                    </span>
                  </div>
                )}
                {booking.number_of_guests && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Guests:</span>
                    <span className="font-medium">{booking.number_of_guests}</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Customer Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-4 w-4" />
                  Customer Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Name:</span>
                  <span className="font-medium">{booking.customer_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Email:</span>
                  <span className="font-medium">{booking.customer_email}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <Badge className={getStatusColor(booking.status)}>
                    {booking.status}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Payment Status:</span>
                  <Badge variant="outline">
                    {booking.payment_status || 'pending'}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Special Requests */}
          {booking.special_requests && (
            <Card>
              <CardHeader>
                <CardTitle>Special Requests</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">{booking.special_requests}</p>
              </CardContent>
            </Card>
          )}

          {/* Service Details */}
          {serviceDetails && (
            <Card>
              <CardHeader>
                <CardTitle>Service Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {booking.booking_type === 'hotel' && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Hotel:</span>
                        <span className="font-medium">{serviceDetails.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Star Rating:</span>
                        <span className="font-medium">{serviceDetails.star_rating} stars</span>
                      </div>
                      {serviceDetails.location && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Location:</span>
                          <span className="font-medium">{serviceDetails.location}</span>
                        </div>
                      )}
                      <div className="flex justify-between">
                        <span className="text-gray-600">Price per night:</span>
                        <span className="font-medium">${serviceDetails.price_per_night}</span>
                      </div>
                    </>
                  )}
                  
                  {booking.booking_type === 'car' && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Car:</span>
                        <span className="font-medium">{serviceDetails.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Category:</span>
                        <span className="font-medium">{serviceDetails.category}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Transmission:</span>
                        <span className="font-medium">{serviceDetails.transmission}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Passengers:</span>
                        <span className="font-medium">{serviceDetails.passengers}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Price per day:</span>
                        <span className="font-medium">${serviceDetails.price}</span>
                      </div>
                      {serviceDetails.fuel_type && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Fuel Type:</span>
                          <span className="font-medium">{serviceDetails.fuel_type}</span>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Booking Data Details */}
          {booking.booking_data && (
            <Card>
              <CardHeader>
                <CardTitle>Booking Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {booking.booking_data.pickup_location && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Pickup Location:</span>
                      <span className="font-medium">{booking.booking_data.pickup_location}</span>
                    </div>
                  )}
                  {booking.booking_data.dropoff_location && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Dropoff Location:</span>
                      <span className="font-medium">{booking.booking_data.dropoff_location}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Timestamps */}
          <Card>
            <CardHeader>
              <CardTitle>Timeline</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Booking Created:</span>
                <span className="font-medium">
                  {booking.created_at && new Date(booking.created_at).getTime() ? 
                    format(new Date(booking.created_at), 'MMM dd, yyyy HH:mm') : 
                    'N/A'
                  }
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Last Updated:</span>
                <span className="font-medium">
                  {booking.updated_at && new Date(booking.updated_at).getTime() ? 
                    format(new Date(booking.updated_at), 'MMM dd, yyyy HH:mm') : 
                    'N/A'
                  }
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default BookingDetailsModal;