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
import { useCurrency } from '@/contexts/CurrencyContext';
import PriceDisplay from '@/components/PriceDisplay';

interface BookingDetailsModalProps {
  booking: any;
  isOpen: boolean;
  onClose: () => void;
}

const BookingDetailsModal = ({ booking, isOpen, onClose }: BookingDetailsModalProps) => {
  const { currency } = useCurrency();
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
          <div className={`flex items-center justify-between p-4 rounded-lg border-l-4 ${
            booking.status === 'confirmed' ? 'bg-green-50 border-green-500' :
            booking.status === 'pending' ? 'bg-yellow-50 border-yellow-500' :
            booking.status === 'cancelled' ? 'bg-red-50 border-red-500' :
            'bg-gray-50 border-gray-500'
          }`}>
            <Badge className={getStatusColor(booking.status)}>
              {booking.status.toUpperCase()}
            </Badge>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">
                <PriceDisplay amount={booking.total_amount} currency={booking.currency || currency} />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Booking Information */}
            <Card className="border-l-4 border-blue-500">
              <CardHeader className="bg-blue-50">
                <CardTitle className="flex items-center gap-2 text-blue-700">
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
            <Card className="border-l-4 border-purple-500">
              <CardHeader className="bg-purple-50">
                <CardTitle className="flex items-center gap-2 text-purple-700">
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
            <Card className="border-l-4 border-orange-500">
              <CardHeader className="bg-orange-50">
                <CardTitle className="text-orange-700">Special Requests</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">{booking.special_requests}</p>
              </CardContent>
            </Card>
          )}

          {/* Service Details */}
          {serviceDetails && (
            <Card className="border-l-4 border-green-500">
              <CardHeader className="bg-green-50">
                <CardTitle className="text-green-700">Service Details</CardTitle>
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
                        <span className="font-medium">
                          <PriceDisplay amount={serviceDetails.price_per_night} currency={serviceDetails.currency || currency} />
                        </span>
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
                        <span className="font-medium">
                          <PriceDisplay amount={serviceDetails.price} currency={serviceDetails.currency || currency} />
                        </span>
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
            <Card className="border-l-4 border-indigo-500">
              <CardHeader className="bg-indigo-50">
                <CardTitle className="text-indigo-700">Booking Details</CardTitle>
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
          <Card className="border-l-4 border-gray-500">
            <CardHeader className="bg-gray-50">
              <CardTitle className="text-gray-700">Timeline</CardTitle>
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